import logging
from datetime import datetime
from typing import Optional, List

from pyfetchtv.api.const.remote_keys import RemoteKey
from pyfetchtv.api.fetchtv_box_interface import FetchTvBoxInterface, RecordSeriesParameters, RecordProgramParameters
from pyfetchtv.api.fetchtv_interface import SubscriberMessage
from pyfetchtv.api.fetchtv_messages_interface import FetchTvMessagesInterface
from pyfetchtv.api.json_objects.epg import Program
from pyfetchtv.api.json_objects.recording import Recording
from pyfetchtv.api.json_objects.series import Series
from pyfetchtv.api.json_objects.set_top_box import State
from pyfetchtv.api.const.message_types import MessageTypeIn, MessageType


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

        if msg_type not in [e.name for e in MessageTypeIn]:
            logging.info(f'FetchTV --> Skipping processing message: {msg_type}')

        msg_command = MessageTypeIn[msg_type]
        if msg_command in [MessageTypeIn.NOW_PLAYING, MessageTypeIn.UNPAUSED]:
            msg_command = MessageTypeIn.PLAYING
        sub_message = {}
        msg_group = MessageType.UNKNOWN

        if msg_type == MessageTypeIn.I_AM_ALIVE.name:
            msg_group = MessageType.BOX
            msg_command = MessageTypeIn.BOX_FOUND

        elif msg_type in [MessageTypeIn.MEDIA_STATE.name, MessageTypeIn.NOW_PLAYING.name]:
            self._state = State(message['message']['data']['currentPlaybackMedia'])
            sub_message = self.state.to_dict()
            msg_group = MessageType.STATE

        elif msg_type in [MessageTypeIn.PAUSED.name, MessageTypeIn.UNPAUSED.name]:
            self._state.set_value('playBackState', msg_type)
            sub_message = self.state.to_dict()
            msg_group = MessageType.STATE

        elif msg_type == MessageTypeIn.FUTURE_RECORDINGS_LIST.name:
            self._recordings.set_future(message['message'], 'data')
            sub_message = [rec.to_dict() for rec in self.recordings.future.values()]
            msg_group = MessageType.FUTURE_RECORDINGS

        elif msg_type == MessageTypeIn.PENDING_DELETE_RECORDINGS_BY_ID_SUCCESS.name:
            # Update recordings to delete pending
            recordings_ids = message['message']['data']['recordingsIds']
            msg_command = MessageTypeIn.RECORDINGS_DELETE
            msg_group = MessageType.RECORDINGS
            sub_message = []
            for rec in self._recordings.items.values():
                if rec.id in recordings_ids:
                    sub_message.append(rec.to_dict())

        elif msg_type == MessageTypeIn.RECORDINGS_UPDATE.name:
            recordings = message['message']['data']['recordingUpdates']
            event_name = recordings[0]['eventName']
            if event_name == 'SERIES_TAG_CANCELLED':
                series_link = recordings[0]['seriesTag']['id']
                series = [i for i in range(len(self.recordings.series))
                          if self.recordings.series[i].series_link == series_link]
                sub_message = self.recordings.series[series[0]].to_dict()
                msg_command = MessageTypeIn.SERIES_CANCELLED
                msg_group = MessageType.SERIES
                del self.recordings.series[series[0]]

            elif event_name == 'SERIES_TAG_SET':
                series = Series(recordings[0]['seriesTag'])
                self.recordings.series.append(series)
                msg_command = MessageTypeIn.SERIES_ADDED
                msg_group = MessageType.SERIES
                sub_message = series.to_dict()

            else:
                recording = Recording(self, recordings[len(recordings) - 1]['recording'])
                # Add to/update recordings list
                self._recordings.items[recording.id] = recording
                last_event_name = recordings[len(recordings) - 1]['eventName']
                sub_message = recording.to_dict()
                msg_group = MessageType.RECORDING
                self._recordings.set_active(message['message']['data']['activeRecordings'])
                if event_name == 'RECORD_PROGRAM_SUCCESS':
                    # Add to future
                    self._recordings.future[recording.id] = recording
                    msg_command = MessageTypeIn.RECORD_PROGRAM_SUCCESS

                if last_event_name in ['RECORD_PROGRAM_START', 'RECORD_PROGRAM_STOP']:
                    msg_command = MessageTypeIn[last_event_name]
                    if last_event_name == 'RECORD_PROGRAM_STOP':
                        # Remove from future
                        del self._recordings.future[recording.id]

        return SubscriberMessage(time=int(datetime.now().timestamp()),
                                 message=sub_message,
                                 msg_command=msg_command,
                                 msg_group=msg_group,
                                 terminal_id=self.terminal_id)

    def update_media_state(self):
        self.__msg_handler.send_media_state(self.terminal_id)

    def play_channel(self, channel_id: str):
        self.__msg_handler.play_channel(self.terminal_id, channel_id)

    def record_channel(self, channel_id: str):
        self.play_channel(channel_id)
        self.__msg_handler.send_remote_key(self.terminal_id, RemoteKey.Record)

    def record_program(self, params: RecordProgramParameters):
        self.__msg_handler.record_program(self.terminal_id, params)

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

    def record_series(self, params: RecordSeriesParameters):
        self.__msg_handler.record_series(self.terminal_id, params)

    def cancel_series(self, program_id: str, series_link: str):
        self.__msg_handler.cancel_series(self.terminal_id, program_id, series_link)
