from wiki_movie.narrators.base_tts import BaseNarrator
from wiki_movie.narrators.engines import py_tts


def build_narrator(**kwargs):
    return PyttsNarrator(**kwargs)


class PyttsNarrator(BaseNarrator):
    def __init__(self, script):
        self._save = py_tts.save
        super().__init__(script)

    def _save_section(self, text, path):
        self._save(text=text, file_name=str(path))
