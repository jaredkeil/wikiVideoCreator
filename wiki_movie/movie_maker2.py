import importlib
import sys

from wikipediaapi import Wikipedia

from wiki_movie.text import generate_script_list
from wiki_movie.utils import repository_root
from wiki_movie.image_downloader import ImageDownloader

w_api = Wikipedia('en')


class WikiMovie:
    def __init__(self, title, narrator_name='', narrator_args=None, downloader_args=None):
        self.title = title
        self.script = generate_script_list(w_api.page(title))

        # Set up narrator
        if not narrator_name:
            if sys.platform == 'darwin':
                narrator_name = 'sys_tts'
            else:
                narrator_name = 'py_tts'

        if not narrator_args:
            narrator_args = {}

        module = importlib.import_module(f'wiki_movie.narrators.{narrator_name}')
        self.narrator = module.build_narrator(self.script, narrator_args)

        # Set up image downloader
        keywords = [' '] + [sd['title'] for sd in self.script[1:] if sd['text']]
        _dir = repository_root / 'data'

        if not downloader_args:
            downloader_args = {}

        d_args = dict(main_keyword=title, supplemented_keywords=keywords,
                      url_dir=_dir / 'url_files', img_dir=_dir / 'images')
        d_args.update(downloader_args)

        self.image_downloader = ImageDownloader(**d_args)

    def make_movie(self):

        self.narrator.make_narration(self.script, self.audio_dir)
