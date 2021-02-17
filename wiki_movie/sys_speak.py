import subprocess
import sys

from wiki_movie.utils import localtime_filepath, repository_root, make_directory


def save_mac(message=None, file=None, voice='Alex', file_name=None):
    if not (message or file):
        raise ValueError('Please specify either message(str) or file (path to text file, as str)')

    if message and file:
        raise ValueError('Can only specify one of either message or file')

    if not file_name:
        save_dir = repository_root / 'data' / 'audio' / 'untitled'
        make_directory(save_dir)
        file_name = localtime_filepath(save_dir, 'aiff')

    args = ['say', '-v', voice, '-o', file_name]
    if file:
        args.extend(['-f', file])
    else:
        args.append(message)

    subprocess.run(args)


def save_linux(message, file_name=None):
    # For Linux-Ubuntu with eSpeak installed:
    # espeak {message} --stdout > {file_name.wav}

    if not file_name:
        save_dir = repository_root / 'data' / 'audio' / 'untitled'
        make_directory(save_dir)
        file_name = localtime_filepath(save_dir, 'aiff')

    subprocess.run(['espeak', message, '--stdout', '>', ])


def save(*args, **kwargs):
    platform = sys.platform
    if platform == "linux" or platform == "linux2":
        save_linux(*args, **kwargs)
    elif platform == "darwin":
        save_mac(*args, **kwargs)
    elif platform == "win32":
        raise NotImplementedError('Speech on Windows platform not implemented yet.')
    else:
        raise NotImplementedError('Unrecognized platform.')



