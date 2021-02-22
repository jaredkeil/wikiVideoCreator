import argparse
from pathlib import Path
import subprocess

from wiki_movie.upload_video import __file__ as uploader
from wiki_movie.video import WikiMovie


def generate_movie(opt):
    movie = WikiMovie(opt.single_page, narrator_name=opt.narrator)
    movie.make_movie(opt.overwrite, opt.overwrite, opt.overwrite)
    return movie


def upload(video_path, title, description, private=False):
    privacy = 'private' if private else 'public'

    args = ['python', uploader,
            f'--file={video_path}',
            f'--title={title}',
            f'--description={description}',
            f'--keywords=',
            '--category=27',
            f'--privacyStatus={privacy}',
            '--noauth_local_webserver']
    print(args)

    subprocess.run(args)


def main(opt):
    movie = generate_movie(opt)

    upload(video_path=movie.vid_path,
           title=movie.script[0]['title'],
           description=movie.script[0]['text'],
           private=opt.private)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='make video and optionally upload via YouTube API.\
                                    default behavior: use top_25 list, do not upload, do not delete assets')

    # Required arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--single_page', help='name of one specific page')
    group.add_argument('-t', '--top25', action='store_true')
    group.add_argument('--url', help='custom URL of Wiki page. Should contain list/table of articles')

    # Optional arguments
    # parser.add_argument('-u', '--upload', action='store_true', help='upload to YouTube')
    # parser.add_argument('-d', '--delete_all', action='store_true', help='delete assets after movie is made')
    # parser.add_argument('-n', '--n_pages', type=int, default=25,
    #                     help='how many pages to include when processing multiple pages')

    parser.add_argument('-p', '--private', action='store_true')
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-n', '--narrator', default='sys_tts',
                        help='Possible narrator names: sys_tts, py_tts, google_tts')

    options = parser.parse_args()
    main(options)
