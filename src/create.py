import os
import argparse
from pathlib import Path
import shutil
import subprocess

import pandas as pd
import wikipediaapi

from movie_maker import WikiMovie


WikiAPI = wikipediaapi.Wikipedia('en') # initialize API
# n_pages = 20 # Number of pages to make videos of from the wikipedia list.


def custom_list(url):
    table = pd.read_html(url)[2]
    print("Extracting wikipedia pages")
    page_list = list(map(lambda x: WikiAPI.page(x), table["Article"][:n_pages]))
    return page_list

def get_top25():
    url = "https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report"
    table = pd.read_html(url)[2]
    print("Extracting wikipedia pages")
    top25 = list(map(lambda x: WikiAPI.page(x), table["Article"][:n_pages]))
    return top25

def upload_to_youtube(movie):
#    keywords = '","'.join(movie.page.categories)
    mtitle = movie.title.title()

    arglist = ['python', 'upload_video.py',
            f'--file={movie.vidpath}',
            f'--title={mtitle}',
            f'--description={movie.page.summary}',
            f'--keywords=',
            '--category=27',
            '--privacyStatus=public']
    print(arglist)
    subprocess.run(arglist)


def delete_assets(movie):
    # delete all in image/{movie.title}, including resize folder
    # delete video, mp3, url_files/.txt
    p = movie.p # A PosixPath

    shutil.rmtree(movie.imgdir)
    shutil.rmtree(movie.auddir)

    links_txt = p / 'url_files' / (movie.title + '.txt')
    asset_paths = [movie.vidpath, links_txt]
    for asset in asset_paths:
        if asset.exists():
            asset.unlink()
            print(f"{asset} deleted")
        else:
            print(f"The file {asset} does not exist or cannot be found")


def main(single_page, top25, url, upload, delete_all, n_pages, cutoff):
    
    if single_page:
        page_list = [WikiAPI.page(single_page)]
    elif top25:
        page_list = get_top25()
    elif url:
        page_list = custom_list(url)

    for page in page_list:
        WMM = WikiMovie(page)
        try:
            WMM.make_movie(cutoff=20)
            print("Saved to: ", str(WMM.vidpath))
        except Exception:
            print("Movie creation failed")

        try:
            if upload: upload_to_youtube(WMM)
            else: print("Not uploading")
        except Exception:
            print("Upload Failed")
        if delete_all:
            delete_assets(WMM)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make video and optionally upload via YouTube API.\
                                    default behavior: Use top_25 list, do not upload, do not delete assets')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--single_page', 
                        help='name of one specific page')
    group.add_argument('-t','--top25', action='store_true')
    group.add_argument('--url', 
                        help='custom URL of Wiki page. Should contain list of articles')
    parser.add_argument('-u', '--upload', action='store_true', 
                        help='upload to YouTube')
    parser.add_argument('-d', '--delete_all', action='store_true',
                         help='delete assets after movie is made')
    parser.add_argument('-n', '--n_pages', type=int, default=25,
                        help='how many pages to include when processing multiple pages')
    parser.add_argument('-c', '--cutoff', type=int,
                        help='number of characters to include from each section')

    args = parser.parse_args()
    print(args)

    main(single_page=args.single_page,
        top25=args.top25,
        url=args.url,
        upload=args.upload,
        delete_all=args.delete_all,
        n_pages=args.n_pages,
        cutoff=args.cutoff)
