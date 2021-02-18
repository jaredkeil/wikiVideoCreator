from unittest import skipUnless
from sys import platform

from wiki_movie.narrators.engines import pyttsx_
from tests.unit.engine_base import BaseEngineTest, skip_platform_msg


class PyttsxTest(BaseEngineTest):
    @skipUnless(platform == 'darwin', skip_platform_msg('darwin'))
    def test_save_mac(self):
        text = 'Basic test save mac.'
        file_path = self.audio_dir / 'test_pyttsx.aiff'

        if file_path.exists():
            file_path.unlink()

        self.assertFalse(file_path.exists())

        pyttsx_.save(text, str(file_path))

        self.assertTrue(file_path.exists())

    @skipUnless(platform == 'linux' or platform == 'linux2', skip_platform_msg('linux'))
    def test_save_linux(self):
        text = 'Basic test save linux.'
        file_path = self.audio_dir / 'test_pyttsx.wav'

        if file_path.exists():
            file_path.unlink()

        self.assertFalse(file_path.exists())

        pyttsx_.save(text, str(file_path))

        self.assertTrue(file_path.exists())

    def test_save_no_extension(self):
        text = 'No extension test save.'
        file_path = self.audio_dir / 'no_ext_pyttsx'

        ext = {'linux': '.wav', 'linux2': '.wav', 'darwin': '.aiff'}.get(platform, None)
        expected_create_path = file_path.with_suffix(ext)

        if expected_create_path.exists():
            expected_create_path.unlink()

        self.assertFalse(expected_create_path.exists())

        pyttsx_.save(text, str(file_path))

        self.assertTrue(expected_create_path.exists())

    def test_save_bad_extension(self):
        text = 'No extension test save.'
        file_path = self.audio_dir / 'no_ext_pyttsx.mp3'  # extension not expected by pyttsx3

        ext = {'linux': '.wav', 'linux2': '.wav', 'darwin': '.aiff'}.get(platform, None)
        if not ext:
            self.skipTest('Skipping bad extension test because platform is unsupported.')

        expected_create_path = file_path.with_suffix(ext)

        if expected_create_path.exists():
            expected_create_path.unlink()

        self.assertFalse(expected_create_path.exists())

        pyttsx_.save(text, str(file_path))

        self.assertTrue(expected_create_path.exists())
