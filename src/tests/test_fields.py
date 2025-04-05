import pytest
from src.utils import *
from src.models import Field, ObjectToJsonFile
from src.tests.const import FileName as f
from src.tests.const import Value


class TestFieldService:
    ASSETS_PATH = "assets/"

    @pytest.mark.parametrize(
        "file_name, all_fields_len, available_parent_fields_len",
        [
            (f.TEST, 8, 3)
        ]
    )
    def test_fields(self, file_name, all_fields_len, available_parent_fields_len):
        v = Value(file_name)
        field_loader = FieldLoader(filepath=v.folder_path, filename=v.file_name)
        all_fields = field_loader.get_all_fields(field_loader.load_fields_to_dict())
        available_parent_fields = field_loader.get_available_parent_fields(all_fields)

        assert len(all_fields) == all_fields_len
        assert len(available_parent_fields) == available_parent_fields_len

    @pytest.mark.parametrize(
        "file_name",
        [
            f.FIELD
        ]
    )
    def test_model(self, file_name):
        v = Value(file_name)
        field_loader = FieldLoader(filepath=v.folder_path, filename=v.file_name)

        data = field_loader.data
        fields = [Field.from_dict(item) for item in data]

        for field in fields:
            assert isinstance(field, Field)
            assert field.key is not None
            assert len(field.children) >= 0
            assert len(field.condition.conditions) >= 0

    @pytest.mark.parametrize(
        "file_name",
        [
            f.FIELD
        ]
    )
    def test_model_to_json(self, file_name):
        v = Value(file_name)
        field_loader = FieldLoader(filepath=v.folder_path, filename=v.file_name)

        data = field_loader.data
        fields = [Field.from_dict(item) for item in data]

        ObjectToJsonFile.to_json(f"{v.folder_path}/output.json", fields)
        with open(f"{v.folder_path}/output.json", "r") as file:
            loaded_data = file.read()
            assert loaded_data is not None
