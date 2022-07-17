from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from pyfetchtv.api.const.remote_keys import RemoteKey
from pyfetchtv.api.fetchtv_interface import FetchTvInterface


class FetchTvMessagesInterface(ABC):

    @property
    @abstractmethod
    def last_received(self) -> datetime:
        pass

    @abstractmethod
    def send_ping(self, terminal_id: str):
        pass

    @abstractmethod
    def send_is_alive(self, terminal_id: str):
        pass

    @abstractmethod
    def send_remote_key(self, terminal_id: str, key: RemoteKey):
        pass

    @abstractmethod
    def play_channel(self, terminal_id: str, channel_id: str):
        pass

    @abstractmethod
    def send_media_state(self, terminal_id: str):
        pass

    @abstractmethod
    def record_program(self, terminal_id: str, channel_id: str, program_id: str, epg_program_id: str,
                       protect_item: bool = False):
        pass

    @property
    @abstractmethod
    def fetchtv(self) -> FetchTvInterface:
        pass

    @abstractmethod
    def cancel_recording(self, terminal_id: str, program_id: str):
        pass

    @abstractmethod
    def send_delete_recordings(self, terminal_id: str, recording_ids: List[str]):
        pass

    @property
    @abstractmethod
    def messages(self) -> List[dict]:
        pass

    @abstractmethod
    def cancel_series(self, terminal_id: str, program_id: str, series_link: str):
        pass

    @abstractmethod
    def record_series(self, terminal_id: str, **params):
        pass
