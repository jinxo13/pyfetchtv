from enum import unique, Enum


@unique
class ChannelType(Enum):
    Unknown = 0
    Radio = 1
    Television = 2
