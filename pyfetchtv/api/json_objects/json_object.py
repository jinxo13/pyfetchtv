from abc import ABC
from enum import Enum

from pyfetchtv.api.helpers import json_utils


class JsonObject(ABC):

    @staticmethod
    def _to_dict_ignored() -> [str]:
        """
        :return: an array of property names to ignore when converting this object to a dict
        """
        return []

    def __init__(self, json: dict):
        self.__map = {}
        props = self.__get_json_properties()
        for key, val in props.items():
            result = None
            if val.name:
                result = json_utils.json_get_value(json, val.name, val.fget(self))
            elif val.path:
                result = json_utils.json_get_path_value(json, val.path, val.fget(self))
            self.__map[val.name or val.path] = result

    @staticmethod
    def __convert_list(value: list, full: bool):
        new_vals = []
        replace = False
        for v in value:
            if isinstance(v, JsonObject):
                replace = True
                if not full:
                    new_vals = len(value)
                    break
                new_vals.append(v.to_dict())
            else:
                break
        return new_vals if replace else value

    @staticmethod
    def __convert_dict(value: dict, full: bool):
        new_vals = {}
        replace = False
        for k, v in value.items():
            if isinstance(v, JsonObject):
                replace = True
                if not full:
                    new_vals = len(value)
                    break
                new_vals[k] = v.to_dict()
            else:
                break
        return new_vals if replace else value

    def to_dict(self, full=False):
        result = {}
        for key in dir(self):
            if key.startswith('_') or key in self._to_dict_ignored():
                continue
            value = getattr(self, key)
            typ = type(value)
            if isinstance(value, JsonObject):
                value = value.to_dict()
                typ = bool
            elif isinstance(value, Enum):
                value = value.name
                typ = bool
            elif isinstance(value, list):
                value = self.__convert_list(value, full)
            elif isinstance(value, dict):
                value = self.__convert_dict(value, full)
            if typ not in [bool, int, str, float, list, dict]:
                continue
            result[key] = value
        return result.copy()

    def get_value(self, name: str):
        return self.__map[name]

    def set_value(self, name, value):
        self.__map[name] = value

    @staticmethod
    def _get_json_value(json: dict, name: str, default=None):
        return json_utils.json_get_value(json, name, default)

    @staticmethod
    def _get_json_path_value(json: dict, path: str, default=None):
        return json_utils.json_get_path_value(json, path, default)

    @classmethod
    def __get_json_properties(cls):
        props = {}
        for k in dir(cls):
            attr = getattr(cls, k)
            # Check that it is a property with a getter
            if isinstance(attr, JsonProperty) and attr.fget:
                props[k] = attr
        return props


class JsonProperty(property):
    def __init__(self, fget=None, fset=None, fdel=None, doc=None, name='', path=''):
        super().__init__(fget, fset, fdel, doc)
        self.name = name
        self.path = path

    def __get__(self, obj: JsonObject, objtype=None):
        if obj is None:
            return self
        return obj.get_value(self.name or self.path)


def json_property(name='', path=''):
    class DummyProperty(JsonProperty):
        def __init__(self, fget=None, fset=None, fdel=None, doc=None):
            super().__init__(fget, fset, fdel, doc, name, path)
    return DummyProperty
