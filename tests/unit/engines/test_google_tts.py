from wiki_movie.narrators.engines import google_tts
from tests.unit.engines.engine_base import BaseEngineTest


class googleTTSTest(BaseEngineTest):
    def test_save(self):
        text = 'This is a test.'
        file_path = self.audio_dir / 'gtts_test_save.mp3'

        if file_path.exists():
            file_path.unlink()

        self.assertFalse(file_path.exists())

        google_tts.save(text, str(file_path))

        self.assertTrue(file_path.exists())

    def test_save_path_without_extension(self):
        text = 'This is a test save without extension.'
        file_path = self.audio_dir / 'gtts_test_save_no_extension'

        expected_create_path = file_path.with_suffix('.mp3')

        if expected_create_path.exists():
            expected_create_path.unlink()

        self.assertFalse(expected_create_path.exists())

        google_tts.save(text, str(file_path))

        self.assertTrue(expected_create_path.exists())
