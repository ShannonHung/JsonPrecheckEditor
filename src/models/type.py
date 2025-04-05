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


class OperationTypes:
    # 定義所有運算符
    EQ = {'value': 'eq', 'label': '=='}
    NE = {'value': 'ne', 'label': '!='}
    GT = {'value': 'gt', 'label': '>'}
    LT = {'value': 'lt', 'label': '<'}
    NOT_EMPTY = {'value': 'not_empty', 'label': 'Not None'}
    EMPTY = {'value': 'empty', 'label': 'Is None'}

    # 定義運算符與 FieldType 的映射
    _TYPE_OPERATORS = {
        FieldTypes.Bool: [EQ, NE],
        FieldTypes.String: [EQ, NE, NOT_EMPTY, EMPTY],
        FieldTypes.Number: [EQ, NE, GT, LT],
        FieldTypes.Email: [EQ, NE, GT, LT],
        FieldTypes.IP: [EQ, NE, GT, LT],
    }

    @classmethod
    def get_operators_by_field_type(cls, field_type):
        """ 根據欄位類型返回對應的運算符列表 """
        return cls._TYPE_OPERATORS.get(field_type, [])

    @classmethod
    def get_type_operations(cls):
        """ 返回所有運算符與其對應的欄位類型 """
        return cls._TYPE_OPERATORS

    @classmethod
    def get_all(cls):
        return [cls.EQ, cls.NE, cls.GT, cls.LT, cls.NOT_EMPTY, cls.EMPTY]

    @classmethod
    def get(cls, condition_operator):
        """ 根據運算符值返回對應的運算符 """
        for operator in cls.get_all():
            if operator['value'] == condition_operator:
                return operator
        return None
