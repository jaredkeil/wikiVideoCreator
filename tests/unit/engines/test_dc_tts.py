from unittest import SkipTest

from tests.unit.engines.engine_base import BaseEngineTest

try:
    from wiki_movie.narrators.engines import dc_tts
except ImportError:
    raise SkipTest('Missing needed packages (probably Tensorflow) for dc_tts engine')


class DcttsEngineTest(BaseEngineTest):
    def test_save(self):
        pass