import json
from typing import LiteralString

from src.models.field import Field
from src.models.condition import Condition


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        field = None

        if isinstance(obj, Field):
            field = {
                "key": obj.key,
                "description": obj.description,
                "type": obj.field_type,
                "item_type": obj.item_type,
                "regex": obj.regex,
                "required": obj.required,
                "condition": obj.condition,
                "children": obj.children
            }

        elif isinstance(obj, Condition):
            field = {
                "logical": obj.logical,
                "conditions": obj.conditions
            }

        return field


class ObjectToJsonFile:
    @staticmethod
    def to_json(file_name: str | LiteralString, obj: object) -> None:
        with open(file_name, "w") as file:
            json.dump(obj, file, cls=CustomEncoder, indent=4)
