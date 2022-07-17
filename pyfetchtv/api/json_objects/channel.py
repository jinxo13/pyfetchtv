from pyfetchtv.api.const.channel_type import ChannelType
from pyfetchtv.api.json_objects.json_object import JsonObject, json_property


class Channel(JsonObject):

    @json_property(name='id')
    def id(self):
        return ''

    @json_property(name='epg_id')
    def epg_id(self):
        return 0

    @json_property(name='name')
    def name(self) -> str:
        return ''

    @json_property(name='isRecordable')
    def is_recordable(self):
        return False

    @json_property(name='image')
    def image_url(self):
        return ''

    @json_property(name='description')
    def description(self):
        return ''

    @json_property(name='is_4k')
    def is_4k(self):
        return False

    @json_property(name='isAudio')
    def __is_audio(self):
        return False

    @json_property(name='isVideo')
    def __is_video(self):
        return False

    @json_property(name='high_definition')
    def __high_definition(self):
        return False

    @property
    def high_definition(self):
        # The JSON field is always false, approximate based on channel name
        return self.__high_definition or "HD" in self.name

    @property
    def channel_type(self) -> ChannelType:
        if self.__is_audio and not self.__is_video:
            return ChannelType.Radio
        elif self.__is_video:
            return ChannelType.Television
        else:
            return ChannelType.Unknown
