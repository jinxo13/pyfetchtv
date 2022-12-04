import threading
import time
from datetime import datetime, timedelta
from fuzzy_match import algorithims

import requests
import logging

from typing import Optional, Dict, List, Callable

from pyfetchtv.api.const.urls import URL_AUTHENTICATE, URL_MESSAGES, URL_EPG, URL_EPG_CHANNELS
from pyfetchtv.api.fetchtv_box import FetchTvBox
from pyfetchtv.api.fetchtv_interface import FetchTvInterface, SubscriberMessage
from pyfetchtv.api.fetchtv_messages import FetchTvMessageHandler
from pyfetchtv.api.json_objects.account import Account
from pyfetchtv.api.json_objects.channel import Channel
from pyfetchtv.api.json_objects.epg import Program
from pyfetchtv.api.json_objects.epg_channel import EpgChannel
from pyfetchtv.api.json_objects.epg_region import EpgRegion
from pyfetchtv.api.json_objects.set_top_box import SetTopBox

STANDARD_HEADERS = {
    "Accept": "application/json",
    "X-FTV-Capabilities": "no_pin,android,v3.21.1.4988,tenplay_v2",
    "X-FTV-Timeout": "3",
    "Accept-Encoding": "gzip, deflate, br"
}

logger = logging.getLogger(__name__)


class FetchTV(FetchTvInterface):

    def publish_to_subscribers(self, msg: SubscriberMessage):
        thread = threading.Thread(target=self.__publish_runnable, args=(msg,))
        thread.start()

    def __publish_runnable(self, msg: SubscriberMessage):
        for callback in self.__subscribers.values():
            try:
                callback(msg)
            except:
                logger.error('Callback to subscriber failed', exc_info=True)

    def add_subscriber(self, subscriber_id: str, callback: Callable[[SubscriberMessage], None]):
        self.__subscribers[subscriber_id] = callback

    def remove_subscriber(self, subscriber_id: str):
        if subscriber_id in self.__subscribers.keys():
            del self.__subscribers[subscriber_id]

    @property
    def epg(self) -> dict:
        return self.__epg

    @property
    def messages(self):
        return self.__message_handler.messages

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __update_epg_periodic(self):
        while self.__connected:
            self.__update_epg()
            for _ in range(60 * 60):  # wait for an hour
                if not self.__connected:
                    break
                time.sleep(1)

    def __update_epg(self):
        if not self.__epg_channels:
            response = self.__request('get epg channels', URL_EPG_CHANNELS, {})
            self.__epg_channels = {k: EpgChannel(v) for k, v in response['channels'].items()}
            self.__epg_regions = {k: EpgRegion(v, k) for k, v in response['region_details'].items()}

        with self.__epg_lock:
            channel_ids = []

            if len(self.get_boxes()) == 0:
                return

            for box in self.get_boxes().values():
                # Get EPG Ids for local channels
                channel_ids.extend([str(v.epg_id) for v in box.dvb_channels.values()])
            channel_ids = set(channel_ids)
            for_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            params = {
                "channel_ids": ','.join(channel_ids),
                "block": f"4-{int(for_date.timestamp() / 14400)}",
                "count": 42,
                "extended": 1,
                "off_air_catchup": 0,
                "include_catchup": 0
            }
            response = self.__request('update epg', URL_EPG, params)
            self.__epg = response

    def get_epg(self, for_date=None) -> Dict[str, List[Program]]:
        for_date = datetime.now() if not for_date else for_date
        to_date = for_date + timedelta(days=2)
        for_date = int(for_date.timestamp() * 1000)
        to_date = int(to_date.timestamp() * 1000)
        with self.__epg_lock:
            channels = self.__epg['channels']
            synopses = self.__epg['synopses']
            program_fields = self.__epg['__meta__']['program_fields']
            pos_start = program_fields.index('start')
            pos_end = program_fields.index('end')
            result = {}
            for k, v in channels.items():
                result[k] = []
                for program in v:
                    if program[pos_end] < for_date or program[pos_start] > to_date:
                        continue
                    result[k].append(Program(program, synopses))
            return result

    @property
    def epg_channels(self) -> Dict[str, EpgChannel]:
        return self.__epg_channels

    @property
    def epg_regions(self) -> Dict[str, EpgRegion]:
        return self.__epg_regions

    def get_program(self, channel: Channel, for_time_msec: int) -> Optional[Program]:
        if str(channel.epg_id) not in self.epg['channels']:
            logger.error(f"Unable to find expected epg_channel [{channel.epg_id}] in {len(self.epg['channels'])} epg channels.")
            return None
        epg = self.epg['channels'][str(channel.epg_id)]
        program_fields = self.__epg['__meta__']['program_fields']
        pos_start = program_fields.index('start')
        pos_end = program_fields.index('end')
        programs = [program for program in epg if program[pos_start] <= for_time_msec <= program[pos_end]]
        if len(programs) > 0:
            return Program(programs[0], self.epg['synopses'])
        return None

    def find_program(self, name: str):
        program_fields = self.__epg['__meta__']['program_fields']
        pos_name = program_fields.index('title')
        results = {}
        synopses = self.__epg['synopses']
        for k, v in self.__epg['channels'].items():
            for program in v:
                match = algorithims.trigram(program[pos_name], name)
                if match > 0.3:
                    program = Program(program, synopses)
                    if hash(program) in results.keys():
                        results[hash(program)]['epg_channels'].append(k)
                    else:
                        results[hash(program)] = {'match': match, 'program': program, 'epg_channels': [k]}
        results = [val for val in results.values()]
        results.sort(reverse=True, key=lambda x: x['match'])
        return results

    @property
    def is_connected(self) -> bool:
        return self.__connected

    @property
    def account(self) -> Account:
        return self.__account

    def __init__(self, ping_sec=60):
        super().__init__()
        self.__epg_channels = {}
        self.__epg_regions = {}
        self.__subscribers = {}
        self.__connected = False
        self.__session = requests.Session()
        self.__epg = {}
        self.__account = None  # type: Optional[Account]
        self.__set_top_boxes = {}  # type: Dict[str, SetTopBox]
        self.__message_handler = FetchTvMessageHandler('FetchTv', self, ping_sec)
        self.__epg_lock = threading.Lock()
        self.__epg_thread = None

    def get_boxes(self):
        return self.__set_top_boxes

    def get_box(self, terminal_id: str):
        return self.__set_top_boxes[terminal_id] if terminal_id in self.__set_top_boxes.keys() else None

    def close(self):
        self.__connected = False
        self.__session.close()
        try:
            self.__epg_thread.join(timeout=10)
        except TimeoutError:
            pass
        self.__message_handler.close()

    def login(self, activation_code: str, pin: str) -> bool:
        params = {}
        data = {"activation_code": activation_code, "pin": pin}
        response = self.__request('login', URL_AUTHENTICATE, params, data)
        if not response:
            return False
        logger.info("FetchTV --> login successful.")
        self.__account = Account(response)
        self.__connected = True
        self.__epg_thread = threading.Thread(target=self.__update_epg_periodic)
        self.__epg_thread.start()
        self.__message_handler.connect(
            url=URL_MESSAGES,
            cookie="auth=" + self.__session.cookies.get('auth')
        )
        for box in self.__account.terminals.values():
            logger.info(f"FetchTV --> Found box [{box.friendly_name}], Status: [{box.status}:{box.activation_status}]")
        return True

    def set_box(self, terminal_id, box_json: dict):
        self.__set_top_boxes[terminal_id] = FetchTvBox(self.__message_handler, box_json)
        self.__update_epg()

    def __request(self, action: str, url: str, params: dict, data: dict = None):
        response = self.__session.post(
            url=URL_AUTHENTICATE,
            params=params,
            headers=STANDARD_HEADERS,
            data=data
        ) if data else \
            self.__session.get(
                url=url,
                params=params,
                headers=STANDARD_HEADERS
            )
        if response.status_code != 200:
            logger.error(f"FetchTV --> {action} failed. {response.status_code}: {response.text}")
            return None
        response = response.json()
        if response['__meta__']['error']:
            logger.error(
                f"FetchTV --> {action} failed. {response['__meta__']['error']}: {response['__meta__']['message']}")
            return None
        return response
