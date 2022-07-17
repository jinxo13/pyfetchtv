from pyfetchtv.api.json_objects.json_object import JsonObject, json_property


class Terminal(JsonObject):

    @json_property(name='id')
    def id(self):
        return ''

    @json_property(name='friendly_name')
    def friendly_name(self):
        return ''

    @json_property(name='type')
    def device_type(self):
        return ''

    @json_property(name='pvr')
    def has_pvr(self):
        return False
