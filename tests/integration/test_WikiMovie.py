from unittest import TestCase, mock

from wiki_movie.video import WikiMovie
from wiki_movie.video.movie_maker import DATA_DIR


class WikiMovieTest(TestCase):
    def setUp(self):
        self.w_movie = WikiMovie('Condyle')

    def test_skip_overwrite_images(self):
        img_dl = self.w_movie.image_downloader
        with mock.patch.object(img_dl, 'find_and_download') as fd:
            self.w_movie.make_movie(overwrite=False)
            fd.assert_not_called()

    def test_skip_overwrite_speech(self):
        narrator = self.w_movie.narrator
        with mock.patch.object(narrator, 'make_narration') as mn:
            self.w_movie.make_movie(overwrite=False)
            mn.assert_not_called()

    def test_skip_overwrite_video(self):
        with mock.patch('wiki_movie.video.slideshow_functions.save_video') as sv:
            self.w_movie.make_movie(overwrite=False)
            sv.assert_not_called()

    @mock.patch('sys.platform', 'linux')
    def test_linux_format(self):
        w_movie = WikiMovie('Condyle', 'sys_tts')

        # Mocked methods to increase speed of test. Only care about correct call to default linux narration engine
        w_movie.prepare_images = mock.MagicMock(name='prepare_images')
        w_movie.slideshow = mock.MagicMock(name='slideshow')

        with mock.patch('wiki_movie.narrators.engines.sys_tts.save_linux') as mock_save_linux:
            w_movie.make_movie()

            expected_file_name = str(DATA_DIR / 'audio' / 'Condyle' / 'Condyle_header')

            mock_save_linux.assert_called()
            mock_save_linux.assert_any_call(message='Condyle', voice='', rate='', file_name=expected_file_name)

