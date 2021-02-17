from unittest import TestCase
from unittest.mock import patch
from pathlib import Path
import os

from wiki_movie.image_downloader2 import ImageDownloader
from wiki_movie.utils import repository_root, file_len


class ImageDownloaderTest(TestCase):
    def setUp(self):
        self.main_keyword = 'python'
        self.supp_list = ['small', 'big', 'red']
        data_dir = repository_root / 'tests' / 'data'
        self.url_dir = data_dir / 'url_files'
        self.img_dir = data_dir / 'images' / self.main_keyword
        self.num_req = 10
        self.speed = 'medium'
        self.headless = True
        self.image_downloader = None

    def tearDown(self):
        if hasattr(self.image_downloader, 'driver'):
            self.image_downloader.driver.quit()

    def _standard_image_downloader(self):
        return ImageDownloader(self.main_keyword,
                               self.supp_list,
                               self.url_dir,
                               self.img_dir,
                               self.num_req,
                               self.speed,
                               self.headless)

    def test_create_image_downloader(self):
        self.headless = False
        self.image_downloader = self._standard_image_downloader()
        self.assertEqual(1, self.image_downloader.wait_time,
                         '"medium" connection speed not setting proper wait_time of 1 second.')
        self.image_downloader.driver.close()

    def test_headless(self):
        self.image_downloader = self._standard_image_downloader()
        self.assertEqual(True, self.image_downloader.headless)

    def test_search_for_images(self):
        self.headless = False
        self.image_downloader = self._standard_image_downloader()
        keyword = self.supp_list[0]
        self.image_downloader._search_for_images(keyword=keyword)

    def test_get_image_links(self):
        self.num_req = 2
        self.image_downloader = self._standard_image_downloader()
        self.image_downloader._get_image_links()

        n_link = len(os.listdir(self.image_downloader.mk_url_dir))
        self.assertEqual(n_link, len(self.supp_list),
                         'Incorrect number of url text files created.')

    def test_download_images(self):
        # check that ImageDownloader._get_link() is called correct number of times
        self.num_req = 2
        image_downloader = self._standard_image_downloader()

        expected_n_calls = sum(file_len(x) for x in image_downloader.mk_url_dir.glob('*.txt'))
        with patch.object(image_downloader, '_get_link', return_value=None) as mock_get_link:
            image_downloader._download_images()
            self.assertEqual(expected_n_calls, mock_get_link.call_count,
                             'Incorrect number of calls to _get_link()')
