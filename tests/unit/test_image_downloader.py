from unittest import TestCase, skipIf
import pytest

from unittest.mock import patch
import os

from wiki_movie.image.downloader import ImageDownloader
from wiki_movie.utils import repository_root, file_len


class ImageDownloaderTest(TestCase):
    def setUp(self):
        self.main_keyword = 'python'
        self.supp_list = ['small', 'big', 'red']
        self.data_dir = repository_root / 'tests' / 'data'
        self.url_dir = self.data_dir / 'url_files' / self.main_keyword
        self.img_dir = self.data_dir / 'images' / self.main_keyword
        self.num_req = 3
        self.speed = 'medium'
        self.headless = True
        self.image_downloader = None

    def tearDown(self):
        if hasattr(self.image_downloader, 'driver'):
            print('closing driver')
            self.image_downloader.driver.close()
            self.image_downloader.driver.quit()

    def _standard_image_downloader(self):
        return ImageDownloader(self.main_keyword,
                               self.supp_list,
                               self.url_dir,
                               self.img_dir,
                               self.num_req,
                               self.speed,
                               self.headless)

    @skipIf(os.environ.get('DISPLAY') is None, '$DISPLAY not configured')
    def test_non_headless(self):
        self.headless = False
        self.image_downloader = self._standard_image_downloader()
        self.assertEqual(1, self.image_downloader.wait_time,
                         '"medium" connection speed not setting proper wait_time of 1 second.')

    def test_headless(self):
        self.image_downloader = self._standard_image_downloader()
        self.assertEqual(True, self.image_downloader.headless)

    def test_search_for_images(self):
        self.image_downloader = self._standard_image_downloader()
        keyword = self.supp_list[0]
        self.image_downloader._search_for_images(keyword=keyword)

    @pytest.mark.slow
    def test_get_image_links(self):
        self.num_req = 10
        self.headless = True
        self.speed = 'medium'
        self.image_downloader = self._standard_image_downloader()

        self.assertEqual(1, self.image_downloader.wait_time)

        self.image_downloader._get_image_links()

        n_link = len(list(self.image_downloader.url_dir.glob('*.txt')))
        self.assertEqual(n_link, len(self.supp_list),
                         'Incorrect number of url text files created.')

    def test_download_images(self):
        # check that ImageDownloader._get_link() is called correct number of times
        self.num_req = 2
        self.main_keyword = 'test'
        self.supp_list = ['1', '2']
        self.url_dir = self.data_dir / 'url_files' / self.main_keyword
        image_downloader = self._standard_image_downloader()

        expected_n_calls = sum(file_len(x) for x in image_downloader.url_dir.glob('*.txt'))
        with patch.object(image_downloader, '_get_link', return_value=None) as mock_get_link:
            image_downloader._download_images()
            self.assertEqual(expected_n_calls, mock_get_link.call_count,
                             'Incorrect number of calls to _get_link()')
            image_downloader.driver.quit()

    # slow
    def test_find_and_download(self):
        self.num_req = 2
        self.speed = 'fast'
        image_downloader = self._standard_image_downloader()
        image_downloader.find_and_download()
        image_downloader.driver.quit()
