from abc import ABC, abstractmethod
from typing import Optional, List

from pyfetchtv.api.const.remote_keys import RemoteKey
from pyfetchtv.api.json_objects.epg import Program
from pyfetchtv.api.json_objects.set_top_box import SetTopBox


class FetchTvBoxInterface(SetTopBox, ABC):

    @abstractmethod
    def ping(self):
        pass

    @abstractmethod
    def is_alive(self):
        pass

    @abstractmethod
    def process_message(self, message: dict):
        pass

    @abstractmethod
    def update_media_state(self):
        pass

    @abstractmethod
    def play_channel(self, channel_id: str):
        pass

    @abstractmethod
    def record_channel(self, channel_id: str):
        pass

    @abstractmethod
    def record_program(self, channel_id: str, program_id: str, epg_program_id: str, protect_item: bool = False):
        pass

    @abstractmethod
    def get_current_program(self) -> Optional[Program]:
        pass

    @abstractmethod
    def record_series(self, **params):
        pass

    @abstractmethod
    def cancel_series(self, program_id: str, series_link: str):
        pass

    @abstractmethod
    def send_key(self, key: RemoteKey):
        pass

    @abstractmethod
    def cancel_recording(self, program_id: str):
        pass

    @abstractmethod
    def delete_recordings(self, recording_ids: List[str]):
        pass
