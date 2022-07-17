from pyfetchtv.api.json_objects.json_object import JsonObject, json_property


class Series(JsonObject):

    @property
    def series_link(self):
        return self.id

    @json_property(name='id')
    def id(self):
        return ''

    @json_property(name='name')
    def name(self):
        return ''

    @json_property(name='channelId')
    def channel_id(self):
        return ''

    @json_property(name='priority')
    def priority(self):
        return 0

    @json_property(name='leadTime')
    def lead_time(self):
        return 0

    @json_property(name='lagTime')
    def lag_time(self):
        return 0

    @json_property(name='latestSeason')
    def latest_season(self):
        return ''

    @json_property(name='latestEpisode')
    def latest_episode(self):
        return ''

    @json_property(name='modifiedDate')
    def updated(self) -> int:
        return 0
