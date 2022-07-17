import json
import logging
import time
from abc import ABC, abstractmethod
from threading import Thread
from typing import Optional
import websocket
from websocket import WebSocketConnectionClosedException

logger = logging.getLogger(__name__)


class WsMessageHandler(ABC):

    def __init__(self, name: str, ping_sec: int = 60):
        self.__connected = False
        self.__name = name
        self.__keep_alive = Thread(target=self._keep_alive)
        self.__message_socket_thread = Thread(target=self.__start)
        self.__message_socket = None  # type: Optional[websocket.WebSocketApp]
        self.__ping_sec = ping_sec
        self.__url = ''
        self.__headers = {}
        self.__cookie = ''

    @property
    def name(self):
        return self.__name

    @property
    def is_connected(self):
        return self.__connected

    @abstractmethod
    def on_message(self, message: str):
        pass

    @abstractmethod
    def on_open(self):
        pass

    @abstractmethod
    def on_error(self, error: str):
        pass

    @abstractmethod
    def keep_alive(self):
        pass

    def _keep_alive(self):
        # Ping every ping_sec
        while self.__connected:
            self.keep_alive()
            for _ in range(self.__ping_sec):
                if not self.__connected:
                    break
                time.sleep(1)

    def connect(self,
                url: str,
                headers: dict = None,
                cookie: str = ''
                ):
        self.__url = url
        self.__headers = headers
        self.__cookie = cookie
        self.__message_socket = websocket.WebSocketApp(
            url=url,
            header=headers,
            cookie=cookie,
            on_message=self.__on_message,
            on_open=self.__on_open,
            on_error=self.__on_error
        )
        if not self.__message_socket_thread.is_alive():
            self.__message_socket_thread.start()

    def __on_message(self, ws, message):
        try:
            self.on_message(message)
        except Exception:
            logger.error('Unexpected error calling on_message', exc_info=True)
            raise

    def __start(self):
        self.__message_socket.run_forever()

    def __on_open(self, ws):
        self.__connected = True
        if not self.__keep_alive.is_alive():
            self.__keep_alive.start()
        logger.info(f"{self.name} --> Ready to receive messages...")
        try:
            self.on_open()
        except Exception:
            logger.error('Unexpected error calling on_open', exc_info=True)
            raise

    def __on_error(self, ws, error):
        try:
            self.on_error(error)
        except Exception:
            logger.error('Unexpected error calling on_error', exc_info=True)
            raise

    def __reconnect(self):
        logger.info('Trying to reconnect websocket....')
        if not self.is_connected:
            return
        # try and reconnect
        try:
            # cleanup old connection
            self.__message_socket.close()
        except WebSocketConnectionClosedException:
            logger.info('*** DEBUG... closing closed socket...', exc_info=True)

        self.__message_socket = websocket.WebSocketApp(
            url=self.__url,
            header=self.__headers,
            cookie=self.__cookie,
            on_message=self.__on_message,
            on_open=self.__on_open,
            on_error=self.__on_error
        )
        try:
            self.__message_socket_thread.join(5)
        except TimeoutError:
            logger.info('*** DEBUG... joining runforever thread...')
        self.__message_socket_thread = Thread(target=self.__start)
        self.__message_socket_thread.start()

    def send_message(self, message: dict):
        try:
            self.__message_socket.send(json.dumps(message))
        except WebSocketConnectionClosedException:
            logger.error(f"{self.name} --> Send message failed.", exc_info=True)
            self.__reconnect()

    def close(self):
        logger.info(f"{self.name} --> Stopped receiving messages.")
        self.__connected = False
        try:
            if self.__message_socket:
                self.__message_socket.close()
        except WebSocketConnectionClosedException:
            pass
        try:
            if self.__message_socket_thread.is_alive():
                self.__message_socket_thread.join(10)
        except TimeoutError:
            pass
        try:
            if self.__keep_alive.is_alive():
                self.__keep_alive.join(10)
        except TimeoutError:
            pass
