import json
import logging
import threading
import time
from datetime import datetime
from typing import List

from pyfetchtv.api.const.message_types import MessageTypeOut, MessageTypeIn
from pyfetchtv.api.const.remote_keys import RemoteKey
from pyfetchtv.api.fetchtv_box_interface import FetchTvBoxInterface
from pyfetchtv.api.fetchtv_interface import FetchTvInterface
from pyfetchtv.api.fetchtv_messages_interface import FetchTvMessagesInterface
from pyfetchtv.api.helpers.ws_message_handler import WsMessageHandler
from pyfetchtv.api.json_objects.recording import Recording

logger = logging.getLogger(__name__)


class FetchTvMessageHandler(WsMessageHandler, FetchTvMessagesInterface):

    @property
    def fetchtv(self) -> FetchTvInterface:
        return self.__fetchtv

    def __init__(self, name: str, fetchtv: FetchTvInterface, ping_sec: int = 60):
        super().__init__(name, ping_sec)
        self.__fetchtv = fetchtv
        self.__last_receive_time = None
        self.__messages = []
        self.__lock = threading.Lock()

    @property
    def messages(self):
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

    def send_delete_recordings(self, terminal_id: str, recording_ids: List[str]):
        recording_ids = [int(rid) for rid in recording_ids]
        params = {
            'recordingIds': recording_ids,
            'startEventRequired': False,
            'progressEventRequired': False,
            'endEventRequired': False,
            'data': {
                'recordingIds': recording_ids
            }
        }
        self._call_send_message(
            terminal_id,
            MessageTypeOut.PENDING_DELETE_RECORDINGS_BY_ID,
            requires_settopbox=True,
            values=params)

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

        elif msg_type == 'PONG':
            # Box is alive
            if terminal_id not in self.__fetchtv.get_boxes().keys():
                self.send_is_alive(terminal_id)

        elif msg_type == 'RECORDINGS_UPDATE':
            # Update recordings
            self.send_future_recordings(terminal_id)

        box = self.__fetchtv.get_box(terminal_id)
        if not box:
            return
        try:
            box.process_message(message)
        except Exception:
            logger.error(f'{self.name} --> Unexpected error', exc_info=True)
            self.__add_subscriber_msg(box, msg_type, message)
            raise
        self.__add_subscriber_msg(box, msg_type, message)

    def record_program(self, terminal_id: str, channel_id: str, program_id: str, epg_program_id: str,
                       protect_item: bool = False):
        params = {
            "channelId": channel_id,
            "programId": program_id,
            "epgProgramId": epg_program_id,
            "lagTime": 3 * 60,
            "leadTime": 5 * 60,
            "protected": protect_item
        }
        self._call_send_message(terminal_id, MessageTypeOut.RECORD_PROGRAM, requires_settopbox=True, values=params)

    def __add_subscriber_msg(self, box: FetchTvBoxInterface, msg_type, message):
        if msg_type in ['PING', 'ARE_YOU_ALIVE']:
            # Nothing to do
            return

        subscribe_msg = {
            'time': datetime.utcnow().timestamp(),
            'message': {},
            'type': msg_type,
            'terminal_id': box.terminal_id}

        if msg_type in [MessageTypeIn.MEDIA_STATE.name, MessageTypeIn.NOW_PLAYING.name,
                        MessageTypeIn.UNPAUSED.name, MessageTypeIn.PAUSED.name]:
            subscribe_msg['type'] = 'STATE'
            subscribe_msg['message'] = box.state.to_dict()

        elif msg_type == 'I_AM_ALIVE':
            subscribe_msg['type'] = 'BOX'
            subscribe_msg['message'] = box.to_dict()

        elif msg_type == 'FUTURE_RECORDINGS_LIST':
            subscribe_msg['message'] = [rec.to_dict() for rec in box.recordings.future]

        elif msg_type == 'PENDING_DELETE_RECORDINGS_BY_ID_SUCCESS':
            subscribe_msg['type'] = 'DELETE_RECORDINGS'
            subscribe_msg['message'] = message['message']['data']['recordingsIds']

        elif msg_type == MessageTypeIn.RECORDINGS_UPDATE.name:
            subscribe_msg['type'] = 'RECORDINGS'
            recordings = message['message']['data']['recordingUpdates']
            if recordings[0]['eventName'] in ['SERIES_TAG_CANCELLED', 'SERIES_TAG_SET']:
                subscribe_msg['type'] = 'SERIES'
            else:
                item = Recording(box, recordings[len(recordings)-1]['recording']).to_dict()
                subscribe_msg['message'] = item

        with self.__lock:
            if len(self.__messages) > 10:
                self.__messages.pop(0)
            self.__messages.append(subscribe_msg)

    def cancel_recording(self, terminal_id: str, program_id: str):
        params = {
            "programId": program_id
        }
        self._call_send_message(
            terminal_id,
            MessageTypeOut.RECORD_PROGRAM_CANCEL,
            requires_settopbox=True,
            values=params)

    def cancel_series(self, terminal_id: str, program_id: str, series_link: str):
        params = {
            "programId": program_id,
            "seriesLinkId": series_link
        }
        self._call_send_message(terminal_id, MessageTypeOut.DISABLE_SERIES_TAG, requires_settopbox=True, values=params)

    def record_series(self, terminal_id: str, **params):
        params = {
          "seriesLink": params['series_link'],
          "channelId": params['channel_id'],
          "epgProgramId": params['epg_program_id'],
          "programId": params['program_id'],
          "leadTime": params['lead_time_min'] if 'lead_time_min' in params else 3,
          "lagTime": params['lag_time_min'] if 'lag_time_min' in params else 5,
          "episodesToKeep": params['keep_episodes'] if 'keep_episodes' in params else 0,
          "seasonsVal": params['start_season'] if 'start_season' in params else 1
        }
        self._call_send_message(terminal_id, MessageTypeOut.ENABLE_SERIES_TAG, requires_settopbox=True, values=params)
