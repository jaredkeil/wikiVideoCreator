# -*- coding: utf-8 -*-
# @Author: WuLC
# @Date:   2017-09-27 23:02:19
# @Last Modified by:   JUSTINPAULTURNER
# @Last Modified time: 2020-04-10 08:56:28


####################################################################################################################
# Download images from google with specified keywords for searching
# search query is created by "main_keyword + supplemented_keyword"
# if there are multiple keywords, each main_keyword will join with each supplemented_keyword
# Use selenium and urllib, and each search query will download any number of images that google provides
# allow single process or multiple processes for downloading
# Pay attention that since selenium is used, geckodriver and firefox browser is required
####################################################################################################################

import os
from pathlib import Path
import sys
import time
import math
import logging
import urllib.request
import urllib.error
from urllib.parse import urlparse, quote

from user_agent import generate_user_agent
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchAttributeException, ElementNotInteractableException

from wiki_movie.image.google_images_locators import GoogleImagesLocators
from wiki_movie.utils import write_seq_to_file, make_directory, file_len


class ImageDownloader:
    def __init__(self, main_keyword, supplemented_keywords, url_dir, img_dir,
                 num_requested=5, connection_speed="medium", headless=True):
        """
        Args:
            main_keyword (str): main keyword
            supplemented_keywords (list[str]): list of supplemented keywords
            url_dir (Path): parent directory where the url.txt files are stored to folder called <main_keyword>
            img_dir (Path): parent directory where images will be downloaded to folder called <main_keyword>
            num_requested (int, optional): maximum number of images to download
            connection_speed (str, optional): 'very slow', 'slow', 'medium', 'fast', or 'very fast'
        """
        self.main_keyword = main_keyword
        self.supplemented_keywords = supplemented_keywords
        self.url_dir = url_dir
        self.mk_url_dir = url_dir / main_keyword
        self.img_dir = img_dir
        self.num_requested = num_requested
        self.wait_time = {'very slow': 7, 'slow': 3, 'medium': 1, 'fast': 0.5, 'very fast': .25}.get(connection_speed, 1)
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
        self._show_more_results()

        thumbs = self._get_thumbnails()

        # Scrape the urls from thumbnails
        urls = self._get_urls_from_thumbs(thumbs)
        self.img_urls.update(urls)

        # write urls in appropriate text file, named by keyword
        link_file_path = self._define_link_file_path(keyword)
        write_seq_to_file(urls, link_file_path)

    def _search_for_images(self, keyword):
        formatted_query = quote(self.main_keyword + ' ' + keyword)
        self.driver.get("https://www.google.com/search?q=" + formatted_query + "&source=lnms&tbm=isch")

    def _show_more_results(self):
        """Scroll down the page to load more image results."""
        for _ in range(math.ceil(self.num_requested / 700)):
            for __ in range(2):
                self.driver.execute_script("window.scrollBy(0, 1000000)")
                time.sleep(2)
            time.sleep(1)
            try:
                self.driver.find_element(*GoogleImagesLocators.MORE_RESULTS).click()
            except ElementNotInteractableException:
                break

    def _get_thumbnails(self):
        return self.driver.find_elements(*GoogleImagesLocators.THUMBNAILS)

    def _get_urls_from_thumbs(self, thumbs):
        urls = set()
        for i, t in enumerate(thumbs[:self.num_requested]):
            sys.stdout.write(f"Finding URL's [{'#' * (i + 1) + ' ' * (self.num_requested - i - 1)}]   \r")
            sys.stdout.flush()
            urls.update(self._extract_url_from_thumb(t))
        return urls

    def _extract_url_from_thumb(self, thumb):
        try:
            thumb.click()
            time.sleep(self.wait_time)
        except ElementNotInteractableException:
            print("Error clicking one thumbnail")

        src_urls = set()
        for el in self.driver.find_elements(*GoogleImagesLocators.URLS_IN_THUMBS):
            try:
                url = el.get_attribute('src')
                if url.startswith('http') and not url.startswith('https://encrypted-tbn0.gstatic.com'):
                    src_urls.add(url)
            except NoSuchAttributeException:
                print("Error getting one url")
        return src_urls

    def _define_link_file_path(self, keyword):
        if keyword == " ":
            return self.url_dir / f"{self.main_keyword + '/' + self.main_keyword}.txt"
        else:
            return self.url_dir / f"{self.main_keyword + '/' + keyword}.txt"

    def _define_supp_img_dir(self, keyword):
        if keyword == " ":
            return self.img_dir / self.main_keyword
        else:
            return self.img_dir / keyword

    def _create_directories(self):
        make_directory(self.url_dir)
        make_directory(self.mk_url_dir)

    def _download_images(self):
        """download images whose links are in the link file"""
        # iterate through keywords
        for keyword in self.supplemented_keywords:
            sk_img_dir = self._define_supp_img_dir(keyword)
            make_directory(sk_img_dir)
            self.img_path = 0
            self._download_image_from_keyword(keyword)

            downloaded_num = os.stat(sk_img_dir).st_nlink
            print(f"\nSuccessfully downloaded {downloaded_num} images for keyword '{keyword}'.")

    def _download_image_from_keyword(self, keyword):
        print(f"starting download of images inside directory {keyword}")

        link_file_path = self._define_link_file_path(keyword)
        n_links = file_len(link_file_path)

        with link_file_path.open('r') as rf:
            for i, link in enumerate(rf.readlines()):
                print(link)
                sys.stdout.write(
                    f"Downloading images [{'#' * (i + 1) + ' ' * (n_links - i - 1)}]   \r")
                sys.stdout.flush()
                self._get_link(link, keyword)

    def _get_link(self, link, keyword):
        try:
            self._save_link(link, keyword)
            self.img_path += 1
        except urllib.error.HTTPError as e:
            logging.error(f'HTTPError while downloading image {link}. http code {e.code}, reason:{e.reason}')
        except urllib.error.URLError as e:
            logging.error(f'URLError while downloading image {link}. Reason:{e.reason}')
        except Exception as e:
            logging.error(f'Unexpected error while downloading image {link}. error type:{e.args}')

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
            'referer': parsed.scheme + '://' + parsed.hostname  # ex. referer = 'https://www.google.com'
        }
        req = urllib.request.Request(url.strip(), headers=headers)
        return urllib.request.urlopen(req, timeout=10)
