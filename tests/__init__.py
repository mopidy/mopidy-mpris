class DictFields:
    """Asserts all required key-value pairs of the dict match.

    assert DictFields({"a": 1}) == {"a": 1, "b": 5}
    assert DictFields({"a": 1}) != {"a": 2}
    """

    def __init__(self, required: dict):
        self.required = required

    def __eq__(self, other: dict) -> bool:
        return {**other, **self.required} == other

    def __repr__(self) -> str:
        return f"DictFields({self.required.__repr__()})"
