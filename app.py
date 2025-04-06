import json
import os
from typing import List

from flask import (Flask, flash, jsonify, redirect, render_template, request, url_for, Response)
from werkzeug.utils import secure_filename

from src.models import *
from src.models import FieldTypes
from src.models.condition import ConditionField
from src.utils import FieldLoader
from src.utils.json_loader import check_folder, save_json

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
    if not filename.endswith('.json'):
        filename += '.json'
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
    fields = field_loader.load_fields_to_dict()
    parent = field_loader.find_field_by_path(fields, parent_path)

    def create_new_field_from_request() -> Field:
        field_type = request.form.get('type') if parent is None else parent.item_type
        """從表單請求中創建新字段"""
        return Field(
            key=request.form.get('field_name'),
            description=request.form.get('description'),
            field_type=field_type,
            item_type=request.form.get('item_type'),
            regex=None,
            required=request.form.get('required') == 'true',
            condition=None,
            children=[]
        )

    def handle_child_field(added_field: Field) -> Response:
        """處理子層級的新字段"""

        if not parent:
            flash(f'Parent field not found: {parent_path}', 'error')
            return redirect(url_for('edit_file', filename=filename))

        if field_loader.is_key_exists2(parent.children, added_field.key):
            flash(f'Field Name "{added_field.key}" is already in "{parent_path}"', 'error')
            return redirect(url_for('edit_file', filename=filename))

        parent.children.append(added_field)
        save_json(ASSETS_FOLDER, filename, fields)
        flash(f'Add new field "{added_field.key}" success in "{parent_path}".', 'success')
        return redirect(url_for('edit_file', filename=filename))

    def handle_root_field(added_field: Field):
        """處理根層級的新字段"""
        if field_loader.is_key_exists(fields, added_field.key):
            flash(f"File name '{added_field.key}' is already exist in root.", "warning")
            return redirect(url_for('edit_file', filename=filename))

        fields.append(added_field)
        save_json(ASSETS_FOLDER, filename, fields)
        flash(f'Add new field "{added_field.key}" success in root.', 'success')
        return redirect(url_for('edit_file', filename=filename))

    new_field = create_new_field_from_request()

    if parent_path == '':
        return handle_root_field(new_field)
    else:
        return handle_child_field(new_field)


@app.route('/api/delete_field/<filename>', methods=['POST'])
def delete_field(filename):
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
            parent_field[:] = [f for f in parent_field if f.key != field_name]
        else:
            parent_field.children = [f for f in parent_field.children if f.key != field_name]

        save_json(ASSETS_FOLDER, filename, data)
        return redirect(url_for('edit_file', filename=filename))
#
# @app.route('/delete_field/<filename>')
# def delete_field(filename):
#     field_path = request.args.get('field_path')
#     if not field_path:
#         flash('Field path not specified', 'error')
#         return redirect(url_for('index'))
#     try:
#         field_loader = FieldLoader(ASSETS_FOLDER, filename)
#         data = field_loader.data
#
#         # 分割路徑
#         path_parts = field_path.split('.')
#         field_name = path_parts[-1]
#         parent_path = '.'.join(path_parts[:-1])
#
#         # 找到父字段
#         if parent_path:
#             parent_field = field_loader.find_field_by_path(data, parent_path)
#             if not parent_field:
#                 if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                     return jsonify({'success': False, 'message': 'Parent field not found'})
#                 flash('Parent field not found', 'error')
#                 return redirect(url_for('edit_file', filename=filename))
#         else:
#             parent_field = data
#
#         # 刪除字段
#         if isinstance(parent_field, list):
#             parent_field[:] = [f for f in parent_field if f['key'] != field_name]
#         else:
#             parent_field['children'] = [f for f in parent_field['children'] if f['key'] != field_name]
#
#         save_json2(ASSETS_FOLDER, filename, data)
#
#
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return jsonify({'success': True})
#         flash('Field deleted successfully', 'success')
#         return redirect(url_for('edit_file', filename=filename))
#
#     except Exception as e:
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return jsonify({'success': False, 'message': str(e)})
#         flash(f'Error deleting field: {str(e)}', 'error')
#         return redirect(url_for('edit_file', filename=filename))


# ==== Field 相關 ====

@app.route('/edit/<filename>/field/<path:field_path>')
def edit_field(filename, field_path):
    field_loader = FieldLoader(ASSETS_FOLDER, filename)
    data = field_loader.load_fields_to_dict()
    target = field_loader.find_field_by_path(data, field_path)
    all_expends_field = field_loader.get_all_fields(data)
    available_fields = FieldLoader.get_available_child_fields(all_expends_field)

    return render_template('field_editor.html',
                           filename=filename,
                           field=target,
                           field_path=field_path,
                           available_fields=available_fields,
                           field_types=FieldTypes.get_all(),
                           item_types=FieldTypes.get_item_types(),
                           logic_types=LogicTypes.get_all(),
                           all_operator_types=OperationTypes.get_all(),
                           operator_types=OperationTypes.get_type_operations())


@app.route('/api/update_field/<filename>', methods=['POST'])
def update_field(filename):
    field_loader = FieldLoader(ASSETS_FOLDER, filename)
    fields = field_loader.load_fields_to_dict()

    field_path = request.form.get('field_path', '')
    field_key = request.form.get('field_key')
    description = request.form.get('description')
    field_type = request.form.get('type')
    item_type = request.form.get('item_type')
    regex = request.form.get('regex')
    required = request.form.get('required') == 'true'
    target = field_loader.find_field_by_path(fields, field_path)
    if target:
        target.update(description, field_type, item_type, regex, required)
        save_json(ASSETS_FOLDER, filename, fields)
        flash('Field updated successfully', 'success')
        return redirect(url_for('edit_field', filename=filename, field_path=field_path))

    flash('Field not found', 'danger')
    return redirect(url_for('edit_field', filename=filename, field_path=field_path))


@app.route('/save_condition/<filename>', methods=['POST'])
def save_condition(filename):
    field_path = request.form.get('field_path')
    field_loader = FieldLoader(ASSETS_FOLDER, filename)
    data = field_loader.load_fields_to_dict()

    # form 讀取
    condition_key = request.form.get('condition_key')
    condition_operator = request.form.get('condition_operator')
    condition_value = request.form.get('condition_value')

    if not all([field_path, condition_key, condition_operator, condition_value]):
        flash(f"Missing required parameters "
              f"(Field: '{condition_key}', Operator: '{condition_operator}', Value: '{condition_value}')"
              , "danger")
        return redirect(url_for('edit_field', filename=filename, field_path=field_path))

    target = field_loader.find_field_by_path(data, field_path)
    if not target:
        flash(f"Field not found (field_path: '{field_path}')", "danger")
        return redirect(url_for('edit_field', filename=filename, field_path=field_path))

    target.condition.conditions.append(ConditionField(
        condition_key,
        condition_operator,
        condition_value
    ))
    save_json(ASSETS_FOLDER, filename, data)
    flash('Field updated successfully', 'success')
    return redirect(url_for('edit_field', filename=filename, field_path=field_path))


@app.route('/delete_condition/<filename>', methods=['POST'])
def delete_condition(filename):
    field_path = request.form.get('field_path')
    field_loader = FieldLoader(ASSETS_FOLDER, filename)
    data = field_loader.load_fields_to_dict()
    condition_index = int(request.form.get('condition_index'))

    target = field_loader.find_field_by_path(data, field_path)
    if target.condition and len(target.condition.conditions) > 0:
        if 0 <= condition_index < len(target.condition.conditions):
            target.condition.conditions.pop(condition_index)
            # 如果沒有條件了，刪除整個 condition 結構
            if len(target.condition.conditions) == 0:
                target.condition = None
            save_json(ASSETS_FOLDER, filename, data)
            flash("Condition deleted successfully", "success")
        else:
            flash("Condition not found", "danger")
    return redirect(url_for('edit_field', filename=filename, field_path=field_path))


@app.route('/update_logical/<filename>', methods=['POST'])
def update_logical(filename):
    field_path = request.form.get('field_path')
    logical = request.form.get('logical')

    field_loader = FieldLoader(ASSETS_FOLDER, filename)
    data = field_loader.load_fields_to_dict()
    target = field_loader.find_field_by_path(data, field_path)

    if target is not None:
        target.condition.logical = logical
        save_json(ASSETS_FOLDER, filename, data)
        flash(f"Logical operator updated to '{logical}'", "success")
    else:
        flash(f"Failed to update condition logic, cannot find target field ({field_path})",
              "danger")
    return redirect(url_for('edit_field', filename=filename, field_path=field_path))


if __name__ == '__main__':
    check_folder(ASSETS_FOLDER)
    app.run(debug=True, port=4000)
