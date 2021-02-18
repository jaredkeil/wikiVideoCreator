import subprocess
import sys

from wiki_movie.utils import localtime_filepath, repository_root, make_directory, has_extension, add_extension


def save_mac(message=None, file=None, voice='Alex', rate=200, file_name=None):
    if not (message or file):
        raise ValueError('Please specify either message(str) or file (path to text file, as str)')

    if message and file:
        raise ValueError('Can only specify one of either message or file')

    if not file_name:
        save_dir = repository_root / 'data' / 'audio' / 'untitled'
        make_directory(save_dir)
        file_name = localtime_filepath(save_dir, 'aiff')

    if not has_extension(file_name, 'aiff'):
        file_name = add_extension(file_name, 'aiff')

    args = ['say', '-v', voice, '-r', rate, '-o', file_name]
    if file:
        args.extend(['-f', file])
    else:
        args.append(message)

    subprocess.run(args)


def save_linux(message, file_name=None, **kwargs):
    # For Linux-Ubuntu with eSpeak installed:
    # espeak {message} --stdout > {file_name.wav}

    if not file_name:
        save_dir = repository_root / 'data' / 'audio' / 'untitled'
        make_directory(save_dir)
        file_name = localtime_filepath(save_dir, 'wav')

    if not has_extension(file_name, 'wav'):
        file_name = add_extension(file_name, 'wav')

    subprocess.run(['espeak', message, '--stdout', '>', file_name])


def save(*args, **kwargs):
    platform = sys.platform
    if platform == "linux" or platform == "linux2":
        save_linux(*args, **kwargs)
    elif platform == "darwin":
        save_mac(*args, **kwargs)
    elif platform == "win32":
        raise NotImplementedError('Speech on Windows platform not implemented yet.')
    else:
        raise NotImplementedError(f'Unrecognized platform {platform}.')
