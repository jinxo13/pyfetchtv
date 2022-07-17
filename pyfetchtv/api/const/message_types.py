from enum import Enum, unique


@unique
class MessageTypeOut(Enum):
    KEYEVENT = 1
    PLAY_CHANNEL = 2
    ARE_YOU_ALIVE = 3
    MEDIA_STATE = 4
    PING = 5
    RECORD_PROGRAM_CANCEL = 6
    DISABLE_SERIES_TAG = 7
    DISABLE_TEAM_TAG = 8
    GET_RECORDINGS_SUMMARY = 9
    PENDING_DELETE_RECORDINGS_BY_ID = 10
    PLAY_ASSET = 11
    KEYCODE = 12
    SERIES_TAG_LIST_REORDER = 13
    LIBRARY_LIST = 14
    FUTURE_RECORDINGS_LIST = 15
    SERIES_TAG_LIST = 16
    RESTORE_RECORDINGS_BY_ID = 17
    RECORD_PROGRAM = 18
    ENABLE_SERIES_TAG = 19
    ENABLE_TEAM_TAG = 20
    SET_VOLUME = 21
    WAKE_STB = 22
    WISHLISTS_CHANGED = 23


@unique
class MessageTypeIn(Enum):
    PONG = 1
    I_AM_ALIVE = 2
    BOOKMARKS_CHANGED = 3
    CHANNEL_CHANGED = 4
    CHANNEL_UNAVAILABLE = 5
    COMMAND_ERROR = 6
    ERR_CONCURRENCY_LIMIT = 7
    CREDIT_USED = 8
    DOWNLOAD_CREATED = 9
    DOWNLOAD_PLAYABLE = 10
    GET_RECORDINGS_SUMMARY = 11
    ENTITLEMENTS_CHANGED = 12
    WISHLISTS_CHANGED = 13
    NOW_PLAYING = 14
    PIN_CHANGED = 15
    RECORD_PROGRAM_CANCEL = 16
    RECORD_PROGRAM_FAILURE = 17
    PENDING_DELETE_RECORDINGS_BY_ID_SUCCESS = 18
    RESTORE_RECORDINGS_BY_ID_SUCCESS = 19
    RECORD_PROGRAM_SUCCESS = 20
    RECORD_PROGRAM_STOP = 21
    RECORDINGS_UPDATE = 22
    RECORDING_UNAVAILABLE = 23
    RECORDING_UPDATED = 24
    FUTURE_RECORDINGS_LIST = 25
    SERIES_TAG_LIST = 26
    PAUSED = 27
    MEDIA_STATE = 28
    UNPAUSED = 29
    SUBSCRIPTIONS_CHANGED = 30
    UPDATE_SETTINGS = 31
    VOD_ACTIVATED = 32
    VOD_UNAVAILABLE = 33
    VOLUME_SET = 34