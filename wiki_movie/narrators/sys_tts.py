from wiki_movie.narrators.base_tts import BaseNarrator
from wiki_movie.narrators.engines import sys_tts


def build_narrator(**kwargs):
    return SystemNarrator(**kwargs)


class SystemNarrator(BaseNarrator):
    def __init__(self, script, voice, rate):
        self.voice = voice
        self.rate = rate
        self._save = sys_tts.save
        super().__init__(script)

    def _save_section(self, text, path):
        self._save(message=text, voice=self.voice, rate=self.rate, file_name=str(path))
