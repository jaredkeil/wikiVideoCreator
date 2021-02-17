from unittest import TestCase
from pathlib import Path

from wiki_movie.image_downloader2 import ImageDownloader
from wiki_movie.utils import repository_root


class ImageDownloaderTest(TestCase):
    def setUp(self):
        self.main_keyword = 'python'
        self.supp_list = ['small', 'big', 'red']
        data_dir = repository_root / 'tests'
        self.url_dir = data_dir / 'url_files'
        self.img_dir = data_dir / 'images'
        self.num_req = 10
        self.speed = 'medium'
        self.headless = False

    def _standard_image_downloader(self):
        return ImageDownloader(self.main_keyword,
                               self.supp_list,
                               self.url_dir,
                               self.img_dir,
                               self.num_req,
                               self.speed,
                               self.headless)

    def test_create_image_downloader(self):
        image_downloader = self._standard_image_downloader()
        self.assertEqual(1, image_downloader.wait_time)

    def test_headless(self):
        self.headless = True
        image_downloader = self._standard_image_downloader()
        self.assertEqual(True, image_downloader.headless)

    def test_image_links(self):
        image_downloader = self._standard_image_downloader()


