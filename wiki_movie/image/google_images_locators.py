from selenium.webdriver.common.by import By
from urllib.parse import quote


class GoogleImagesLocators:
    MORE_RESULTS = By.XPATH, "//input[@value='Show more results']"
    THUMBNAILS = By.XPATH, '//a[@class="wXeWr islib nfEiy mM5pbd"]'
    URLS_IN_THUMBS = By.XPATH, '//img[@class="n3VNCb"]'

    @staticmethod
    def fmt_image_search_url(query):
        """
        Format query string into url for google image search.
        """
        return "https://www.google.com/search?q=" + \
               quote(query) + \
               "&source=lnms&tbm=isch"
