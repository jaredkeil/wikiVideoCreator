import importlib
import sys


class WikiMovie:
    def __init__(self, narrator_name='', narrator_args=None):
        if not narrator_name:
            if sys.platform == 'darwin':
                narrator_name = 'sys_tts'
            else:
                narrator_name = 'py_tts'

        if not narrator_args:
            narrator_args = {}

        module = importlib.import_module(f'wiki_movie.narrators.{narrator_name}')
        self.narrator = module.build_narrator(narrator_args)





    def make_movie(self):



        self.narrator.make_narration(self.script, self.audio_dir)
