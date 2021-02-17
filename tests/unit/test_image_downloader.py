from unittest import TestCase

from wiki_movie.image_downloader2 import ImageDownloader


class ImageDownloaderTest(TestCase):
    def setUp(self):
        self.main_keyword = 'python'
        self.supp_list = []


    def test_create_image_downloader(self):
        image_downloader = ImageDownloader(self.main_keyword,
                                           self.supp_list)
