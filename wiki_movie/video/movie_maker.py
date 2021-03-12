import importlib
import sys
import argparse

from wikipediaapi import Wikipedia

from wiki_movie.image import ImageDownloader, resize_image_directory
from wiki_movie.text import generate_section_dictionaries_list
from wiki_movie.video.slideshow_functions import create_clip, add_outro, save_video
from wiki_movie import utils

W_API = Wikipedia('en')
DATA_DIR = utils.repository_root / 'data'
PLATFORM_AUDIO_EXT = utils.get_platform_audio_ext()
NARRATOR_FMTS = {'sys_tts': PLATFORM_AUDIO_EXT, 'py_tts': PLATFORM_AUDIO_EXT,
                 'google_tts': 'mp3', 'dc_tts': 'mp3'}


class WikiMovie:
    """
    Make movies in mp4 from wikipedia pages.
    """

    def __init__(self,
                 title,
                 narrator_name=None,
                 narrator_args=None,
                 downloader_args=None):
        """
        Initialization parses wikipedia api response into a readable script,
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

        narrator_module = importlib.import_module(
                            f'wiki_movie.narrators.{narrator_name}')
        self.narrator = narrator_module.build_narrator(self.script,
                                                       **narrator_args)

        # ImageDownloader setup
        self.img_dir = DATA_DIR / 'images' / title
        self.resize_dir = self.img_dir / 'resize'
        self.url_dir = DATA_DIR / 'url_files' / title

        keywords = [' '] + [s['title'] for s in self.script[1:] if s['text']]

        if not downloader_args:
            downloader_args = {}
        d_args = dict(main_keyword=title, supplemented_keywords=keywords,
                      url_dir=self.url_dir, img_dir=self.img_dir)
        d_args.update(downloader_args)

        self.image_downloader = ImageDownloader(**d_args)

        # Video setup
        self.vid_path = DATA_DIR / 'videos' / f'{title}.mp4'

    def make_movie(self, overwrite=True):
        if overwrite:
            self.prepare_images()
            self.narrator.make_narration(self.audio_dir)
            self.slideshow()
        else:
            print("Overwrite was set to False - No movie created.")

    def prepare_images(self):
        self.image_downloader.find_and_download()
        resize_image_directory(self.img_dir, self.resize_dir)

    def slideshow(self):
        clips = [create_clip(s['title'],
                             self.audio_dir,
                             self.resize_dir,
                             s['level'],
                             bool(s['text']),
                             self.fmt)
                 for s in self.script]
        video = add_outro(clips)
        save_video(clips=video, path=self.vid_path)

    def delete_assets(self):
        for _dir in self._directories:
            utils.rm_directory(_dir)

        self.vid_path.unlink()

    @property
    def _directories(self):
        return self.audio_dir, self.img_dir, self.url_dir


def main(args):
    movie = WikiMovie(title=args.title,
                      narrator_name=args.narrator,
                      narrator_args=parse_narrator_args(args),
                      downloader_args=parse_downloader_args(args))
    movie.make_movie()


def parse_narrator_args(args):
    kwargs = {}
    if args.voice:
        kwargs['voice'] = args.voice
    if args.rate:
        kwargs['rate'] = args.rate
    return kwargs


def parse_downloader_args(args):
    kwargs = {}
    if args.watch:
        kwargs['headless'] = False
    if args.image_count:
        kwargs['num_requested'] = args.image_count
    if args.connect_speed:
        kwargs['connection_speed'] = args.connect_speed
    return kwargs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Make movie from wikipedia article.")
    parser.add_argument('title', nargs='+', help='wikipedia article title')
    parser.add_argument('-n', '--narrator', choices=('sys_tts', 'google_tts', 'py_tts', 'dc_tts'),
                        help='text to speech method')

    tts_args = parser.add_argument_group('narrator arguments (optional)')
    tts_args.add_argument('-v', '--voice', help='voice of sys_tts - available voices dependant on platform')
    tts_args.add_argument('-r', '--rate', help='words per minute of sys_tts')

    img_dl_args = parser.add_argument_group('image downloader arguments (optional)')
    img_dl_args.add_argument('-i', '--image_count', type=int, help='how many images per section')
    img_dl_args.add_argument('-c', '--connect_speed', choices=('very slow', 'slow', 'medium', 'fast', 'very fast'),
                             help='how fast the webdriver clicks on search results')
    img_dl_args.add_argument('-w', '--watch', action='store_true', help='run browser in non-headless mode')

    options = parser.parse_args(['hello', '-v', 'somevoice', '-i', '10'])

    print(options)

    main(options)
