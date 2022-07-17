from typing import Dict

from pyfetchtv.api.json_objects.channel import Channel
from pyfetchtv.api.json_objects.json_object import JsonObject, json_property
from pyfetchtv.api.json_objects.recording import Recordings


class Hardware(JsonObject):

    @json_property(name='hardwareName')
    def name(self):
        return ''

    @json_property(name='hardwareType')
    def type(self) -> str:
        return ''

    @json_property(name='pvr')
    def is_pvr(self):
        return False

    @json_property(path='$.tuner.tunersAvailable')
    def tuners_available(self):
        return 0

    @json_property(path='$.tuner.maximumRecordingCount')
    def max_recordings(self):
        return 0


class Storage(JsonObject):

    @json_property(path='$.freeSize')
    def free_space(self):
        return 0

    @json_property(path='$.recordingsAllocation')
    def recordings_space(self):
        return 0


class State(JsonObject):

    @json_property(name='playbackType')
    def playback_type(self):
        return ''

    @json_property(name='channelId')
    def channel_id(self):
        return ''

    @json_property(name='mediaTitle')
    def media_title(self):
        return ''

    @json_property(name='playBackState')
    def play_state(self):
        return ''


class SetTopBox(JsonObject):

    def __init__(self, json):
        super().__init__(json)
        hardware_json = self._get_json_path_value(json, '$.sysInfo.hardwareCapabilities')
        hardware_json['hardwareName'] = self._get_json_path_value(json, '$.sysInfo.hardwareName')
        hardware_json['hardwareType'] = self._get_json_path_value(json, '$.sysInfo.hardwareType')
        self._hardware = Hardware(hardware_json)
        self._storage = Storage(self._get_json_value(json, 'storageInfo'))
        self._state = State(self._get_json_value(json, 'state'))
        self._recordings = Recordings(self, json)
        channels = [Channel(channel) for channel in self._get_json_value(json, 'dvbChannels')]
        self._dvb_channels = {v.id: v for v in channels}

    @property
    def hardware(self) -> Hardware:
        return self._hardware

    @property
    def storage(self) -> Storage:
        return self._storage

    @property
    def dvb_channels(self) -> Dict[str, Channel]:
        return self._dvb_channels

    @property
    def recordings(self) -> Recordings:
        return self._recordings

    @property
    def state(self):
        return self._state

    @json_property(path='$.sysInfo.label')
    def label(self) -> str:
        return ''

    @json_property(name='ipAddress')
    def ip_address(self) -> str:
        return ''

    @json_property(name='standby')
    def is_in_standby(self) -> bool:
        return False

    @json_property(name='idle')
    def is_idle(self) -> bool:
        return False

    @json_property(path='$.sysInfo.terminalId')
    def terminal_id(self) -> str:
        return ''

    @json_property(path='$.sysInfo.macAddress')
    def mac_address(self) -> str:
        return ''

    @json_property(path='$.sysInfo.dlnaPort')
    def dlna_port(self) -> str:
        return ''

    @json_property(path='$.sysInfo.dlnaURL')
    def dlna_url(self) -> str:
        return ''

    @json_property(path='$.sysInfo.uptime')
    def up_from(self) -> int:
        return 0
