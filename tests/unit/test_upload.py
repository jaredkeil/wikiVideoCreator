import argparse
from pathlib import Path
import subprocess


def upload_to_youtube(filepath):
    # Upload to youtube privately with simple arguments.
    # Requires access/oauth2 tokens -> client_secrets.json & upload_video.py-oauth2.json
    p = Path(filepath)
    args = ['python', 'upload_video.py',
               f'--file={p.absolute()}',
               f'--title={p.stem}',
               f'--description={p.stem}',
               f'--keywords=',
               '--category=27',
               '--privacyStatus=private',  # You can change privacyStatus to 'public' if desired.
               '--noauth_local_webserver']  # For browser-less run. Without, browser opens and asks permission.
    print(args)
    subprocess.run(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload videos to youtube. Usage: python test_upload.py <filepath>')
    parser.add_argument('filepath')
    opt = parser.parse_args()
    upload_to_youtube(filepath=opt.filepath)
