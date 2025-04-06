from src.models.type import OperationTypes
from typing import List

class Condition:
    """表示字段的条件"""
    def __init__(self, logical=None, conditions: List['ConditionField'] = None):
        if conditions is None:
            conditions = []  # Default to an empty list if None is provided
        self.logical = logical
        self.conditions = conditions

    def __repr__(self):
        return f"Condition(logical={self.logical}, conditions={self.conditions})"


class ConditionField:
    def __init__(self,
                 key: str,
                 operator: str,
                 value: str):
        self.key = key
        self.operator = operator
        self.value = value
