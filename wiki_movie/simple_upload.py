import argparse
from pathlib import Path
import subprocess

from upload_video import __file__ as uploader


def upload_to_youtube(filepath):
    # Upload to youtube privately with simple arguments.
    # Requires access/oauth2 tokens
    # e.g. client_secrets.json & upload_video.py-oauth2.json
    p = Path(filepath)

    args = ['python', uploader,
            f'--file={p.absolute()}',
            f'--title={p.stem}',
            f'--description={p.stem}',
            f'--keywords=',
            '--category=27',
            '--privacyStatus=private',  # can change privacyStatus to 'public'
            '--noauth_local_webserver']  # For browser-less run
    print(args)
    subprocess.run(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Upload videos to youtube. '
                    'Usage: python simple_upload.py <filepath>')
    parser.add_argument('filepath')
    opt = parser.parse_args()

    print(uploader)

    upload_to_youtube(filepath=opt.filepath)
