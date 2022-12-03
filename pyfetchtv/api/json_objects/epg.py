from typing import Dict

from pyfetchtv.api.json_objects.json_object import JsonObject


class Program(JsonObject):

    def __init__(self, json, synopses: Dict[str, str]):
        super().__init__(json)
        self.__values = json
        self.__synopsis = synopses[str(self.synopsis_id)] if str(self.synopsis_id) in synopses else ''

    def __hash__(self):
        return hash(self.title + self.episode_title + self.series_no + self.episode_no)

    def __eq__(self, other):
        return isinstance(other, Program) and hash(other) == hash(self)

    @property
    def synopsis(self):
        return self.__synopsis

    @property
    def program_id(self) -> str:
        return self.__values[0]

    @property
    def title(self) -> str:
        return self.__values[1]

    @property
    def start(self) -> int:
        return self.__values[2]

    @property
    def end(self) -> int:
        return self.__values[3]

    @property
    def synopsis_id(self) -> int:
        return self.__values[4]

    @property
    def rating(self) -> int:
        return self.__values[5]

    @property
    def warnings(self) -> str:
        return self.__values[6]

    @property
    def flags(self) -> int:
        return self.__values[7]

    @property
    def genre(self) -> str:
        return self.__values[8]

    @property
    def series_link(self) -> str:
        return self.__values[9]

    @property
    def episode_title(self) -> str:
        return self.__values[10]

    @property
    def series_no(self) -> str:
        return self.__values[11]

    @property
    def episode_no(self) -> str:
        return self.__values[12]

    @property
    def series_id(self) -> str:
        return self.__values[13]

    @property
    def epg_program_id(self) -> str:
        return self.__values[14]
