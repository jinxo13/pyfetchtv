from enum import Enum, unique


@unique
class RemoteKey(Enum):
    Back = "KEY_BACK"
    Blue = "KEY_BLUE"
    Down = "KEY_DOWN"
    Exit = "KEY_EXIT"
    FastForward = "KEY_FAST_FORWARD"
    Green = "KEY_GREEN"
    Left = "KEY_LEFT"
    Menu = "KEY_MENU"
    Mute = "KEY_MUTE"
    PlayPause = "KEY_PLAY_PAUSE"
    Power = "KEY_POWER"
    Record = "KEY_RECORD"
    Red = "KEY_RED"
    Rewind = "KEY_REWIND"
    Right = "KEY_RIGHT"
    Select = "KEY_SELECT"
    Stop = "KEY_STOP"
    Text = "KEY_TEXT"
    Up = "KEY_UP"
    Yellow = "KEY_YELLOW"
