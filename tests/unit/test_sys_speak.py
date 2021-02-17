from unittest import TestCase, skipUnless
from sys import platform
import time

from wiki_movie.utils import repository_root
from wiki_movie.narrators.engines.sys_speak import save_linux, save_mac


def skip_platform_msg(req):
    return f'Test is {req} platform exclusive. Skipping because platform is {platform}'


class SysSpeakTest(TestCase):
    def setUp(self):
        self.audio_dir = repository_root / 'tests' / 'data' / 'audio'
        self.text_dir = repository_root / 'tests' / 'data' / 'text'

    @skipUnless(platform == 'darwin', skip_platform_msg('darwin'))
    def test_save_mac(self):
        file_path = self.audio_dir / 'test_save_mac.aiff'

        if file_path.exists():
            file_path.unlink()

        self.assertFalse(file_path.exists(),
                         'File should not exist or have been deleted by test suite before creation')

        save_mac(message='test', voice='Alex', file_name=str(file_path))

        self.assertTrue(file_path.exists(),
                        'File should have been created.')

    @skipUnless(platform == 'linux' or platform == 'linux2', skip_platform_msg('linux'))
    def test_save_linux(self):
        file_path = self.audio_dir / 'test_save_linux.wav'

        if file_path.exists():
            file_path.unlink()

        self.assertFalse(file_path.exists(),
                         'File should not exist or have been deleted by test suite before creation')

        save_linux(message='test', file_name=str(file_path))

        self.assertTrue(file_path.exists(),
                        'File should have been created.')

    @skipUnless(platform == 'darwin', skip_platform_msg('darwin'))
    def test_save_mac_no_filename(self):
        name = time.strftime("%H.%M.%S", time.localtime()) + '.aiff'
        file_path = repository_root / 'data' / 'audio' / 'untitled' / name

        if file_path.exists():
            file_path.unlink()

        self.assertFalse(file_path.exists(),
                         'File should not exist or have been deleted by test suite before creation')

        save_mac(message='test no filename')

        self.assertTrue(file_path.exists(),
                        f'File {file_path} should have been created.')

    @skipUnless(platform == 'darwin', skip_platform_msg('darwin'))
    def test_save_mac_text_file(self):
        file_path = self.audio_dir / 'test_save_mac_text_file.aiff'

        if file_path.exists():
            file_path.unlink()

        self.assertFalse(file_path.exists(),
                         'File should not exist or have been deleted by test suite before creation')

        text_file = str(self.text_dir / 'test_one_line.txt')
        save_mac(file=text_file, file_name=str(file_path))

        self.assertTrue(file_path.exists(),
                        'File should have been created.')

    @skipUnless(platform == 'darwin', skip_platform_msg('darwin'))
    def test_save_mac_multi_line_text_file(self):
        file_path = self.audio_dir / 'test_save_mac_multi_line_text_file.aiff'

        if file_path.exists():
            file_path.unlink()

        self.assertFalse(file_path.exists(),
                         'File should not exist or have been deleted by test suite before creation')

        text_file = str(self.text_dir / 'test_multi_line.txt')
        save_mac(file=text_file, file_name=str(file_path))

        self.assertTrue(file_path.exists(),
                        'File should have been created.')
