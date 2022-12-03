import logging
import os
import sys
import time
import unittest
from os.path import join, dirname

from dotenv import load_dotenv

from pyfetchtv.api.const.remote_keys import RemoteKey
from pyfetchtv.api.fetchtv import FetchTV


class TestFetchTV(unittest.TestCase):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger()
    # logger.level = logging.DEBUG
    # stream_handler = logging.StreamHandler(sys.stdout)
    # logger.addHandler(stream_handler)

    def setUp(self) -> None:
        pass

    def test_login(self):
        fetchtv = FetchTV()
        try:
            self.assertFalse(fetchtv.is_connected)
            self.assertFalse(fetchtv.login("123", "123"))
            self.assertFalse(fetchtv.is_connected)

            self.assertTrue(fetchtv.login(os.environ.get('ACTIVATION_CODE'), os.environ.get('PIN')))
            self.assertTrue(fetchtv.is_connected)
            time.sleep(10)

            box_id = "971725107197290|0C:56:5C:6D:D2:6A"
            # fetchtv.send_key(box_id, RemoteKey.PlayPause)
            # fetchtv.send_key(box_id, RemoteKey.PlayPause)

            # fetchtv.play_channel(box_id, 10264783)
            # fetchtv.play_channel(box_id, 30246952)

            box = fetchtv.get_box(box_id)
            fetchtv.get_epg()
            # box.send_key(RemoteKey.Stop)
            # print(box.to_dict())

            # box.update_media_state()

            # program = box.get_current_program()

            programs = fetchtv.find_program('hunted')
            programs = fetchtv.find_program('star trek')

            """
            box.record_program(box.state.channel_id, program.program_id, program.epg_program_id)

            time.sleep(10)
            recording = [rec.id for rec in box.recordings.future.values() if rec.program_id == program.program_id]

            box.cancel_recording(program.program_id)
            box.delete_recordings(recording)
            """
            time.sleep(10)

        finally:
            fetchtv.close()
