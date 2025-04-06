import json
import os
from typing import List

from src.models import Field, CustomEncoder


def load_json(filepath, filename):
    filepath = os.path.join(filepath, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []


def load_json_to_fields(filepath, filename) -> List[Field]:
    filepath = os.path.join(filepath, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
            fields = [Field.from_dict(item) for item in data]
            return fields
    return []


def save_json(folder_path, filename, data):
    filepath = os.path.join(folder_path, filename)
    with open(filepath, "w") as file:
        json.dump(data, file, cls=CustomEncoder, indent=4)


def check_folder(folder_path):
    # 確保 assets 目錄存在
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
