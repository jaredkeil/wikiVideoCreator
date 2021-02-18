from unittest import TestCase
from sys import platform

from wiki_movie.utils import repository_root, make_directory


class BaseEngineTest(TestCase):
    def setUp(self):
        self.audio_dir = repository_root / 'tests' / 'data' / 'audio'
        make_directory(self.audio_dir)


def skip_platform_msg(req):
    return f'Test is {req} platform exclusive. Skipping because platform is {platform}'
