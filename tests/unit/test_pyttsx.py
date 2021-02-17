from unittest import TestCase
import time

import pyttsx3
from wiki_movie.utils import repository_root, make_directory


def localtime_filepath(directory, extension):
    """
    directory -- Path
    extension -- str

    return -- str
    """
    formatted_current_time = time.strftime('%H.%M.%S.%MS', time.localtime())
    return str(directory / str(formatted_current_time + '.' + extension))


class PyttsxTest(TestCase):
    def setUp(self):
        self.audio_dir = repository_root / 'tests' / 'data' / 'audio'
        make_directory(self.audio_dir)
        self.engine = pyttsx3.init()

    def test_say(self):
        text = 'Hello world'
        self.engine.say(text)
        self.engine.runAndWait()

    def test_save_to_aiff(self):
        text = 'If there is no audio after this sentence, the test failed. If hearing this then test passed.'
        file_path = localtime_filepath(self.audio_dir, 'aiff')
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()

    def test_save_to_mp3(self):
        text = 'If there is no audio after this sentence, the test failed. If hearing this then test passed.'
        file_path = localtime_filepath(self.audio_dir, 'mp3')
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()

    def test_save_to_wav(self):
        text = 'If there is no audio after this sentence, the test failed. If hearing this then test passed.'
        file_path = localtime_filepath(self.audio_dir, 'wav')
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()
