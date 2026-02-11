"""Lightweight local fallback for pydantic APIs used in this project."""

from __future__ import annotations

from copy import deepcopy


class _FieldDefault:
    def __init__(self, default=None, default_factory=None):
        self.default = default
        self.default_factory = default_factory


def Field(default=None, default_factory=None):
    return _FieldDefault(default=default, default_factory=default_factory)


class BaseModel:
    def __init__(self, **kwargs):
        annotations = getattr(self, "__annotations__", {})
        for key in annotations:
            class_default = getattr(self.__class__, key, None)
            if isinstance(class_default, _FieldDefault):
                if class_default.default_factory is not None:
                    value = class_default.default_factory()
                else:
                    value = deepcopy(class_default.default)
            elif key in self.__class__.__dict__:
                value = deepcopy(class_default)
            else:
                value = None

            if key in kwargs:
                value = kwargs[key]

            nested_type = annotations[key]
            if (
                isinstance(value, dict)
                and isinstance(nested_type, type)
                and issubclass(nested_type, BaseModel)
            ):
                value = nested_type(**value)
            if isinstance(value, list):
                origin = getattr(nested_type, "__origin__", None)
                args = getattr(nested_type, "__args__", ())
                if (
                    origin is list
                    and args
                    and isinstance(args[0], type)
                    and issubclass(args[0], BaseModel)
                ):
                    value = [args[0](**v) if isinstance(v, dict) else v for v in value]
            setattr(self, key, value)

    @classmethod
    def model_validate(cls, data):
        return cls(**data)
