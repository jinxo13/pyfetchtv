from datetime import datetime
from typing import Optional, List

from pyfetchtv.api.const.remote_keys import RemoteKey
from pyfetchtv.api.fetchtv_box_interface import FetchTvBoxInterface
from pyfetchtv.api.fetchtv_messages_interface import FetchTvMessagesInterface
from pyfetchtv.api.json_objects.epg import Program
from pyfetchtv.api.json_objects.recording import Recording
from pyfetchtv.api.json_objects.series import Series
from pyfetchtv.api.json_objects.set_top_box import State
from pyfetchtv.api.const.message_types import MessageTypeIn


class FetchTvBox(FetchTvBoxInterface):

    def send_key(self, key: RemoteKey):
        self.__msg_handler.send_remote_key(self.terminal_id, key)

    def __init__(self, msg_handler: FetchTvMessagesInterface, json):
        super().__init__(json)
        self.__msg_handler = msg_handler

    def ping(self):
        self.__msg_handler.send_ping(self.terminal_id)

    def is_alive(self):
        self.__msg_handler.send_is_alive(self.terminal_id)

    def process_message(self, message: dict):
        msg_type = message['message']['type']
        if msg_type in [MessageTypeIn.MEDIA_STATE.name, MessageTypeIn.NOW_PLAYING.name]:
            self._state = State(message['message']['data']['currentPlaybackMedia'])
        elif msg_type in [MessageTypeIn.PAUSED.name, MessageTypeIn.UNPAUSED.name]:
            self._state.set_value('playBackState', msg_type)
        elif msg_type == MessageTypeIn.FUTURE_RECORDINGS_LIST.name:
            self._recordings.set_future(message['message'], 'data')
        elif msg_type == MessageTypeIn.PENDING_DELETE_RECORDINGS_BY_ID_SUCCESS.name:
            # Update recordings to delete pending
            recordings_ids = message['message']['data']['recordingsIds']
            for rec in self._recordings.items.values():
                if rec.id in recordings_ids:
                    rec.delete()
        elif msg_type == MessageTypeIn.RECORDINGS_UPDATE.name:
            recordings = message['message']['data']['recordingUpdates']
            if recordings[0]['eventName'] == 'SERIES_TAG_CANCELLED':
                series_link = recordings[0]['seriesTag']['id']
                series = [i for i in range(len(self.recordings.series))
                          if self.recordings.series[i].series_link == series_link]
                del self.recordings.series[series[0]]
            elif recordings[0]['eventName'] == 'SERIES_TAG_SET':
                self.recordings.series.append(Series(recordings[0]['seriesTag']))
            else:
                recording = Recording(self, recordings[len(recordings) - 1]['recording'])
                self._recordings.items[recording.id] = recording

    def update_media_state(self):
        self.__msg_handler.send_media_state(self.terminal_id)

    def play_channel(self, channel_id: str):
        self.__msg_handler.play_channel(self.terminal_id, channel_id)

    def record_channel(self, channel_id: str):
        self.play_channel(channel_id)
        self.__msg_handler.send_remote_key(self.terminal_id, RemoteKey.Record)

    def record_program(self, channel_id: str, program_id: str, epg_program_id: str, protect_item: bool = False):
        self.__msg_handler.record_program(self.terminal_id, channel_id, program_id, epg_program_id, protect_item)

    def cancel_recording(self, program_id: str):
        self.__msg_handler.cancel_recording(self.terminal_id, program_id)

    def delete_recordings(self, recording_ids: List[int]):
        self.__msg_handler.send_delete_recordings(self.terminal_id, recording_ids)

    def get_current_program(self) -> Optional[Program]:
        if not self.state:
            return None
        channel_id = self.state.channel_id
        if channel_id not in self.dvb_channels.keys():
            return None
        channel = self.dvb_channels[channel_id]
        return self.__msg_handler.fetchtv.get_program(channel, int(datetime.now().timestamp() * 1000))

    def record_series(self, **params):
        self.__msg_handler.record_series(self.terminal_id, **params)

    def cancel_series(self, program_id: str, series_link: str):
        self.__msg_handler.cancel_series(self.terminal_id, program_id, series_link)
