import argparse
from pathlib import Path
import subprocess


def upload_to_youtube(filepath):
    # Upload to youtube privately with simple arguments.
    # Requires access/oauth2 tokens -> client_secrets.json & upload_video.py-oauth2.json
    p = Path(filepath)
    arglist = ['python', 'upload_video.py',
            f'--file={p.absolute()}',
            f'--title={p.stem}',
            f'--description={p.stem}',
            f'--keywords=',
            '--category=27',
            '--privacyStatus=private',  # You can change privacyStatus to 'public' if desired.
            '--noauth_local_webserver'] # I believe necessary for browserless. Without, browser pops-up and asks permission.
    print(arglist)
    subprocess.run(arglist)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload videos to youtube. Usage: python test_upload.py <filepath>')
    parser.add_argument('filepath')
    opt = parser.parse_args()
    upload_to_youtube(filepath=opt.filepath)
