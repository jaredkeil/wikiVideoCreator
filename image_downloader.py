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
import json
import time
from math import ceil
import logging
import urllib.request
import urllib.error
from urllib.parse import urlparse, quote
import wikipediaapi

from multiprocessing import Pool
from user_agent import generate_user_agent
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1 # I will be the index of the last line. 1 is added to account for the folder of resized images.

def get_image_links(main_keyword, supplemented_keywords, url_dir, num_requested = 20, connection_speed = "medium"):
    """get image links with selenium
    
    Args:
        main_keyword (str): main keyword
        url_dir (Path): 
        supplemented_keywords (list[str]): list of supplemented keywords
        link_file_path (str): path of the file to store the links
        num_requested (int, optional): maximum number of images to download
    
    Returns:
        list of url link_file_paths (Path): # still need to integrate 
    """
    number_of_scrolls = ceil(num_requested/700) #Set number of times to scroll
    # 700 is currently arbitrary. It is an attempt to limit the images loaded.
    
    # Setting the wait time based on the set connection speed
    if connection_speed == "very slow":
        wait_time = 7
    elif connection_speed == "slow":
        wait_time = 3
    elif connection_speed == "medium":
        wait_time = 1
    elif connection_speed == "fast":
        wait_time = .5
    elif connection_speed == "very fast":
        wait_time = .25
        
    # Set current working directory
    p = Path(os.getcwd())
    mk_url_dir = url_dir / main_keyword

    driver = webdriver.Firefox()
    for ind, keyword in enumerate(supplemented_keywords):
        img_urls = set()
        search_query = quote(main_keyword + ' ' + keyword)
        url = "https://www.google.com/search?q="+search_query+"&source=lnms&tbm=isch"
        driver.get(url)
        for _ in range(number_of_scrolls): # Scroll down page
            for __ in range(2):
                # multiple scrolls needed to show all images
                driver.execute_script("window.scrollBy(0, 1000000)")
                time.sleep(2)
            # to load next images
            time.sleep(1)
            try:
                driver.find_element_by_xpath("//input[@value='Show more results']").click()
            except Exception as e:
                print(f"Process {main_keyword} reached the end of page")
                break

        thumbs = driver.find_elements_by_xpath('//a[@class="wXeWr islib nfEiy mM5pbd"]')

        # print(f"Number of thumbnails on screen: {len(thumbs)}") # Optional
        
        for i, thumb in enumerate(thumbs[:num_requested]):
            sys.stdout.write(f"Finding URL's [{'#' * (i+1) + ' ' * (num_requested - i -1)}]   \r")
            sys.stdout.flush() 
            try:
                thumb.click()
                time.sleep(wait_time) # This is wait time for the image to load in it's higher resolution so that the URL can be retrieved
            except e:
                print("Error clicking one thumbnail")

            url_elements = driver.find_elements_by_xpath('//img[@class="n3VNCb"]')
            for url_element in url_elements:
                try:
                    url = url_element.get_attribute('src')
                except e:
                    print("Error getting one url")

                if url.startswith('http') and not url.startswith('https://encrypted-tbn0.gstatic.com'):
                    img_urls.add(url)
        
            # Create URL file directories
            if not url_dir.exists():
                url_dir.mkdir()
                print(url_dir, "directory created")
            elif url_dir.exists():
                print(url_dir, "exists")
            
            # Create main keyowrd url directory
            if not mk_url_dir.exists():
                mk_url_dir.mkdir()
                print(url_dir, "directory created")
            elif mk_url_dir.exists():
                print(mk_url_dir, "exists")

            # Defining link file path    
            if keyword != " ":
                fname = f"{main_keyword + '/' + keyword}.txt"
            elif keyword == " ":
                fname = f"{main_keyword + '/' + main_keyword}.txt"
            link_file_path = url_dir / fname
            if not link_file_path.exists():
                link_file_path.touch(mode=0o777)
                print(f"Made file {link_file_path}")
            
            # Saving url links in file
            with link_file_path.open('w') as wf:
                for url in img_urls:
                    # print(url)
                    wf.write(url +'\n')

        print(f'\nStored {len(img_urls)} links in {link_file_path}')
    
    driver.quit()


def download_images(main_keyword, supplemented_keywords, url_dir, img_dir):
    """download images whose links are in the link file
    
    Args:
        main_keyword (str): main keyword used previously by get_image_links
        supplemented_keywords lst(str): supplimental keywords used in the previous image search
        link_file_path (Path): path of directory which contains image URL .txt files
        url_dir (Path): directory where the url.txt files are stored
        img_dir (Path): directory to store the downloaded images

    Returns:
        None
    """
    # Creating paths reletive to this file's location
    p = Path(__file__).resolve().parents[0]
    # mk_img_dir = p / img_dir / main_keyword

    
    # Creating file paths to save images to

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    
    for ind, s_keyword in enumerate(supplemented_keywords):

        link_file_path = url_dir / main_keyword / f"{s_keyword}.txt" # sets the path to the url file to access 
        sk_img_dir = img_dir / s_keyword # sets the path to the direstory on where to save images to

        # Creates directory to save supplimental keywords to
        if not os.path.exists(sk_img_dir):
            os.makedirs(sk_img_dir)

        print("starting download of images inside directory {s_keyword}") # Terminal message
        
        count = 0 # Used as the name the image title when saved
        headers = {} # Used by selenium 
        
        # start to download images
        
        with link_file_path.open('r') as rf:
            for i, link in enumerate(rf.readlines()):
                print(link)
                sys.stdout.write(f"Downloading images [{'#' * (i+1) + ' ' * (file_len(link_file_path) - i -1)}]   \r")
                sys.stdout.flush() 
                try:
                    o = urlparse(link)
                    ref = o.scheme + '://' + o.hostname
                    #ref = 'https://www.google.com'
                    ua = generate_user_agent()
                    headers['User-Agent'] = ua
                    headers['referer'] = ref
                    # print(f'\n{link.strip()}\n{ref}\n{ua}')
                    req = urllib.request.Request(link.strip(), headers = headers)
                    response = urllib.request.urlopen(req)
                    data = response.read()
                    file_path = sk_img_dir / f'{count}.jpg'
                    with file_path.open('wb') as wf:
                        wf.write(data)
                    # print(f'Process-{main_keyword} download image {main_keyword}/{count}.jpg')
                    count += 1
                    if count % 10 == 0:
                        #print(f'Process-{main_keyword} is sleeping')
                        time.sleep(5)

                except urllib.error.URLError as e:
                    print('URLError')
                    logging.error(f'URLError while downloading image {link}reason:{e.reason}')
                    continue
                except urllib.error.HTTPError as e:
                    print('HTTPError')
                    logging.error(f'HTTPError while downloading image {link}http code {e.code}, reason:{e.reason}')
                    continue
                except Exception as e:
                    print('Unexpected Error')
                    logging.error(f'Unexpeted error while downloading image {link}error type:{e.args}')
                    continue
            downloaded_num = os.stat(sk_img_dir).st_nlink 
            print(f"\nSuccessfully downloaded {downloaded_num} images")
                
def master_download(main_keyword, supplemented_keywords, url_dir,  img_dir, num_requested = 20, connection_speed = "medium"):
    """
    Retrieve image URLs and download, in two step process.

    Args:
        main_keyword (str): Keyword to search google with
        url_dir: directory to store the generated .txt file containing list of image URLs
        img_dir: parent directory to store the downloaded images
    Returns:
        None
    """
    get_image_links(main_keyword, supplemented_keywords, url_dir, num_requested = num_requested, connection_speed = connection_speed)
    download_images(main_keyword, supplemented_keywords, url_dir, img_dir)


if __name__ == "__main__":
    p = Path(os.getcwd())

    main_keyword = "Badger"
    supplemented_keywords = ["Tiny","Huge","Cute"]

    url_dir = p / "url_files" 
    img_dir = p / "images" / main_keyword

    

    master_download(main_keyword, supplemented_keywords, url_dir,  img_dir, num_requested = 5, connection_speed = "medium")
    