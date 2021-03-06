import time
import os
from unittest import skip
import pytest

import pyttsx3
from wiki_movie.utils import localtime_filepath
from tests.unit.engines.engine_base import BaseEngineTest


class Pyttsx3Test(BaseEngineTest):
    def setUp(self):
        super().setUp()
        self.engine = pyttsx3.init()

    @skip('Sound card verification is not implemented yet.')
    def test_say(self):
        text = 'Hello world'
        self.engine.say(text)
        self.engine.runAndWait()

    @pytest.mark.timeout(1)
    def test_save_to_aiff(self):
        text = 'If there is no audio after this sentence, the test failed. ' \
               'If hearing this then test passed.'
        file_path = localtime_filepath(self.audio_dir, 'aiff')
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()

    @pytest.mark.timeout(1)
    def test_save_to_mp3(self):
        text = 'If there is no audio after this sentence, the test failed. If hearing this then test passed.'
        file_path = localtime_filepath(self.audio_dir, 'mp3')
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()

    @pytest.mark.timeout(1)
    def test_save_to_wav(self):
        text = 'If there is no audio after this sentence, the test failed. If hearing this then test passed.'
        file_path = localtime_filepath(self.audio_dir, 'wav')
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()

    @skip('Skip because timeout is likely')
    def test_save_with_wait(self):
        text = 'If there is no audio after this sentence, the test failed. If hearing this then test passed.'
        text = ' '.join(text + f' {i} loops complete.' for i in range(5))

        file_path = localtime_filepath(self.audio_dir, 'aiff')
        print(file_path)
        print(list(os.listdir(self.audio_dir)))

        while not os.path.exists(file_path):
            val = self.engine.save_to_file(text, file_path)
            print('val', val)
            time.sleep(2)
            res = self.engine.runAndWait()
            print('res', res)
            time.sleep(2)
