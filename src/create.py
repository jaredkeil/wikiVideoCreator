import os
import shutil
import subprocess
import pandas as pd
import wikipediaapi

from movie_maker import WikiMovie


WikiAPI = wikipediaapi.Wikipedia('en') # initialize API
n_pages = 20 # Number of pages to make videos of from the wikipedia list.


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
            f'--file={movie.VID_PATH}',
            f'--title={movie.title}',
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

    txt_path = p / 'url_files' / (movie.title + '.txt')
    asset_paths = [movie.VID_PATH, movie.AUDIO_PATH, txt_path]
    for p in asset_paths:
        if os.path.exists(p):
            os.remove(p)
        else:
            print(f"The file {p} does not exist or cannot be found")

def main(upload=True):

    page_list = get_top25()

    for page in page_list:
        WMM = WikiMovie(page)
        try:
            WMM.make_movie(cutoff=3000)
            print("Saved to: ", str(WMM.vidpath))
        except Exception:
            print("Movie creation failed")

        try:
            if upload: upload_to_youtube(WMM)
            else: print("Not uploading")
        except Exception:
            print("Upload Failed")

        delete_assets(WMM)



if __name__ == '__main__':
    main(upload = False)
