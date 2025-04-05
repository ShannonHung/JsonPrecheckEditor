from src.models.operation import OperationTypes


class FieldTypes:
    String = 'string'
    Number = 'number'
    List = 'list'
    Email = 'email'
    Bool = 'bool'
    IP = 'ip'
    Object = 'object'

    _TYPES = [
        {'value': String, 'label': 'String'},
        {'value': Number, 'label': 'Number'},
        {'value': List, 'label': 'List'},
        {'value': Email, 'label': 'Email'},
        {'value': Bool, 'label': 'Boolean'},
        {'value': IP, 'label': 'IP'},
        {'value': Object, 'label': 'Object'}
    ]

    @classmethod
    def get_all(cls):
        """回傳所有欄位型別"""
        return cls._TYPES

    @classmethod
    def get_item_types(cls):
        """回傳適用於 list items 的型別（排除 list 和 bool）"""
        return [t for t in cls._TYPES if t['value'] != cls.List and t['value'] != cls.Bool]

    @classmethod
    def get_label(cls, value):
        """根據 value 回傳對應的 label"""
        for t in cls._TYPES:
            if t['value'] == value:
                return t['label']
        return None

    @classmethod
    def is_valid(cls, value):
        """檢查 value 是否是合法的欄位型別"""
        return any(t['value'] == value for t in cls._TYPES)

    @classmethod
    def get_operators(cls, field_type):
        """根據欄位類型取得對應的運算符（由 OperationTypes 提供）"""
        # 直接透過 OperationTypes 取得對應 FieldType 的運算符
        operators = OperationTypes.get_operators_by_field_type(field_type)
        return operators
