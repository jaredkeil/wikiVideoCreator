import subprocess
import pandas as pd
import wikipedia

from movie_maker import WikiMovie

n_pages = 20 # Number of pages to make videos of from the wikipedia list.

def get_top25():
    url = "https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report"
    table = pd.read_html(url)[2]
    print("Extracting wikipedia pages")
    top25 = list(map(lambda x: wikipedia.page(x), table["Article"][:n_pages]))
    return top25

def upload_to_youtube(movie):
#    keywords = '","'.join(movie.page.categories)
    arglist = ['python', 'upload_video.py',
            f'--file={movie.VID_PATH}',
            f'--title={movie.title}',
            f'--description={movie.page.summary}',
            f'--keywords=',
            '--category=27',
            '--privacyStatus=public']
    print(arglist)
    subprocess.run(arglist)

def main():
    page_list = get_top25()
    for page in page_list:
        WMM = WikiMovie(page)
        try: 
            WMM.make_movie(cutoff=3000)
        except Exception:
            print("Movie creation failed")
        try:
            upload_to_youtube(WMM)
        except Exception:
            print("Upload Failed")


if __name__ == '__main__':
    main()
