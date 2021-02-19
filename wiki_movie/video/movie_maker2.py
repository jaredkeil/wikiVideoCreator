import importlib
import sys

from wikipediaapi import Wikipedia

from wiki_movie.image import ImageDownloader, resize_image_directory
from wiki_movie.text import generate_section_dictionaries_list
from wiki_movie.utils import repository_root
from wiki_movie.video.slideshow_functions import create_clip, add_outro, save_video

W_API = Wikipedia('en')
DATA_DIR = repository_root / 'data'


class WikiMovie:
    def __init__(self, title, narrator_name=None, narrator_args=None, downloader_args=None):
        # Script list setup
        self.title = title
        self.script = generate_section_dictionaries_list(W_API.page(title))

        # Narrator setup
        self.audio_dir = DATA_DIR / 'audio' / title
        if not narrator_name:
            if sys.platform == 'darwin':
                narrator_name = 'sys_tts'
                self.fmt = 'aiff'
            else:
                narrator_name = 'py_tts'
                self.fmt = 'wav'

        if not narrator_args:
            narrator_args = {}

        narrator_module = importlib.import_module(f'wiki_movie.narrators.{narrator_name}')
        self.narrator = narrator_module.build_narrator(self.script, **narrator_args)

        # ImageDownloader setup
        self.img_dir = DATA_DIR / 'images' / title
        self.resize_dir = self.img_dir / 'resize'

        keywords = [' '] + [s['title'] for s in self.script[1:] if s['text']]

        if not downloader_args:
            downloader_args = {}
        d_args = dict(main_keyword=title, supplemented_keywords=keywords,
                      url_dir=DATA_DIR / 'url_files', img_dir=self.img_dir)
        d_args.update(downloader_args)

        self.image_downloader = ImageDownloader(**d_args)

    def make_movie(self):
        self.prepare_images()
        self.narrator.make_narration(self.audio_dir)
        self.slideshow()

    def prepare_images(self):
        self.image_downloader.find_and_download()
        resize_image_directory(self.img_dir, self.resize_dir)

    def slideshow(self):
        clips = [create_clip(s['title'], self.audio_dir, self.resize_dir, s['level'], bool(s['text']), self.fmt)
                 for s in self.script]
        clips = add_outro(clips)
        save_video(clips, DATA_DIR / 'videos' / f'{self.title}.mp4')


if __name__ == '__main__':
    WikiMovie('Condyle').make_movie()
