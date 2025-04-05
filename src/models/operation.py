
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
        'bool': [EQ, NE],
        'string': [EQ, NE, NOT_EMPTY, EMPTY],
        'number': [EQ, NE, GT, LT],
        'email': [EQ, NE, GT, LT],
        'ip': [EQ, NE, GT, LT],
    }

    @classmethod
    def get_operators_by_field_type(cls, field_type):
        """ 根據欄位類型返回對應的運算符列表 """
        return cls._TYPE_OPERATORS.get(field_type, [])

    @classmethod
    def get_all(cls):
        return [cls.EQ, cls.NE, cls.GT, cls.LT, cls.NOT_EMPTY, cls.EMPTY]
