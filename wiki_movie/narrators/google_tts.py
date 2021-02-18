from wiki_movie.narrators.base_tts import BaseNarrator
from wiki_movie.narrators.engines import google_tts


def build_narrator(**kwargs):
    return GttsNarrator(**kwargs)


class GttsNarrator(BaseNarrator):
    def __init__(self, script):
        self._save = google_tts.save
        super().__init__(script)

    def _save_section(self, text, path):
        self._save(text=text, file_name=str(path))