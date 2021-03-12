from moviepy.video.VideoClip import TextClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import moviepy.video.fx.all as vfx
from moviepy.video.compositing.concatenate import concatenate_videoclips

from wiki_movie.utils import make_directory

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WHITE_GIZEH = (1, 1, 1)
BLACK_GIZEH = (0, 0, 0)

VIDEO_SIZE = (1920, 1080)
IMG_SHAPE = (1080, 1920)
IMG_DURATION = 4

THANKS = "Thanks for watching \n and listening"
SUBSCRIBE = "Please Subscribe!"


def create_clip(clip_title, audio_dir, image_dir, level, include_images, fmt):
    """
    Creates section title text clip, a slideshow, and adds narrator audio.

    Args:
        clip_title (str) -- clip title
        audio_dir (Path) -- e.g. 'audio/<clip_title>/*.wav'
        image_dir (Path) -- e.g. 'images/python/resized/<clip_title>/*.jpg'
        level (int) -- Indentation level. Higher means more indented.
        include_images (bool) -- Should be true if section contains text.
        fmt (str) -- audio format which narrator used.
    Returns:
        clip (VideoClip) -- Combined TextClip and (optional) ImageSequence
    """
    audio_path = str(audio_dir / clip_title)

    clip = narrated_header(clip_title, audio_path, level, fmt)

    if include_images or level == 0:
        img_seq = narrated_image_seq(audio_path, image_dir / clip_title, fmt)
        clip = concatenate_videoclips([clip, img_seq], method='compose')

    print(clip_title, 'clip created!')

    clip = clip.set_fps(1)
    return clip


def narrated_header(section_title, narration_path, level, fmt):
    """
    Create video which displays section title
    and attaches audio of narrator reading title."
    """
    audio_clip_header = AudioFileClip(narration_path + f'_header.{fmt}'
                                      ).set_fps(1)
    return (TextClip(section_title,
                     color='white',
                     fontsize=130 - (30 * level),
                     size=VIDEO_SIZE,
                     method='caption')
            .set_audio(audio_clip_header)
            .set_duration(audio_clip_header.duration))


def narrated_image_seq(narration_path, image_dir, fmt):
    """
    Create video which displays looping slideshow of images
    and attaches audio of narrator reading section text."
    """
    audio_clip_text = AudioFileClip(narration_path + f'_text.{fmt}').set_fps(1)
    images = files_in_directory(image_dir)
    return (ImageSequenceClip(sequence=images,
                              durations=const_list(IMG_DURATION, len(images)),
                              load_images=True)
            .set_position(('center', 400))
            .fx(vfx.loop, duration=audio_clip_text.duration)
            .set_audio(audio_clip_text))


def files_in_directory(directory):
    return [str(p) for p in directory.glob('*')
            if p.is_file() and p.parts[-1][0] != '.']


def const_list(val, n):
    return [val for _ in range(n)]


def add_outro(clips):
    thx = TextClip(THANKS, color='white', fontsize=72,
                   size=VIDEO_SIZE, method='caption').set_duration(2)
    sub = TextClip(SUBSCRIBE, color='white', fontsize=72,
                   size=VIDEO_SIZE, method='caption').set_duration(2)

    return concatenate_videoclips(clips + [thx, sub],
                                  method='compose'
                                  ).on_color(color=BLACK, col_opacity=1)


def save_video(clips, path):
    make_directory(path.parent)
    clips.write_videofile(str(path),
                          fps=1,
                          audio_codec='aac',
                          preset='ultrafast',
                          threads=2)
    clips.close()
