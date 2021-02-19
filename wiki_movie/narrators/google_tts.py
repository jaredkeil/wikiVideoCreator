from wiki_movie.narrators.base_tts import BaseNarrator
from wiki_movie.narrators.engines import google_tts


def build_narrator(*args, **kwargs):
    return GttsNarrator(*args, **kwargs)


class GttsNarrator(BaseNarrator):
    def __init__(self, script, *args, **kwargs):
        self._save = google_tts.save
        super().__init__(script)

    def _save_section(self, text, path):
        self._save(text=text, file_name=str(path))
