from typing import Dict, List

from pyfetchtv.api.json_objects.json_object import JsonObject, json_property
from pyfetchtv.api.json_objects.series import Series


class Recording(JsonObject):

    def __init__(self, box, json: dict):
        super().__init__(json)
        self.__terminal_id = box.terminal_id
        self.__dlna_url = box.dlna_url

    @property
    def terminal_id(self) -> str:
        return self.__terminal_id

    @property
    def dlna_url(self) -> str:
        return self.__dlna_url + str(self.id)

    @json_property(name='diskId')
    def disk_id(self) -> int:
        return 0

    @json_property(name='id')
    def id(self) -> int:
        return 0

    @json_property(name='name')
    def name(self):
        return ''

    @json_property(name='channelId')
    def channel_id(self) -> str:
        return ''

    @json_property(name='programId')
    def program_id(self) -> int:
        return 0

    @json_property(name='description')
    def description(self) -> str:
        return ''

    @json_property(name='episodeTitle')
    def episode_title(self) -> str:
        return ''

    @json_property(name='seriesNumber')
    def season(self) -> str:
        return ''

    @json_property(name='episodeNumber')
    def episode(self) -> str:
        return ''

    @json_property(name='programStartDate')
    def program_start(self) -> int:
        return 0

    @json_property(name='programEndDate')
    def program_end(self) -> int:
        return 0

    @json_property(name='startDate')
    def record_start(self) -> int:
        return 0

    @json_property(name='endDate')
    def record_end(self) -> int:
        return 0

    @json_property(name='creationDate')
    def created(self) -> int:
        return 0

    @json_property(name='seriesLinkId')
    def series_id(self) -> str:
        return ''

    @json_property(name='episodeId')
    def episode_id(self) -> int:
        return 0

    @json_property(name='currentPosition')
    def current_position(self) -> int:
        return 0

    @json_property(name='viewCount')
    def view_count(self) -> int:
        return 0

    @json_property(name='lastViewed')
    def last_viewed(self) -> int:
        return 0

    @json_property(name='size')
    def size(self) -> int:
        return 0

    @json_property(name='pendingDelete')
    def pending_delete(self) -> bool:
        return False

    def delete(self):
        self.set_value('pendingDelete', True)


class Recordings(JsonObject):

    def __init__(self, box, json: dict):
        super().__init__(json)
        self.__box = box
        self.__series = [Series(item) for item in self._get_json_value(json, 'seriesTagList', [])]
        self.__future = []
        self.set_future(json, 'currentFutureRecordings')
        self.__items = {itm['id']: Recording(self.__box, itm) for itm in self._get_json_value(json, 'recordings', [])}

    def set_future(self, json, tag):
        self.__future = [Recording(self.__box, item) for item in self._get_json_value(json, tag, [])]

    @property
    def series(self) -> List[Series]:
        return self.__series

    @property
    def future(self) -> List[Recording]:
        return self.__future

    @property
    def items(self) -> Dict[int, Recording]:
        return self.__items

    @property
    def pending_delete(self) -> int:
        return len([item for item in self.__items.values() if item.pending_delete])
