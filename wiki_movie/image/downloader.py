import os
from pathlib import Path
import sys
import logging
import urllib.request
import urllib.error
from urllib.parse import urlparse, quote

from user_agent import generate_user_agent
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import ElementNotInteractableException, \
    TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from wiki_movie.image.google_images_locators import GoogleImagesLocators
from wiki_movie.utils import write_seq_to_file, make_directory, file_len


class ImageDownloader:
    def __init__(self,
                 main_keyword,
                 supplemented_keywords=None,
                 url_dir=None,
                 img_dir=None,
                 num_requested=5,
                 connection_speed="medium",
                 headless=True):
        """
        Args:
            main_keyword (str): main keyword
            supplemented_keywords (list[str]): list of supplemented keywords
            url_dir (Path): parent directory where the url.txt files are stored
            img_dir (Path): parent directory where images will be downloaded
            num_requested (int): maximum number of images to download
            connection_speed (str): very slow, slow, medium, fast, or very fast
        """
        self.main_keyword = main_keyword
        self.supplemented_keywords = supplemented_keywords if supplemented_keywords else []
        self.url_dir = url_dir if url_dir else Path.cwd() / 'data' / 'url_files'
        self.img_dir = img_dir if img_dir else Path.cwd() / 'data' / 'images' / main_keyword
        self.num_requested = num_requested
        self.wait_time = {'very slow': 7,
                          'slow': 3,
                          'medium': 1,
                          'fast': 0.5,
                          'very fast': .25}.get(connection_speed, 1)
        self.headless = headless
        self.img_urls = set()
        self._boot_driver()

    def _boot_driver(self):
        options = Options()
        options.headless = self.headless
        self.driver = webdriver.Firefox(options=options)

    def find_and_download(self):
        self._get_image_links()
        self.driver.quit()
        self._download_images()

    def _get_image_links(self):
        self._create_directories()
        for keyword in self.supplemented_keywords:
            self._scrape_urls(keyword)

    def _scrape_urls(self, keyword):
        # Perform a google image search and load enough results
        self._search_for_images(keyword)

        thumbs = self._get_thumbnails()
        while len(thumbs) < self.num_requested:
            self._show_more_results()
            thumbs.update(self._get_thumbnails())

        # Scrape the 'src' attribute as a url from from thumbnails
        urls = self._get_urls_from_thumbs(list(thumbs))
        self.img_urls.update(urls)

        # write urls in appropriate text file, named by keyword
        link_file_path = self._define_link_file_path(keyword)
        write_seq_to_file(urls, link_file_path)
        print(f"Wrote {len(urls)} links to {link_file_path}\n")

    def _search_for_images(self, keyword):
        print(f'Searching for "{self.main_keyword + " " + keyword}"')
        formatted_query = quote(self.main_keyword + ' ' + keyword)
        self.driver.get("https://www.google.com/search?q=" + formatted_query
                        + "&source=lnms&tbm=isch")

    def _show_more_results(self):
        # Scroll, loading more image results. Click 'More results' if possible
        try:
            more_results_element = WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable(GoogleImagesLocators.MORE_RESULTS))
            more_results_element.click()
        except (TimeoutException, ElementNotInteractableException):
            pass

        self.driver.execute_script("window.scrollBy(0, 1000)")

    def _get_thumbnails(self):
        try:
            thumbnails = WebDriverWait(self.driver, 10).until(
                n_elements_clickable(GoogleImagesLocators.THUMBNAILS,
                                     self.num_requested)
            )
            return set(thumbnails)
        except TimeoutException:
            return set()

    def _get_urls_from_thumbs(self, thumbs):
        urls = set()
        n_found = 0
        i = 0
        while len(urls) < self.num_requested and i < len(thumbs):
            sys.stdout.write(
                f"Finding {self.num_requested} URL's "
                f"[{'#' * n_found + ' ' * (self.num_requested - n_found)}] \r")
            sys.stdout.flush()
            src = self._extract_src_from_thumb(thumbs[i])
            if src:
                urls.update(src)
                n_found += 1
            i += 1
        return urls

    def _extract_src_from_thumb(self, thumb):
        try:
            WebDriverWait(self.driver, self.wait_time).until(
                element_is_clickable(thumb)).click()
        except (TimeoutException, ElementNotInteractableException,
                ElementClickInterceptedException) as e:
            logging.error(f'Error clicking thumbnail: {e}')

        try:
            elements = self.driver.find_elements(
                *GoogleImagesLocators.URLS_IN_THUMBS)
            el = WebDriverWait(self.driver, self.wait_time).until(
                element_is_clickable(elements[1]))
            src = el.get_attribute('src')
            if src.startswith('http') and not src.startswith('https://encrypted-tbn0.gstatic.com'):
                return {src}
        except (IndexError, Exception) as e:
            logging.error(f'Error extracting "src" attribute: {e}')

        return set()

    def _define_link_file_path(self, keyword):
        if keyword == " ":
            return self.url_dir / f"{self.main_keyword}.txt"
        else:
            return self.url_dir / f"{keyword}.txt"

    def _define_supp_img_dir(self, keyword):
        if keyword == " ":
            return self.img_dir / self.main_keyword
        else:
            return self.img_dir / keyword

    def _create_directories(self):
        make_directory(self.url_dir)

    def _download_images(self):
        """download images whose links are in the link file"""
        # iterate through keywords
        for keyword in self.supplemented_keywords:
            sk_img_dir = self._define_supp_img_dir(keyword)
            make_directory(sk_img_dir)

            self.img_path = 0

            self._download_image_from_keyword(keyword)

            downloaded_num = len(os.listdir(sk_img_dir))
            print(f"\nSuccessfully downloaded {downloaded_num} images "
                  f"for search '{self.main_keyword + ' ' + keyword}'.\n")

    def _download_image_from_keyword(self, keyword):
        """
        Reads urls from '{keyword}.txt'.
        Downloads to images/main_keyword/supp_keyword/ directory
        """
        print(f"Downloading path: {self._define_supp_img_dir(keyword)}")

        link_file_path = self._define_link_file_path(keyword)
        n_links = file_len(link_file_path)

        with link_file_path.open('r') as rf:
            for i, link in enumerate(rf.readlines()):
                # print(link)
                sys.stdout.write(
                    f"Downloading {n_links} images "
                    f"[{'#' * (i + 1) + ' ' * (n_links - i - 1)}]   \r")
                sys.stdout.flush()
                self._get_link(link, keyword)

    def _get_link(self, link, keyword):
        try:
            self._save_link(link, keyword)
            self.img_path += 1
        except urllib.error.HTTPError as e:
            logging.error(f'HTTPError while downloading image {link}. '
                          f'http code {e.code}, reason:{e.reason}')
        except urllib.error.URLError as e:
            logging.error(f'URLError while downloading image {link}. '
                          f'Reason:{e.reason}')
        except Exception as e:
            logging.error(f'Unexpected error while downloading image {link}. '
                          f'error type:{e.args}')

    def _save_link(self, link, keyword):
        response = self._req_response(link)
        file_path = self._define_supp_img_dir(keyword) / f'{self.img_path}.jpg'
        with file_path.open('wb') as wf:
            wf.write(response.read())

    @staticmethod
    def _req_response(url):
        parsed = urlparse(url)
        headers = {
            'User-Agent': generate_user_agent(),
            'referer': parsed.scheme + '://' + parsed.hostname
        }  # ex. referer = 'https://www.google.com'
        req = urllib.request.Request(url.strip(), headers=headers)
        return urllib.request.urlopen(req, timeout=10)


class n_elements_clickable:
    """
    Check whether there are a certain number of elements found by the locator
    """
    def __init__(self, locator, n):
        self.locator = locator
        self.n = n

    def __call__(self, driver):
        elements = driver.find_elements(*self.locator)
        if len(elements) >= self.n:
            return elements
        else:
            return False


class element_is_clickable:
    """
    Expected condition which accepts an element rather than a locator
    """
    def __init__(self, element: WebElement):
        self.element = element

    def __call__(self, driver):
        # if self.element.is_displayed() and self.element.is_enabled():
        if self.element.is_displayed():
            return self.element
        else:
            return False


if __name__ == '__main__':
    from wiki_movie.utils import repository_root

    kw = 'Test'
    s_kw = [' ', 'Hello', 'There']

    data_dir = repository_root / 'data'
    txt_dir = data_dir / 'url_files' / kw
    images_dir = data_dir / 'images' / kw

    image_downloader = ImageDownloader(main_keyword=kw,
                                       supplemented_keywords=s_kw,
                                       url_dir=txt_dir,
                                       img_dir=images_dir)

    image_downloader.find_and_download()
