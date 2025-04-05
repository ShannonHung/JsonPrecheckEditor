from src.models import FieldTypes, LogicTypes, OperationTypes

# 定義可用的類型選項
FIELD_TYPES = FieldTypes.get_all()

# 定義可用的項目類型選項（用於 list 的 item_type）
ITEM_TYPES = FieldTypes.get_item_types()

# 定義邏輯運算符類型
LOGIC_TYPES = LogicTypes.get_all()

# 定義條件運算符類型
OPERATOR_TYPES = OperationTypes.get_all()

# 定義每個字段類型對應的運算符
FIELD_OPERATORS = {
    'bool': ['eq', 'ne'],
    'string': ['eq', 'ne', 'not_empty', 'empty'],
    'number': ['eq', 'ne', 'gt', 'lt'],
    'email': ['eq', 'ne', 'gt', 'lt'],
    'ip': ['eq', 'ne', 'gt', 'lt'],
}