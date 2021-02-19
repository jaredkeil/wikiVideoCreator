import importlib
import sys

from wikipediaapi import Wikipedia

from wiki_movie.image import ImageDownloader, resize_image_directory
from wiki_movie.text import generate_section_dictionaries_list
from wiki_movie.utils import repository_root, get_platform_audio_ext
from wiki_movie.video.slideshow_functions import create_clip, add_outro, save_video

W_API = Wikipedia('en')
DATA_DIR = repository_root / 'data'
NARRATOR_FMTS = {'sys_tts': get_platform_audio_ext(), 'py_tts': get_platform_audio_ext(),
                 'google_tts': 'mp3', 'dc_tts': 'mp3'}


class WikiMovie:
    def __init__(self, title, narrator_name=None, narrator_args=None, downloader_args=None,):
        """
        Initialization parses response of wikipedia api into a readable script for narrator,
        then initializes narrator and image downloader.

        Call WikiMovie().make_movie() to generate video output in .mp4 format.
        """

        # Script list setup
        self.title = title
        self.script = generate_section_dictionaries_list(W_API.page(title))

        # Narrator setup
        self.audio_dir = DATA_DIR / 'audio' / title
        if not narrator_name:
            if sys.platform == 'darwin':
                narrator_name = 'sys_tts'
            else:
                narrator_name = 'py_tts'

        if not narrator_args:
            narrator_args = {}

        self.fmt = NARRATOR_FMTS[narrator_name]

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

    def make_movie(self, overwrite_images=True, overwrite_speech=True, overwrite_video=True):
        if overwrite_images:
            self.prepare_images()
        if overwrite_speech:
            self.narrator.make_narration(self.audio_dir)
        if overwrite_video:
            self.slideshow()

    def prepare_images(self):
        self.image_downloader.find_and_download()
        resize_image_directory(self.img_dir, self.resize_dir)

    def slideshow(self):
        clips = [create_clip(s['title'], self.audio_dir, self.resize_dir, s['level'], bool(s['text']), self.fmt)
                 for s in self.script]
        video = add_outro(clips)
        save_video(clips=video, path=DATA_DIR / 'videos' / f'{self.title}.mp4')


if __name__ == '__main__':
    w_movie = WikiMovie('Condyle')
