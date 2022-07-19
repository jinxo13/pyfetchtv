from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Optional, List, Callable

from pyfetchtv.api.fetchtv_box_interface import FetchTvBoxInterface
from pyfetchtv.api.json_objects.account import Account
from pyfetchtv.api.json_objects.channel import Channel
from pyfetchtv.api.json_objects.epg import Program
from pyfetchtv.api.json_objects.epg_channel import EpgChannel
from pyfetchtv.api.json_objects.epg_region import EpgRegion


class MessageType(Enum):
    Pause = 0
    Play = 1
    Stop = 2
    Record = 3


class SubscriberMessage:
    def __init__(self, time: int, message: dict, msg_type: MessageType, terminal_id: str):
        self.__time = time
        self.__message = message
        self.__msg_type = msg_type
        self.__terminal_id = terminal_id

    @property
    def time(self) -> int:
        return self.__time

    @property
    def message(self) -> dict:
        return self.__message

    @property
    def msg_type(self) -> MessageType:
        return self.__msg_type

    @property
    def terminal_id(self) -> str:
        return self.__terminal_id


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

    @abstractmethod
    def add_subscriber(self, subscriber_id: str, callback: Callable[[SubscriberMessage], None]):
        pass

    @abstractmethod
    def remove_subscriber(self, subscriber_id: str):
        pass

    @abstractmethod
    def publish_to_subscribers(self, msg: SubscriberMessage):
        pass
