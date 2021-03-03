import argparse
import subprocess

from wiki_movie.upload_video import __file__ as uploader
from wiki_movie.video import WikiMovie, parse_narrator_args, parse_downloader_args
from wiki_movie.resources import top25, wiki_page_list


def upload(video_path, title, description, private=False):
    privacy = 'private' if private else 'public'

    cmd_args = ['python', uploader,
                f'--file={video_path}',
                f'--title={title}',
                f'--description={description}',
                f'--keywords=',
                '--category=27',
                f'--privacyStatus={privacy}',
                '--noauth_local_webserver']

    print(cmd_args)

    subprocess.run(cmd_args)


def main(args):
    if args.single_page:
        titles = [" ".join(args.single_page)]

    elif args.top25:
        titles = top25()

    elif args.url:
        titles = wiki_page_list(args.url, args.n_pages)

    for title in titles:
        try:
            print(f'Initializing WikiMovie for "{title}"')
            movie = WikiMovie(title, args.narrator, parse_narrator_args(args), parse_downloader_args(args))

            movie.image_downloader.driver.quit()
            movie.make_movie(args.overwrite)

            if args.upload:
                upload(movie.vid_path, movie.script[0]['title'], movie.script[0]['text'], args.private)

            if args.delete_all:
                movie.delete_assets()
        except Exception as e:
            print(e)
            print(f'Failed on {title}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='make video from wikipedia articles(s) and optionally upload via YouTube API.')

    # Required arguments
    exgroup = parser.add_argument_group(title='Mode (only pick one)')
    mode = exgroup.add_mutually_exclusive_group(required=True)
    mode.add_argument('-s', '--single_page', nargs='+', help='name of one specific page')
    mode.add_argument('-t', '--top25', action='store_true', help='use the top25 articles of the week')
    mode.add_argument('--url', help='URL of an article, which must contain a list/table of articles')

    # Optional arguments
    parser.add_argument('-d', '--delete_all', action='store_true', help='delete assets after movie is made')
    parser.add_argument('--n_pages', type=int, default=25, help='number to process from url')

    parser.add_argument('-u', '--upload', action='store_true', help='upload to YouTube')
    parser.add_argument('-p', '--private', action='store_true', help='set uploaded video as private')
    parser.add_argument('-o', '--overwrite', action='store_true', help='overwrite previous files under same title')
    parser.add_argument('-n', '--narrator', default='sys_tts', choices=('sys_tts', 'google_tts', 'py_tts', 'dc_tts'),
                        help='Possible narrator names: sys_tts, py_tts, google_tts')

    # SystemNarrator arguments
    narrator_args = parser.add_argument_group('System narrator arguments (optional)')
    narrator_args.add_argument('-v', '--voice', help='voice of sys_tts - available voices dependant on platform')
    narrator_args.add_argument('-r', '--rate', help='words per minute of sys_tts')

    # ImageDownloader object arguments
    downloader_args = parser.add_argument_group('image downloader arguments (optional)')
    downloader_args.add_argument('-i', '--image_count', type=int, help='how many images per section')
    downloader_args.add_argument('-c', '--connect_speed', choices=('very slow', 'slow', 'medium', 'fast', 'very fast'),
                                 help='how quickly the webdriver waits for timeout')
    downloader_args.add_argument('-w', '--watch', action='store_true', help='run browser in non-headless mode')

    options = parser.parse_args()
    print(options)
    # main(options)
