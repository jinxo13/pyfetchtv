import json
import logging
import threading
import time
from datetime import datetime
from typing import List

from pyfetchtv.api.const.message_types import MessageTypeOut
from pyfetchtv.api.const.remote_keys import RemoteKey
from pyfetchtv.api.fetchtv_box_interface import RecordSeriesParameters, RecordProgramParameters
from pyfetchtv.api.fetchtv_interface import FetchTvInterface, SubscriberMessage
from pyfetchtv.api.fetchtv_messages_interface import FetchTvMessagesInterface
from pyfetchtv.api.helpers.ws_message_handler import WsMessageHandler

logger = logging.getLogger(__name__)


class FetchTvMessageHandler(WsMessageHandler, FetchTvMessagesInterface):

    @property
    def fetchtv(self) -> FetchTvInterface:
        return self.__fetchtv

    def __init__(self, name: str, fetchtv: FetchTvInterface, ping_sec: int = 60):
        super().__init__(name, ping_sec)
        self.__fetchtv = fetchtv
        self.__last_receive_time = None
        self.__messages = []  # type: List[SubscriberMessage]
        self.__lock = threading.Lock()

    @property
    def messages(self) -> List[SubscriberMessage]:
        return self.__messages

    @property
    def last_received(self) -> datetime:
        return self.__last_receive_time

    def keep_alive(self):
        account = self.__fetchtv.account
        if not account:
            return
        for key in self.__fetchtv.account.terminals.keys():
            self.send_ping(key)

    def _call_send_message(self, to: str, msg_type: MessageTypeOut, is_queueable=False, requires_settopbox=False,
                           only_paired_settopbox=False, values=None):
        msg = self.__create_msg(to, msg_type, is_queueable, requires_settopbox, only_paired_settopbox, values)
        logger.info(f'{self.name} --> Sending {msg_type.name} message to {to}')
        self.send_message(msg)

    def send_ping(self, terminal_id: str):
        self._call_send_message(terminal_id, MessageTypeOut.PING, only_paired_settopbox=True)

    @staticmethod
    def __create_msg(to: str, msg_type: MessageTypeOut, is_queueable=False, requires_settopbox=False,
                     only_paired_settopbox=False, values=None):
        result = {
            "to": to,
            "message": {
                "data": {
                },
                "type": msg_type.name,
                "isQueueable": is_queueable,
                "requiresSetTopBox": requires_settopbox,
                "onlyPairedSetTopBox": only_paired_settopbox
            }
        }
        if values:
            result['message'].update(values)
        result['message']['data']['messageId'] = f"{to}_{str(round(time.time() * 1000))}"
        return result

    def send_is_alive(self, terminal_id):
        self._call_send_message(terminal_id, MessageTypeOut.ARE_YOU_ALIVE, is_queueable=True,
                                only_paired_settopbox=True)

    def send_remote_key(self, terminal_id: str, key: RemoteKey):
        self._call_send_message(terminal_id, MessageTypeOut.KEYEVENT, requires_settopbox=True,
                                values={"keyName": str(key.value)})
        if key == RemoteKey.Stop:
            self.send_media_state(terminal_id)

    def send_keycode(self, terminal_id: str, key: str):
        self._call_send_message(terminal_id, MessageTypeOut.KEYCODE, requires_settopbox=True,
                                values={"keyCode": ord(key[0])})

    def play_channel(self, terminal_id: str, channel_id: str):
        self._call_send_message(terminal_id, MessageTypeOut.PLAY_CHANNEL, requires_settopbox=True,
                                values={"channelId": int(channel_id)})

    def send_media_state(self, terminal_id: str):
        self._call_send_message(terminal_id, MessageTypeOut.MEDIA_STATE, requires_settopbox=True)

    def send_future_recordings(self, terminal_id: str):
        self._call_send_message(terminal_id, MessageTypeOut.FUTURE_RECORDINGS_LIST, requires_settopbox=True)

    def send_delete_recordings(self, terminal_id: str, recording_ids: List[int]):
        recording_ids = [rid for rid in recording_ids]
        self._call_send_message(terminal_id,
                                MessageTypeOut.PENDING_DELETE_RECORDINGS_BY_ID,
                                requires_settopbox=True,
                                values={
                                    'recordingIds': recording_ids,
                                    'startEventRequired': False,
                                    'progressEventRequired': False,
                                    'endEventRequired': False,
                                    'data': {
                                        'recordingIds': recording_ids
                                    }
                                })

    def on_open(self):
        logger.info(f'{self.name} --> Connected to FetchTV Web Socket')

    def on_error(self, error: str):
        logger.info(f"{self.name} --> {error}")

    def on_message(self, message):
        self.__last_receive_time = datetime.now()
        message = json.loads(message)
        if 'type' not in message['message']:
            if message['message']['frag'] not in ['SUBSCRIPTIONS_INITIALISED']:
                logger.warning(f"{self.name} --> Received unknown message:\n{message['message']}")
            return
        msg_type = message['message']['type']
        terminal_id = message['sender']
        logger.info(f"{self.name} --> Received {msg_type} from {terminal_id}.")
        if msg_type == 'I_AM_ALIVE':
            self.__fetchtv.set_box(terminal_id, message['message']['data'])
        box = self.__fetchtv.get_box(terminal_id)
        if msg_type == 'PONG' and not box:
            self.send_is_alive(terminal_id)
        if not box:
            return
        msg = box.process_message(message)
        with self.__lock:
            if len(self.__messages) > 10:
                self.__messages.pop(0)
            self.__messages.append(msg)
        self.__fetchtv.publish_to_subscribers(msg)

    def record_program(self, terminal_id: str, params: RecordProgramParameters):
        self._call_send_message(terminal_id, MessageTypeOut.RECORD_PROGRAM, requires_settopbox=True, values={
            "channelId": params.channel_id,
            "programId": params.program_id,
            "epgProgramId": params.epg_program_id,
            "lagTime": params.lag_time_min,
            "leadTime": params.lead_time_min,
            "protected": params.protect_item
        })

    def cancel_recording(self, terminal_id: str, program_id: str):
        self._call_send_message(terminal_id, MessageTypeOut.RECORD_PROGRAM_CANCEL, requires_settopbox=True, values={
            "programId": program_id
        })

    def cancel_series(self, terminal_id: str, program_id: str, series_link: str):
        self._call_send_message(terminal_id, MessageTypeOut.DISABLE_SERIES_TAG, requires_settopbox=True, values={
            "programId": program_id,
            "seriesLinkId": series_link
        })

    def record_series(self, terminal_id: str, params: RecordSeriesParameters):
        self._call_send_message(terminal_id, MessageTypeOut.ENABLE_SERIES_TAG, requires_settopbox=True, values={
            "seriesLink": params.series_link,
            "channelId": params.channel_id,
            "epgProgramId": params.epg_program_id,
            "programId": params.program_id,
            "leadTime": params.lead_time_min,
            "lagTime": params.lag_time_min,
            "episodesToKeep": params.num_episodes_to_keep,
            "seasonsVal": params.start_season
        })
