import threading
import time
from datetime import datetime

import requests
import logging

from typing import Optional, Dict, List

from pyfetchtv.api.const.urls import URL_AUTHENTICATE, URL_MESSAGES, URL_EPG, URL_EPG_CHANNELS
from pyfetchtv.api.fetchtv_box import FetchTvBox
from pyfetchtv.api.fetchtv_interface import FetchTvInterface
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

    @property
    def epg(self) -> Dict[str, List[Program]]:
        if not self.__epg:
            self.__update_epg()
        return self.__epg

    @property
    def messages(self):
        return self.__message_handler.messages

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __update_epg_periodic(self):
        for _ in range(60 * 60):  # every hour
            if not self.__connected:
                break
            time.sleep(1)
        if self.__connected:
            self.__update_epg()

    def __update_epg(self):
        with self.__epg_lock:
            self.__epg = self.get_epg()

    def get_epg(self, for_date=None) -> Dict[str, List[Program]]:
        if not self.__epg_channels:
            response = self.__request('get epg channels', URL_EPG_CHANNELS, {})
            self.__epg_channels = {k: EpgChannel(v) for k, v in response['channels'].items()}
            self.__epg_regions = {k: EpgRegion(v, k) for k, v in response['region_details'].items()}
        channel_ids = []
        for_date = datetime.now() if not for_date else for_date
        for box in self.get_boxes().values():
            # Get EPG Ids for local channels
            channel_ids.extend([str(v.epg_id) for v in box.dvb_channels.values()])
        channel_ids = set(channel_ids)
        params = {
            "channel_ids": ','.join(channel_ids),
            "block": f"4-{int(for_date.timestamp() / 14400)}",
            "count": 10,
            "extended": 1,
            "off_air_catchup": 1,
            "include_catchup": 1
        }
        response = self.__request('update epg', URL_EPG, params)
        channels = response['channels']
        Program.synopses = response['synopses']

        result = {}
        for k, v in channels.items():
            result[k] = [Program(program) for program in v]
        return result

    @property
    def epg_channels(self) -> Dict[str, EpgChannel]:
        return self.__epg_channels

    @property
    def epg_regions(self) -> Dict[str, EpgRegion]:
        return self.__epg_regions

    def get_program(self, channel: Channel, for_time_msec: int) -> Optional[Program]:
        epg = self.epg[str(channel.epg_id)]
        programs = [program for program in epg if program.start <= for_time_msec <= program.end]
        if len(programs) > 0:
            return programs[0]
        return None

    @property
    def is_connected(self) -> bool:
        return self.__connected

    @property
    def account(self) -> Account:
        return self.__account

    def __init__(self, ping_sec=60):
        super().__init__()
        self.__connected = False
        self.__session = requests.Session()
        self.__epg = {}
        self.__account = None  # type: Optional[Account]
        self.__set_top_boxes = {}  # type: Dict[str, SetTopBox]
        self.__message_handler = FetchTvMessageHandler('FetchTv', self, ping_sec)
        self.__epg_lock = threading.Lock()
        self.__epg_thread = threading.Thread(target=self.__update_epg_periodic)
        self.__epg_thread.start()
        self.__epg_channels = {}
        self.__epg_regions = {}

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
        self.__message_handler.connect(
            url=URL_MESSAGES,
            cookie="auth=" + self.__session.cookies.get('auth')
        )
        return True

    def set_box(self, terminal_id, box_json: dict):
        self.__set_top_boxes[terminal_id] = FetchTvBox(self.__message_handler, box_json)

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
