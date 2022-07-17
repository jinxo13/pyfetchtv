from pyfetchtv.api.json_objects.json_object import JsonObject


class EpgRegion(JsonObject):

    def __init__(self, json, region_id: str):
        super().__init__(json)
        self.__values = json
        self.__id = region_id

    @property
    def id(self) -> str:
        return self.__id

    @property
    def state(self) -> str:
        return self.__values[0]

    @property
    def location(self) -> str:
        return self.__values[1]
