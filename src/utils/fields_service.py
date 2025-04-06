from typing import List

from src.models import Field, FieldTypes, Condition
from src.utils.data import FIELD_OPERATORS, OPERATOR_TYPES
from src.utils.json_loader import load_json as JsonLoader
from src.utils.json_loader import load_json_to_fields as JsonLoaderToFields


class FieldLoader:
    def __init__(self, filepath, filename):
        self.filepath = filepath
        self.filename = filename

    def load_fields(self):
        return JsonLoader(self.filepath, self.filename)

    def load_fields_to_dict(self):
        return JsonLoaderToFields(self.filepath, self.filename)

    @staticmethod
    def get_field_operators(field_type):
        """根據字段類型返回可用的運算符"""
        operators = FIELD_OPERATORS.get(field_type, [])
        return [op for op in OPERATOR_TYPES if op['value'] in operators]

    @staticmethod
    def is_key_exists2(fields: List[Field], key):
        """檢查 key 是否已存在於當前層級"""
        result = None
        for field in fields:
            if field.key == key:
                result = field

        return result is not None

    @staticmethod
    def is_key_exists(fields, key):
        """檢查 key 是否已存在於當前層級"""
        result = None
        for field in fields:
            if field.key == key:
                result = field

        return result is not None

    @staticmethod
    def find_field_by_key(data, key):
        for field in data:
            if field['key'] == key:
                return field
        return None

    @staticmethod
    def find_field_by_path2(data: List[Field], path: str) -> Field | None:
        """根據路徑查找字段"""
        if not path:
            return None

        def error(msg, field):
            raise ValueError(f"Cannot find path '{path}'：'{field}' {msg}")

        keys = path.split('.')
        current = data

        for i, key in enumerate(keys):
            is_last = (i == len(keys) - 1)

            if isinstance(current, list):
                # 如果是列表，尋找匹配 key
                current = next((f for f in current if f['key'] == key), None)
                if not current:
                    error('Not exist', key)
            else:
                if current.get('key') != key:
                    error('Not Match', key)

            if not is_last:
                # 如果不是最後一層，確認有 children
                if 'children' not in current:
                    error('No children', key)
                current = current['children']

        return current

    @staticmethod
    def find_field_by_path(data: List[Field], path) -> Field | None:
        """根據路徑查找字段"""
        def error(msg, field):
            raise ValueError(f"Cannot find path '{path}'：'{field}' {msg}")

        if not path:
            return None

        keys = path.split('.')
        current = data

        for i, key in enumerate(keys):
            is_last = (i == len(keys) - 1)

            current = next((f for f in current if f.key == key), None)
            if not current:
                error('Not exist', key)

            if not is_last:
                current = current.children

        # 初始化或更新 condition 結構
        if current.condition is None:
            current.condition = Condition(logical='and', conditions=[])

        return current

    @staticmethod
    def get_all_fields(field_list: List[Field]):
        def _collect_fields(data: List[Field], current_path='', all_fields=None):
            if all_fields is None:
                all_fields = []
            for field in data:
                field_path = current_path + field.key if current_path else field.key
                field_info = {
                    'key': field_path,
                    'type': field.field_type,
                    'item_type': field.item_type if field.field_type == FieldTypes.List else None
                }
                all_fields.append(field_info)

                if field.children and len(field.children) > 0:
                    _collect_fields(field.children, field_path + '.', all_fields)
            return all_fields

        return _collect_fields(field_list)

    @staticmethod
    def get_available_parent_fields(all_expends_fields):
        """獲取可用的父級字段"""
        available_fields = []

        # 根據類型過濾字段
        for field_info in all_expends_fields:
            if (field_info['type'] == 'object') or (field_info['type'] == 'list' and field_info['item_type'] == 'object'):
                available_fields.append({
                    'key': field_info['key'],
                    'type': field_info['type'],
                    'operators': FIELD_OPERATORS.get(field_info['type'], [])
                })
        return available_fields

    @staticmethod
    def get_available_child_fields(all_expends_fields):
        """獲取可用的子字段"""
        available_fields = []

        # 根據類型過濾字段
        for field_info in all_expends_fields:
            if field_info['type'] not in ['object', 'list']:
                available_fields.append({
                    'key': field_info['key'],
                    'type': field_info['type'],
                    'operators': FIELD_OPERATORS.get(field_info['type'], [])
                })
        return available_fields

    @staticmethod
    def get_parent_fields_for_child(field_list: List[Field], path: str = ''):
        parent_fields = []

        def collect_parent_fields(fields: List[Field], path=''):
            for field in fields:
                if field.field_type in [FieldTypes.Object, FieldTypes.List]:
                    parent_fields.append({
                        'key': path + field.key if path else field.key,
                        'type': field.field_type,
                        'item_type': field.item_type if field.field_type == FieldTypes.List else None
                    })
                if len(field.children) > 0:
                    collect_parent_fields(field.children, path + field.key + '.')

        collect_parent_fields(field_list, path)
        return parent_fields

