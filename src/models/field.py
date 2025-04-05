from src.models.condition import Condition


class Field:
    """表示字段的类"""

    def __init__(self, key, description, field_type, item_type=None, regex=None, required=False, condition=None,
                 children=None):
        self.key = key
        self.description = description
        self.field_type = field_type
        self.item_type = item_type
        self.regex = regex
        self.required = required
        self.condition = condition if isinstance(condition, Condition) else None
        self.children = children or []

    def __repr__(self):
        return (f"Field(key={self.key}, description={self.description}, "
                f"type={self.field_type}, item_type={self.item_type}, regex={self.regex}, "
                f"required={self.required}, condition={self.condition}, children={self.children})")

    def is_required(self):
        """返回字段是否是必填字段"""
        return self.required

    def get_condition(self):
        """返回字段的条件"""
        return self.condition

    def add_child(self, child_field):
        """添加子字段"""
        self.children.append(child_field)

    def get_children(self):
        """获取子字段"""
        return self.children

    def update(self, description, field_type=None, item_type=None, regex=None, required=False):
        self.description = description
        if field_type:
            self.field_type = field_type
        if item_type:
            self.item_type = item_type
        self.regex = regex
        self.required = required

        if self.required:
            self.condition = None
        return self

    @classmethod
    def from_dict(cls, data):
        """从字典创建一个 Field 实例"""
        condition = None
        if 'condition' in data and data['condition']:
            condition = Condition(
                logical=data['condition'].get('logical'),
                conditions=data['condition'].get('conditions')
            )

        children = []
        if 'children' in data:
            children = [cls.from_dict(child) for child in data['children']]

        return cls(
            key=data['key'],
            description=data.get('description', ''),
            field_type=data['type'],
            item_type=data.get('item_type'),
            regex=data.get('regex'),
            required=data.get('required', False),
            condition=condition,
            children=children
        )