import argparse
from pathlib import Path
import subprocess


def upload_to_youtube(filepath):
    p = Path(filepath)
    arglist = ['python', 'upload_video.py',
            f'--file={p.absolute()}',
            f'--title={p.stem}',
            f'--description={p.stem}',
            f'--keywords=',
            '--category=27',
            '--privacyStatus=public',
            '--noauth_local_webserver']
    print(arglist)
    subprocess.run(arglist)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath')
    opt = parser.parse_args()
    upload_to_youtube(filepath=opt.filepath)
