

class FileName:
    TEST = "test"
    FIELD = "fields"

    @classmethod
    def get_all_files(cls):
        return [value for name, value in cls.__dict__.items() if isinstance(value, str) and "const" not in value]


class Value:
    def __init__(self, file_name: str):
        self.file_name = f"{file_name}.json"
        self.folder_path = "assets"
        self.json_path = f"{self.folder_path}/{file_name}.json"
