from wiki_movie.narrators.base import BaseNarrator
from wiki_movie.narrators.engines import sys_speak


class SystemNarrator(BaseNarrator):
    def __init__(self, script, voice, rate):
        self.voice = voice
        self.rate = rate
        self._save = sys_speak.save
        super().__init__(script)

    def _save_section(self, text, path):
        self._save(message=text,
                   voice=self.voice,
                   rate=self.rate,
                   file_name=str(path))
