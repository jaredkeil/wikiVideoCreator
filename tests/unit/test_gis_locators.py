from unittest import TestCase, skip


from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from wiki_movie.image.google_images_locators import GoogleImagesLocators


class TestGisLocators(TestCase):
    def setUp(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

    @skip('Requires prior window scrolling to show More Results button')
    def test_more_results(self):
        self.driver.find_element(*GoogleImagesLocators.MORE_RESULTS).click()

    def test_fmt_image_search_url(self):
        url = GoogleImagesLocators.fmt_image_search_url('test this')
        self.driver.get(url)
