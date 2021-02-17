from selenium.webdriver.common.by import By


class GoogleImagesLocators:
    MORE_RESULTS = By.XPATH, "//input[@value='Show more results']"
    THUMBNAILS = By.XPATH, '//a[@class="wXeWr islib nfEiy mM5pbd"]'
    URLS_IN_THUMBS = By.XPATH, '//img[@class="n3VNCb"]'
