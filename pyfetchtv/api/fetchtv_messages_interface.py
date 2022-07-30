from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from pyfetchtv.api.const.remote_keys import RemoteKey
from pyfetchtv.api.fetchtv_box_interface import RecordSeriesParameters, RecordProgramParameters
from pyfetchtv.api.fetchtv_interface import FetchTvInterface, SubscriberMessage


class FetchTvMessagesInterface(ABC):

    @property
    @abstractmethod
    def last_received(self) -> datetime:
        """
        .
        :return The last time a message was received:
        """
        pass

    @abstractmethod
    def send_ping(self, terminal_id: str):
        """
        Send a Ping message to a FetchTV Box. Responds with a "PONG" message.
        :param terminal_id: The FetchTV Box ID
        """
        pass

    @abstractmethod
    def send_is_alive(self, terminal_id: str):
        """
        Send is alive message, returns full Fetch TV Box state as an "I_AM_ALIVE" message.
        :param terminal_id: The FetchTV Box ID
        """
        pass

    @abstractmethod
    def send_remote_key(self, terminal_id: str, key: RemoteKey):
        """
        Sends a Remote Key to the FetchTV box. e.g. Play, Pause, Stop etc...
        :param terminal_id: The FetchTV Box ID
        :param key: RemoteKey enumeration
        """
        pass

    @abstractmethod
    def play_channel(self, terminal_id: str, channel_id: str):
        """
        Change the FetchTV box to the channel provided.
        :param terminal_id: The FetchTV Box ID
        :param channel_id: The Channel Id
        """
        pass

    @abstractmethod
    def send_media_state(self, terminal_id: str):
        """
        Sends a message to get the current media state of the FetchTV Box. Returns a "MEDIA_STATE" message.
        :param terminal_id: The FetchTV Box ID
        """
        pass

    @abstractmethod
    def record_program(self, terminal_id: str, params: RecordProgramParameters):
        """
        Schedule the provided program to record.
        :param terminal_id: The FetchTV Box ID
        :param params: The program details
        """
        pass

    @property
    @abstractmethod
    def fetchtv(self) -> FetchTvInterface:
        """
        .
        :return: The main FetchTV instance.
        """
        pass

    @abstractmethod
    def cancel_recording(self, terminal_id: str, program_id: str):
        """
        Cancel the specified program from recording.
        :param terminal_id: The FetchTV Box ID
        :param program_id: The Program ID
        """
        pass

    @abstractmethod
    def send_delete_recordings(self, terminal_id: str, recording_ids: List[int]):
        """
        Delete the specified stored recordings from the FetchTV box.
        This sets the recordings to Pending Delete, the FetchTV box will delete them eventually, or as needed.
        :param terminal_id: The FetchTV Box ID
        :param recording_ids: A list of the Recording IDs
        """
        pass

    @property
    @abstractmethod
    def messages(self) -> List[SubscriberMessage]:
        """
        .
        :return: A list of messages sent to Subscribers from oldest to newest, capped at 10 messages.
        """
        pass

    @abstractmethod
    def cancel_series(self, terminal_id: str, program_id: str, series_link: str):
        """
        Cancel the specified Series from recording.
        :param terminal_id: The FetchTV Box ID
        :param program_id: The program ID
        :param series_link: The series ID
        """
        pass

    @abstractmethod
    def record_series(self, terminal_id: str, params: RecordSeriesParameters):
        """
        :param terminal_id: The FetchTV Box ID
        :param params: The details of the series to record
        """
        pass
