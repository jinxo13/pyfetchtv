from abc import ABC, abstractmethod
from typing import Optional, List

from pyfetchtv.api.const.remote_keys import RemoteKey
from pyfetchtv.api.json_objects.epg import Program
from pyfetchtv.api.json_objects.set_top_box import SetTopBox


class RecordProgramParameters:
    """
    Parameters required to record a program
    """
    def __init__(self,
                 channel_id: str,
                 epg_program_id: str,
                 program_id: str,
                 lead_time_min: int = 3,
                 lag_time_min: int = 5,
                 protect_item: bool = False
                 ):
        self.channel_id = channel_id
        self.epg_program_id = epg_program_id
        self.program_id = program_id
        self.lead_time_min = lead_time_min
        self.lag_time_min = lag_time_min
        self.protect_item = protect_item


class RecordSeriesParameters(RecordProgramParameters):
    """
    Parameters required to record a series
    """
    def __init__(self, series_link: str, channel_id: str, epg_program_id: str, program_id: str, lead_time_min: int = 3,
                 lag_time_min: int = 5, num_episodes_to_keep: int = 0, start_season: int = 1):
        super().__init__(channel_id, epg_program_id, program_id, lead_time_min, lag_time_min)
        self.series_link = series_link
        self.num_episodes_to_keep = num_episodes_to_keep
        self.start_season = start_season


class FetchTvBoxInterface(SetTopBox, ABC):

    @abstractmethod
    def ping(self):
        """
        Send a ping message to this box, it should respond with a pong
        """
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        """
        .
        :return True if this box is responding to pings:
        """
        pass

    @abstractmethod
    def process_message(self, message: dict):
        """
        Process a received FetchTV message, updating the stored FetchTV box state.
        :param message: The message to process
        """
        pass

    @abstractmethod
    def update_media_state(self):
        """
        Retrieves the current media state from the FetchTV box
        """
        pass

    @abstractmethod
    def play_channel(self, channel_id: str):
        """
        Changes to the channel provided
        :param channel_id:
        """
        pass

    @abstractmethod
    def record_channel(self, channel_id: str):
        """
        Starts recording the provided channel
        :param channel_id:
        """
        pass

    @abstractmethod
    def record_program(self, params: RecordProgramParameters):
        """
        Schedules the provided program to record.
        :param params: The program details
        """
        pass

    @abstractmethod
    def get_current_program(self) -> Optional[Program]:
        """
        :return: The current playing program on the FetchTV box
        """
        pass

    @abstractmethod
    def record_series(self, params: RecordSeriesParameters):
        """
        Schedules the specified series to record
        :param params: The series details
        """
        pass

    @abstractmethod
    def cancel_series(self, program_id: str, series_link: str):
        """
        Cancels the series from recording
        :param program_id:
        :param series_link:
        """
        pass

    @abstractmethod
    def send_key(self, key: RemoteKey):
        """
        Simulates pressing a remote key
        :param key:
        """
        pass

    @abstractmethod
    def cancel_recording(self, program_id: str):
        """
        Cancels the provided program from recording
        :param program_id:
        """
        pass

    @abstractmethod
    def delete_recordings(self, recording_ids: List[int]):
        """
        Deletes the provided recordings from the FetchTV box.
        These will be set to pending delete and eventually removed.
        :param recording_ids:
        """
        pass
