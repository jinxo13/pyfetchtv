from pyfetchtv.api.json_objects.json_object import JsonObject
from pyfetchtv.api.json_objects.terminal import Terminal


class Account(JsonObject):
    def __init__(self, json):
        super().__init__(json)
        self.__terminals = {}
        for terminal in json['terminals']:
            terminal = Terminal(terminal)
            self.__terminals[terminal.id] = terminal

    @property
    def terminals(self):
        return self.__terminals
