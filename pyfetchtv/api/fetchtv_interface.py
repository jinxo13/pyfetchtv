from abc import ABC, abstractmethod
from typing import Dict, Optional, List

from pyfetchtv.api.fetchtv_box_interface import FetchTvBoxInterface
from pyfetchtv.api.json_objects.account import Account
from pyfetchtv.api.json_objects.channel import Channel
from pyfetchtv.api.json_objects.epg import Program
from pyfetchtv.api.json_objects.epg_channel import EpgChannel
from pyfetchtv.api.json_objects.epg_region import EpgRegion


class FetchTvInterface(ABC):

    @property
    @abstractmethod
    def account(self) -> Account:
        pass

    @property
    def is_connected(self) -> bool:
        return False

    @property
    @abstractmethod
    def messages(self):
        pass

    @property
    @abstractmethod
    def epg(self) -> Dict[str, List[Program]]:
        pass

    @abstractmethod
    def login(self, activation_code: str, pin: str) -> bool:
        pass

    @property
    @abstractmethod
    def epg_channels(self) -> Dict[str, EpgChannel]:
        pass

    @property
    @abstractmethod
    def epg_regions(self) -> Dict[str, EpgRegion]:
        pass

    @abstractmethod
    def get_program(self, channel: Channel, time: int) -> Optional[Program]:
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_boxes(self) -> Dict[str, FetchTvBoxInterface]:
        pass

    @abstractmethod
    def set_box(self, terminal_id, box: FetchTvBoxInterface):
        pass

    @abstractmethod
    def get_box(self, terminal_id) -> FetchTvBoxInterface:
        pass

    @abstractmethod
    def get_epg(self, for_date=None) -> Dict[str, List[Program]]:
        pass
