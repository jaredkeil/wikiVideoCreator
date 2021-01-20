import os
import argparse
from pathlib import Path
import shutil
import subprocess

import pandas as pd
import wikipediaapi

from movie_maker import WikiMovie


# initialize API
WikiAPI = wikipediaapi.Wikipedia('en')

def custom_list(url):
    table = pd.read_html(url)[2]
    print("Extracting wikipedia pages")
    page_list = list(map(lambda x: WikiAPI.page(x), table["Article"][:n_pages]))
    return page_list

def get_top25(n_pages):
    url = "https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report"
    table = pd.read_html(url)[2]
    print("Extracting wikipedia pages")
    top25 = list(map(lambda x: WikiAPI.page(x), table["Article"][:n_pages]))
    return top25

def upload_to_youtube(movie):
#    keywords = '","'.join(movie.page.categories)
    p = Path(__file__).parents[0].resolve()
    py_file = str(p / 'upload_video.py')
    mtitle = movie.title.title()
    arglist = ['python', py_file,
            f'--file={movie.vidpath}',
            f'--title={mtitle}',
            f'--description={movie.page.summary}',
            f'--keywords=',
            '--category=27',
            '--privacyStatus=public',
            '--noauth_local_webserver']
    print(arglist)
    subprocess.run(arglist)


def delete_assets(movie):
    # delete all in image/{movie.title}, including resize folder
    # delete video, mp3, url_files/.txt
    recursive_dirs = [movie.imgdir, movie.auddir]
    for d in recursive_dirs:
        shutil.rmtree(d)
        print("removed ", d)

    links_file = movie.url_dir / (movie.title + '.txt')
    asset_paths = [movie.vidpath, links_file]
    for asset in asset_paths:
        if asset.exists():
            asset.unlink()
            print(f"{asset} deleted")
        else:
            print(f"The file {asset} does not exist or cannot be found")


def main(opt):
    if opt.single_page: page_list = [WikiAPI.page(opt.single_page)]
    elif opt.top25: page_list = get_top25(opt.n_pages)
    elif opt.url: page_list = custom_list(opt.url)

    for page in page_list:
        WMM = WikiMovie(page)
        try:
            WMM.make_movie(cutoff=opt.cutoff)
            print("Saved to: ", str(WMM.vidpath))
        except Exception as e:
            print(e)
            print("Movie creation failed")
        try:
            if opt.upload: upload_to_youtube(WMM)
            else: print("Not uploading")
        except Exception:
            print("Upload Failed")
        if opt.delete_all:
            delete_assets(WMM)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='make video and optionally upload via YouTube API.\
                                    default behavior: use top_25 list, do not upload, do not delete assets')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--single_page', help='name of one specific page')
    group.add_argument('-t','--top25', action='store_true')
    group.add_argument('--url', help='custom URL of Wiki page. Should contain list of articles')
    parser.add_argument('-u', '--upload', action='store_true', help='upload to YouTube')
    parser.add_argument('-d', '--delete_all', action='store_true', help='delete assets after movie is made')
    parser.add_argument('-n', '--n_pages', type=int, default=25, help='how many pages to include when processing multiple pages')
    parser.add_argument('-c', '--cutoff', type=int,  help='number of characters to include from each section')
    opt = parser.parse_args()

    print(opt)
    main(opt)
