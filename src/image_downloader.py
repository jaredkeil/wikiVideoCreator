# -*- coding: utf-8 -*-
# @Author: WuLC
# @Date:   2017-09-27 23:02:19
# @Last Modified by:   Arthur 
# @Last Modified time: 2020-03-11 15:36:58


####################################################################################################################
# Download images from google with specified keywords for searching
# search query is created by "main_keyword + supplemented_keyword"
# if there are multiple keywords, each main_keyword will join with each supplemented_keyword
# Use selenium and urllib, and each search query will download any number of images that google provide
# allow single process or multiple processes for downloading
# Pay attention that since selenium is used, geckodriver and firefox browser is required
####################################################################################################################

import os
import sys
import json
import time
from math import ceil
import logging
import urllib.request
import urllib.error
from urllib.parse import urlparse, quote

from multiprocessing import Pool
from user_agent import generate_user_agent
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def get_image_links(main_keyword, supplemented_keywords, num_requested = 100):
    """get image links with selenium
    
    Args:
        main_keyword (str): main keyword
        supplemented_keywords (list[str]): list of supplemented keywords
        link_file_path (str): path of the file to store the links
        num_requested (int, optional): maximum number of images to download
    
    Returns:
        None
    """
    number_of_scrolls = ceil(num_requested/700)
    # 700 is currently arbitrary. It is an attempt to limit the images loaded.

    img_urls = set()
    driver = webdriver.Firefox()
    for i in range(len(supplemented_keywords)):
        search_query = quote(main_keyword + ' ' + supplemented_keywords[i])
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
            sys.stdout.write(f"Finding URL's [{'#' * (i+1) + ' ' * (num_requested - i)}]   \r")
            sys.stdout.flush() 
            try:
                thumb.click()
                time.sleep(1) # This is wait time for the image to load in it's higher resolution 
                                # so that the URL can be retrieved
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
                    
    driver.quit()
    
    # Defining link file path
    p = Path(__file__).resolve().parents[1]
    link_file_path = p / 'url_files' / f"{main_keyword}.txt"
    
    with open(link_file_path, 'w') as wf:
        for url in img_urls:
            wf.write(url +'\n')
    print(f'\nStored {len(img_urls)} links in {link_file_path}')
    return link_file_path


def download_images(link_file_path):
    """download images whose links are in the link file
    
    Args:
        link_file_path (str): path of file containing links of images
        download_dir (str): directory to store the downloaded images
    
    Returns:
        None
    """
    link_file_path=f"../url_files/{main_keyword}.txt"
    print('Start downloading with link file {0}..........'.format(link_file_path))
    log_dir='log_dir/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = log_dir + 'download_selenium_{0}.log'.format(main_keyword)
    logging.basicConfig(level=logging.DEBUG, filename=log_file, filemode="a+", 
                        format="%(asctime)-15s %(levelname)-8s  %(message)s")
    download_dir='../images/'
    img_dir = download_dir + main_keyword + '/'
    count = 0
    headers = {}
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        
    # start to download images
    with open(link_file_path, 'r') as rf:
        for i, link in enumerate(rf):
            sys.stdout.write(f"Downloading images [{'#' * (i+1) + ' ' * (file_len(link_file_path) - i)}]   \r")
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
                file_path = img_dir + f'{count}.jpg'
                with open(file_path,'wb') as wf:
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
        downloaded_num = len(os.listdir(f"../images/{main_keyword}")) - 1 # 
        print(f"\nSuccessfully downloaded {downloaded_num} images")
                
def master_download(main_keyword, num_requested = 20, supplemented_keywords=[' ']):
    link_file_path = get_image_links(main_keyword, supplemented_keywords, num_requested)
    download_images(link_file_path)


if __name__ == "__main__":
    main_keywords = ['neutral', 'angry', 'surprise', 'disgust', 'fear', 'happy', 'sad']

    supplemented_keywords = ['facial expression',\
                'human face',\
                'face',\
                'old face',\
                'young face',\
                'adult face',\
                'child face',\
                'woman face',\
                'man face',\
                'male face',\
                'female face',\
                'gentleman face',\
                'lady face',\
                'boy face',\
                'girl face',\
                'American face',\
                'Chinese face',\
                'Korean face',\
                'Japanese face',\
                'actor face',\
                'actress face'\
                'doctor face',\
                'movie face'
                ]

    # test for chinese
    # main_keywords = ['高兴', '悲伤', '惊讶']
    # supplemented_keywords = ['人脸']

    # test for japanese
    # main_keywords = ['喜びます', 'きょうがいする', '悲しみ']
    # supplemented_keywords = ['顔つき']

    download_dir = './data/'
    link_files_dir = './data/link_files/'
    log_dir = './logs/'
    for d in [download_dir, link_files_dir, log_dir]:
        if not os.path.exists(d):
            os.makedirs(d)

    ###################################
    # get image links and store in file
    ###################################
    # single process
    # for keyword in main_keywords:
    #     link_file_path = link_files_dir + keyword
    #     get_image_links(keyword, supplemented_keywords, link_file_path)
    

    # multiple processes
    p = Pool(3) # default number of process is the number of cores of your CPU, change it by yourself
    for keyword in main_keywords:
        p.apply_async(get_image_links, args=(keyword, supplemented_keywords, link_files_dir + keyword))
    p.close()
    p.join()
    print('Fininsh getting all image links')
    
    ###################################
    # download images with link file
    ###################################
    # single process
    # for keyword in main_keywords:
    #     link_file_path = link_files_dir + keyword
    #     download_images(link_file_path, download_dir)
    
    # multiple processes
    p = Pool() # default number of process is the number of cores of your CPU, change it by yourself
    for keyword in main_keywords:
        p.apply_async(download_images, args=(link_files_dir + keyword, download_dir, log_dir))
    p.close()
    p.join()
    print('Finish downloading all images')
