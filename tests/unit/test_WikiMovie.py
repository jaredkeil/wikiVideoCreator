from unittest import TestCase, mock, skipUnless
import pkgutil

from wiki_movie.video.movie_maker2 import WikiMovie
from wiki_movie.utils import repository_root


class WikiMovieTest(TestCase):
    @mock.patch('sys.platform', 'darwin')
    def test_create_darwin_platform_default_narrator(self):
        w_movie = WikiMovie(title='Test')
        narrator_cls_name = w_movie.narrator.__class__.__name__
        self.assertEqual('SystemNarrator', narrator_cls_name)

    @mock.patch('sys.platform', 'linux')
    @skipUnless(pkgutil.find_loader('pyttsx3'), 'pyttsx3 not installed')
    def test_create_other_platform_default_narrator(self):
        w_movie = WikiMovie(title='Test')
        narrator_cls_name = w_movie.narrator.__class__.__name__
        self.assertEqual('PyttsNarrator', narrator_cls_name)

    @skipUnless(pkgutil.find_loader('tensorflow'), 'Tensorflow not installed')
    def test_create_with_narrator_name(self):
        w_movie = WikiMovie(title='Test', narrator_name='dc_tts')
        narrator_cls_name = w_movie.narrator.__class__.__name__
        self.assertEqual('DcttsNarrator', narrator_cls_name)

    def test_create_default_downloader(self):
        w_movie = WikiMovie(title='Test')
        downloader = w_movie.image_downloader

        actual_keywords = [' ', 'Arts and entertainment', 'Computing', 'People', 'Science and technology', 'Sports', 'Other uses']

        self.assertEqual(downloader.main_keyword, 'Test', 'Incorrect main keyword')
        self.assertEqual(downloader.url_dir, repository_root / 'data' / 'url_files', 'Incorrect url directory')
        self.assertListEqual(downloader.supplemented_keywords, actual_keywords, 'Incorrect keyword list')

    def test_pass_downloader_args(self):
        w_movie = WikiMovie(title='Test',
                            downloader_args={'img_dir': 'test_path',
                                             'supplemented_keywords': ['1', '2', '3']
                                             }
                            )
        downloader = w_movie.image_downloader


        self.assertEqual(downloader.img_dir, 'test_path')
        self.assertEqual(downloader.main_keyword, 'Test')
        self.assertListEqual(downloader.supplemented_keywords, ['1', '2', '3'])
