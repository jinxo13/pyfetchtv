import os
import pprint
import time
import logging
from os.path import join, dirname

from dotenv import load_dotenv

from pyfetchtv.api.const.remote_keys import RemoteKey
from pyfetchtv.api.fetchtv import FetchTV
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
    print(f'MESSAGE: {msg.msg_type}')
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
            if fetchtv.get_boxes():
                break
            time.sleep(1)

        if not fetchtv.get_boxes():
            logger.error('No boxes found. Check your FetchTV box is on.')

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
        if box.state.play_state == PlayState.Idle:
            print(f'\n--> Turning {box.label} on.')
            box.send_key(RemoteKey.Power)

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
        box.record_program(box.state.channel_id, program.program_id, program.epg_program_id)
        time.sleep(CMD_DELAY)

        # List recordings for today
        print(f'\n--> Recordings...')
        pp.pprint([rec.name for rec in box.recordings.future])

        # Cancel recording
        print(f'\n--> Cancel recording')
        recording_ids = [rec.id for rec in box.recordings.future if rec.program_id == program.program_id]
        box.cancel_recording(program.program_id)
        time.sleep(CMD_DELAY)

        # List stored recording
        print(f'\n--> Stored recording')
        pp.pprint([rec.dlna_url for rec in box.recordings.items.values() if rec.program_id == program.program_id])

        # Delete recording
        print(f'\n--> Delete recording')
        box.delete_recordings(recording_ids)
        time.sleep(CMD_DELAY)

    finally:
        fetchtv.close()
