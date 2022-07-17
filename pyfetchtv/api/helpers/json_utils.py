from typing import Any

from jsonpath_ng import parse


def json_get_value(json: dict, name: str, default=None) -> Any:
    return json[name] if name in json.keys() else default


def json_has_value(json: dict, name: str) -> bool:
    return name in json.keys()


def json_get_path_value(json: dict, path: str, default=None) -> Any:
    json_exp = parse(path)
    result = json_exp.find(json)
    for match in result:
        return match.value
    return default
