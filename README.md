FetchTV python library
Compatible with Python 3.7

## Description
Connects to the FetchTV ecosystem allowing:
- Sending commands to a Fetch Box
- Recording free-to-air (FTA) programs
- Listing and deleting recordings

The API retrieves and maintains the FetchTV data locally.
The primary classes are:
* **FetchTV** - Primary object to interact with FetchTV
  * Login with authorisation code and PIN
  * Access a FetchTV Box
  * Access the Electronic Program Guide (EPG)
  * Subscribe a callback for events
  

* **FetchTvBox** - Represents a FetchTV box, allowing checking state and calling functions.
  * Returned from FetchTV by: ```fetchtv.get_boxes(), fetchtv.get_box(<terminal_id>)```
  * Send Remote Key (Play, Pause, etc...)
  * Record/Cancel a program
  * List/delete recordings
  * Record/Cancel a series

## Installing
Add the respective version to your ```requirements.txt``` file
```
git+https://github.com/jinxo13/pyfetchtv@v0.4.9#egg=pyfetchtv
```

## Example Usage
Refer to the examples in ```test/examples```
```python
import os
import pprint
import sys
import time
import logging
from os.path import join, dirname

from dotenv import load_dotenv

from pyfetchtv.api.const.remote_keys import RemoteKey
from pyfetchtv.api.fetchtv import FetchTV
from pyfetchtv.api.fetchtv_box_interface import RecordProgramParameters
from pyfetchtv.api.fetchtv_interface import SubscriberMessage
from pyfetchtv.api.json_objects.set_top_box import PlayState

CMD_DELAY = 5

pp = pprint.PrettyPrinter(indent=2)

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

logger = logging.getLogger()
# logger.level = logging.DEBUG
# stream_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(stream_handler)


def callback(msg: SubscriberMessage):
    print(f'Received Message: {msg.group} - {msg.command}')
    print('-->' + str(msg.message))


if __name__ == "__main__":

    fetchtv = FetchTV(ping_sec=60)
    fetchtv.add_subscriber('me', callback)

    print(f'\n--> Login to FetchTV')
    if not fetchtv.login(os.environ.get('ACTIVATION_CODE'), os.environ.get('PIN')):
        logger.error('Login to FetchTV failed, check activation code and pin are correct.')
        exit(1)

    try:
        # Wait for box
        for _ in range(10):
            if len(fetchtv.get_boxes()) > 0:
                break
            time.sleep(1)

        if len(fetchtv.get_boxes()) == 0:
            logger.error('No boxes found. Check your FetchTV box is on.')
            exit(0)

        # Print box status
        terminal_id = ''
        print(f'\n--> FetchTV Boxes')
        for box in fetchtv.get_boxes().values():
            print(f'Box Id: {box.terminal_id}, Name: {box.label}')
            print('-->' + str(box.state.to_dict()))
            if not terminal_id:
                terminal_id = box.terminal_id

        # Turn on
        box = fetchtv.get_box(terminal_id)
        if box.state.play_state == PlayState.IDLE:
            print(f'\n--> Turning {box.label} on.')
            box.send_key(RemoteKey.Power)
            time.sleep(CMD_DELAY)

        # Pause
        print(f'\n--> Pause')
        box.send_key(RemoteKey.PlayPause)
        time.sleep(CMD_DELAY)

        # Play
        print(f'\n--> Play')
        box.send_key(RemoteKey.PlayPause)
        time.sleep(CMD_DELAY)

        # Stop (goes back to live TV)
        print(f'\n--> Stop')
        box.send_key(RemoteKey.Stop)
        time.sleep(CMD_DELAY)

        # Retrieve current program
        program = box.get_current_program()
        if not program:
            logger.error(f'No current program TV found on FetchTV box {box.label}.')
            exit(1)

        print(f'\n--> Current program')
        print(program.to_dict())

        # Record current program
        print(f'\n--> Record current program')
        box.record_program(RecordProgramParameters(
            channel_id=box.state.channel_id,
            program_id=program.program_id,
            epg_program_id=program.epg_program_id))
        time.sleep(CMD_DELAY)

        # List recordings for today
        print(f'\n--> Recordings...')
        pp.pprint([rec.name for rec in box.recordings.future.values()])

        # Cancel recording
        print(f'\n--> Cancel recording')
        box.cancel_recording(program.program_id)
        time.sleep(CMD_DELAY)

        # List stored recording
        print(f'\n--> Stored recording')
        pp.pprint([rec.dlna_url for rec in box.recordings.items.values() if rec.program_id == program.program_id
                   and not rec.pending_delete])

        # Delete recording
        print(f'\n--> Delete recording')
        recording_ids = [rec.id for rec in box.recordings.items.values()
                         if rec.program_id == program.program_id and not rec.pending_delete]
        box.delete_recordings(recording_ids)
        time.sleep(CMD_DELAY)

    finally:
        fetchtv.close()
```
