class LogicTypes:
    AND = 'and'
    OR = 'or'

    _TYPES = [
        {'value': AND, 'label': 'AND'},
        {'value': OR, 'label': 'OR'}
    ]

    @classmethod
    def get_all(cls):
        """回傳所有欄位型別"""
        return cls._TYPES

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