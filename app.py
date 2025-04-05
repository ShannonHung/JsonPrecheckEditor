from typing import List

from flask import (Flask, flash, jsonify, redirect, render_template, request, url_for, Response)
from werkzeug.utils import secure_filename
import os
import json

from src.models import *
from src.utils import FieldLoader, OPERATOR_TYPES, json_loader
from src.models import FieldTypes
from src.utils.json_loader import check_folder, save_json, save_json2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'assets'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'your-secret-key-here'  # 用於 flash 訊息

ASSETS_FOLDER = app.config['UPLOAD_FOLDER']


# @app.errorhandler(Exception)
# def handle_exception(e):
#     # pass through HTTP errors
#     flash(f'Error occurred: {str(e)}', 'danger')
#     return redirect(url_for('error'))


@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/')
def index():
    files = [f for f in os.listdir(ASSETS_FOLDER) if f.endswith('.json')]
    return render_template('index.html', files=files)


# ==== File 相關 ====
@app.route('/create', methods=['POST'])
def create_file():
    filename = secure_filename(request.form.get('filename'))
    filepath = os.path.join(ASSETS_FOLDER, filename)

    # 檢查檔案是否已存在
    if os.path.exists(filepath):
        flash(f"File '{filename}' is already exist.", "warning")
        return redirect(url_for('index'))
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        flash(f"Create file '{filename}' success", "success")

    return redirect(url_for('index'))


@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filepath = os.path.join(ASSETS_FOLDER, filename)
    # 檢查檔案是否存在
    if not os.path.exists(filepath):
        flash('File does not exist', 'danger')
        return redirect(url_for('index'))
    else:
        os.remove(filepath)
        flash(f"File '{filename}' deleted successfully", 'success')
        return redirect(url_for('index'))


# ==== File 裡面的 Fields 相關 ====
@app.route('/edit/<filename>')
def edit_file(filename):
    field_loader = FieldLoader(ASSETS_FOLDER, filename)
    fields = field_loader.load_fields_to_dict()
    return render_template('editor.html',
                           filename=filename,
                           data=fields,
                           field_types=FieldTypes.get_all(),
                           item_types=FieldTypes.get_item_types(),
                           parent_fields=field_loader.get_parent_fields_for_child(fields))


@app.route('/api/add_field/<filename>', methods=['POST'])
def add_field(filename):
    field_loader = FieldLoader(ASSETS_FOLDER, filename)
    parent_path = request.form.get('field_path', '')

    def create_new_field_from_request() -> Field:
        """從表單請求中創建新字段"""
        return Field(
            key=request.form.get('field_name'),
            description=request.form.get('description'),
            field_type=request.form.get('type'),
            item_type=request.form.get('item_type'),
            regex=None,
            required=request.form.get('required') == 'true',
            condition=None,
            children=[]
        )

    def handle_child_field(fields: List[Field], added_field: Field) -> Response:
        """處理子層級的新字段"""
        parent = field_loader.find_field_by_path2(fields, parent_path)
        if not parent:
            flash(f'Parent field not found: {parent_path}', 'error')
            return redirect(url_for('edit_file', filename=filename))

        if field_loader.is_key_exists2(parent.children, added_field.key):
            flash(f'Field Name "{added_field.key}" is already in "{parent_path}"', 'error')
            return redirect(url_for('edit_file', filename=filename))

        parent.children.append(added_field)
        save_json2(ASSETS_FOLDER, filename, fields)
        flash(f'Add new field "{added_field.key}" success in "{parent_path}".', 'success')
        return redirect(url_for('edit_file', filename=filename))

    def handle_root_field(fields: List[Field], added_field: Field):
        """處理根層級的新字段"""
        if field_loader.is_key_exists(fields, added_field.key):
            flash(f"File name '{added_field.key}' is already exist in root.", "warning")
            return redirect(url_for('edit_file', filename=filename))

        fields.append(added_field)
        save_json2(ASSETS_FOLDER, filename, fields)
        flash(f'Add new field "{added_field.key}" success in root.', 'success')
        return redirect(url_for('edit_file', filename=filename))

    data = field_loader.load_fields_to_dict()
    new_field = create_new_field_from_request()

    if parent_path == '':
        return handle_root_field(data, new_field)
    else:
        return handle_child_field(data, new_field)

@app.route('/api/delete_field/<filename>', methods=['POST'])
def test(filename):
    field_path = request.form.get('field_path')
    if not field_path:
        flash('Field path not specified', 'danger')
        return redirect(url_for('index'))
    else:
        field_loader = FieldLoader(ASSETS_FOLDER, filename)
        data: List[Field] = field_loader.load_fields_to_dict()
        # 分割路徑
        path_parts = field_path.split('.')
        field_name = path_parts[-1]
        parent_path = '.'.join(path_parts[:-1])

        # 找到父字段
        if parent_path:
            parent_field = field_loader.find_field_by_path(data, parent_path)
        else:
            parent_field = data

        # 刪除字段
        if isinstance(parent_field, list):
            parent_field[:] = [f for f in parent_field if f['key'] != field_name]
        else:
            parent_field.children = [f for f in parent_field.children if f.key != field_name]

        save_json2(ASSETS_FOLDER, filename, data)
        return redirect(url_for('edit_file', filename=filename))

@app.route('/delete_field/<filename>')
def delete_field(filename):
    field_path = request.args.get('field_path')
    if not field_path:
        flash('Field path not specified', 'error')
        return redirect(url_for('index'))
    try:
        field_loader = FieldLoader(ASSETS_FOLDER, filename)
        data = field_loader.data

        # 分割路徑
        path_parts = field_path.split('.')
        field_name = path_parts[-1]
        parent_path = '.'.join(path_parts[:-1])

        # 找到父字段
        if parent_path:
            parent_field = field_loader.find_field_by_path(data, parent_path)
            if not parent_field:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'Parent field not found'})
                flash('Parent field not found', 'error')
                return redirect(url_for('edit_file', filename=filename))
        else:
            parent_field = data

        # 刪除字段
        if isinstance(parent_field, list):
            parent_field[:] = [f for f in parent_field if f['key'] != field_name]
        else:
            parent_field['children'] = [f for f in parent_field['children'] if f['key'] != field_name]

        save_json2(ASSETS_FOLDER, filename, data)


        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        flash('Field deleted successfully', 'success')
        return redirect(url_for('edit_file', filename=filename))

    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)})
        flash(f'Error deleting field: {str(e)}', 'error')
        return redirect(url_for('edit_file', filename=filename))


# ==== Field 相關 ====

@app.route('/edit/<filename>/field/<path:field_path>')
def edit_field(filename, field_path):
    field_loader = FieldLoader(ASSETS_FOLDER, filename)
    data = field_loader.load_fields_to_dict()
    target = field_loader.find_field_by_path(data, field_path)
    all_expends_field = field_loader.get_all_fields(data)
    available_fields = FieldLoader.get_available_parent_fields(all_expends_field)

    return render_template('field_editor.html',
                           filename=filename,
                           field=target,
                           field_path=field_path,
                           available_fields=available_fields,
                           field_types=FieldTypes.get_all(),
                           item_types=FieldTypes.get_item_types(),
                           logic_types=LogicTypes.get_all(),
                           operator_types=OperationTypes.get_all())


@app.route('/api/update_field/<filename>', methods=['POST'])
def update_field(filename):
    field_loader = FieldLoader(ASSETS_FOLDER, filename)
    data = field_loader.load_fields_to_dict()
    field_path = request.form.get('field_path', '')
    new_key = request.form.get('key')
    description = request.form.get('description')
    field_type = request.form.get('type')
    item_type = request.form.get('item_type')
    regex = request.form.get('regex')
    required = request.form.get('required') == 'true'

    # Find the field based on the provided field_path
    field = field_loader.find_field_by_path(data, field_path)
    if field:
        # 检查新 key 是否已存在
        parent_path = '.'.join(field_path.split('.')[:-1])
        parent = field_loader.find_field_by_path(data, parent_path) if parent_path else data

        # Handling case where parent is either a list or a single field (Field)
        if isinstance(parent, list):
            # Parent is a list of fields, check for duplicate key in the list
            for existing_field in parent:
                if existing_field.key == new_key:
                    field = existing_field

        # Update the field attributes
        field.key = new_key
        field.description = description
        if field_type:
            field.field_type = field_type
        if item_type:
            field.item_type = item_type
        field.regex = regex
        field.required = required

        # Reset condition if field is required
        if field.required:
            field.condition = None

        # Save the updated data
        save_json2(ASSETS_FOLDER, filename, data)
        flash('Field updated successfully', 'success')
    else:
        flash('Field not found', 'danger')

    return redirect(url_for('edit_field', filename=filename, field_path=field_path))

# @app.route('/api/update_field/<filename>', methods=['POST'])
# def update_field(filename):
#     try:
#         field_loader = FieldLoader(ASSETS_FOLDER, filename)
#         data = field_loader.data
#         field_path = request.form.get('field_path', '')
#         new_key = request.form.get('key')
#         description = request.form.get('description')
#         field_type = request.form.get('type')
#         item_type = request.form.get('item_type')
#         regex = request.form.get('regex')
#         required = request.form.get('required') == 'true'
#
#         field = field_loader.find_field_by_path(data, field_path)
#         if field:
#             # 檢查新 key 是否已存在
#             parent_path = '.'.join(field_path.split('.')[:-1])
#             parent = field_loader.find_field_by_path(data, parent_path) if parent_path else data
#             if isinstance(parent, list):
#                 for existing_field in parent:
#                     if existing_field['key'] == new_key and existing_field != field:
#                         flash(f'Field name "{new_key}" already exists in current level', 'error')
#                         return redirect(url_for('edit_field', filename=filename, field_path=field_path))
#             else:
#                 if parent['key'] == new_key and parent != field:
#                     flash(f'Field name "{new_key}" already exists in current level', 'error')
#                     return redirect(url_for('edit_field', filename=filename, field_path=field_path))
#
#             # 更新字段
#             field['key'] = new_key
#             field['description'] = description
#             if field_type:
#                 field['type'] = field_type
#             if item_type:
#                 field['item_type'] = item_type
#             field['regex'] = regex
#             field['required'] = required
#
#             if field['required']:
#                 field['condition'] = None
#
#             save_json(filename, data)
#             flash('Field updated successfully', 'success')
#         else:
#             flash('Field not found', 'danger')
#     except ValueError as e:
#         flash(str(e), 'error')
#     except Exception as e:
#         flash(f'Error updating field: {str(e)}', 'danger')
#
#     return redirect(url_for('edit_field', filename=filename, field_path=field_path))


@app.route('/save_condition/<filename>', methods=['POST'])
def save_condition(filename):
    try:
        # 讀取 JSON 檔案
        filepath = os.path.join(ASSETS_FOLDER, filename)
        field_path = request.form.get('field_path')

        if not os.path.exists(filepath):
            flash(f"File not found: {filename}", "danger")
            return redirect(url_for('edit_field', filename=filename, field_path=field_path))

        field_loader = FieldLoader(ASSETS_FOLDER, filename)
        data = field_loader.data

        if not isinstance(data, list):
            flash("JSON file format error: root element must be an array", "danger")
            return redirect(url_for('edit_field', filename=filename, field_path=field_path))

        condition_key = request.form.get('condition_key')
        condition_operator = request.form.get('condition_operator')
        condition_value = request.form.get('condition_value')

        if not all([field_path, condition_key, condition_operator, condition_value]):
            flash("Missing required parameters", "danger")
            return redirect(url_for('edit_field', filename=filename, field_path=field_path))

        field = field_loader.find_field_by_path(data, field_path)
        if not field:
            flash("Field not found", "danger")
            return redirect(url_for('edit_field', filename=filename, field_path=field_path))

        # 初始化或更新 condition 結構
        if 'condition' not in field or field['condition'] is None:
            field['condition'] = {
                'logical': 'and',  # 預設邏輯運算符
                'conditions': []
            }

        # 添加新條件
        field['condition']['conditions'].append({
            'key': condition_key,
            'operator': condition_operator,
            'value': condition_value
        })

        # 保存更新後的 JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        flash("Condition saved successfully", "success")
    except Exception as e:
        flash(f'Error saving condition: {str(e)}', "danger")

    return redirect(url_for('edit_field', filename=filename, field_path=field_path))


@app.route('/delete_condition/<filename>', methods=['POST'])
def delete_condition(filename):
    try:
        # 讀取 JSON 檔案
        filepath = os.path.join(ASSETS_FOLDER, filename)
        field_path = request.form.get('field_path')

        if not os.path.exists(filepath):
            flash(f"File not found: {filename}", "danger")
            return redirect(url_for('edit_field', filename=filename, field_path=field_path))

        field_loader = FieldLoader(ASSETS_FOLDER, filename)
        data = field_loader.data

        if not isinstance(data, list):
            flash("JSON file format error: root element must be an array", "danger")
            return redirect(url_for('edit_field', filename=filename, field_path=field_path))

        field_path = request.form.get('field_path')
        condition_index = int(request.form.get('condition_index'))

        if not field_path:
            flash("Missing required parameters", "danger")
            return redirect(url_for('edit_field', filename=filename, field_path=field_path))

        field = field_loader.find_field_by_path(data, field_path)
        if not field:
            flash("Field not found", "danger")
            return redirect(url_for('edit_field', filename=filename, field_path=field_path))

        # 檢查並刪除條件
        if 'condition' in field and 'conditions' in field['condition']:
            if 0 <= condition_index < len(field['condition']['conditions']):
                field['condition']['conditions'].pop(condition_index)

                # 如果沒有條件了，刪除整個 condition 結構
                if not field['condition']['conditions']:
                    del field['condition']

                # 保存更新後的 JSON
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                flash("Condition deleted successfully", "success")
            else:
                flash("Condition not found", "danger")
        else:
            flash("No conditions found for this field", "danger")

    except Exception as e:
        flash(f'Error deleting condition: {str(e)}', "danger")

    return redirect(url_for('edit_field', filename=filename, field_path=field_path))


@app.route('/update_logical/<filename>', methods=['POST'])
def update_logical(filename):
    try:
        field_path = request.form.get('field_path')
        logical = request.form.get('logical')

        if not field_path or not logical:
            flash(f"Field({field_path}) or logical({logical}) is empty. ")
            return redirect(url_for('edit_field', filename=filename, field_path=field_path))

        # 讀取並更新 JSON
        filepath = os.path.join(ASSETS_FOLDER, filename)
        field_loader = FieldLoader(ASSETS_FOLDER, filename)
        data = field_loader.data

        field = field_loader.find_field_by_path(data, field_path)
        if not field:
            flash("Field not found", "danger")
            return redirect(url_for('edit_field', filename=filename, field_path=field_path))

        # 更新邏輯運算符
        if 'condition' not in field or field['condition'] is None:
            field['condition'] = {'logical': "and", 'conditions': []}
        field['condition']['logical'] = logical

        # 保存更新
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        flash(f"Logical operator updated to '{logical}'", "success")
    except Exception as e:
        flash(f'Update failed: {str(e)}', "danger")

    return redirect(url_for('edit_field', filename=filename, field_path=field_path))


if __name__ == '__main__':
    check_folder(ASSETS_FOLDER)
    app.run(debug=True, port=4000)
