from typing import List

from pyfetchtv.api.const.urls import URL_BASE_STATIC
from pyfetchtv.api.json_objects.json_object import JsonObject, json_property


class EpgChannel(JsonObject):

    @json_property(name='epg_id')
    def id(self) -> int:
        return 0

    @json_property(name='regions')
    def regions(self) -> List[int]:
        return []

    @json_property(name='name')
    def name(self) -> str:
        return ''

    @json_property(name='description')
    def description(self) -> str:
        return ''

    @json_property(name='flags')
    def __flags(self) -> int:
        return 0

    @property
    def type(self) -> str:
        return 'radio' if self.__flags == 4 else 'tv'

    @json_property(name='image')
    def __image_url(self) -> str:
        return ''

    @property
    def image_url(self) -> str:
        return URL_BASE_STATIC + self.__image_url

    @json_property(name='high_definition')
    def __high_definition(self) -> bool:
        return False

    @property
    def high_definition(self) -> bool:
        return self.__high_definition or "HD" in self.name
