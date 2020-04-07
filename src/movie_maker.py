from pathlib import Path
import os
from moviepy.editor import *
import gizeh as gz
from gtts import gTTS
from skimage.io import imread, imsave
from skimage import transform
from skimage.util import img_as_ubyte
import time
from datetime import datetime

import wikipediaapi
from image_downloader import master_download
from im_funcs import maxsize_pad


# Default Parameters
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WHITE_GIZEH = (1, 1, 1)
BLACK_GIZEH = (0, 0, 0)

VIDEO_SIZE = (1920, 1080)
IMG_SHAPE = (1080, 1920)
IMG_DISPLAY_DURATION = 4    #duration, in seconds, to display each image

exclude_set = {'See also', 'References', 'Further reading', 'External links',
                'Formats and track listings', 'Credits and personnel', 'Charts',
                'Certifications', 'Release history'}

class WikiMovie():
    """
    Make movies in standard format (.mp4) from wikipedia pages.
    Initialize with 'page' object from wikipedia Python module.
    Primary user function is make_movie().
    """
    def __init__(self, page):
        self.page = page
        self.title = self.page._attributes['title']
        self.cliplist = []
        self.p = Path(__file__).resolve().parents[1]
        self._imgidx = 0
        

    def _create_paths(self):
        # Directories
        self.parent_images = self.p / 'images'
        self.imgdir = self.p / 'images' / self.title
        self.resizedir = self.imgdir / 'resize'
        self.parent_audio = self.p / 'audio'
        self.auddir = self.p / 'audio' / self.title
        self.url_dir = self.p / 'url_files'
        self.viddir = self.p / 'videos'
        # Path
        self.vidpath = self.viddir / (self.title + ".mp4")

        print('creating paths...')
        for d in [self.parent_images, self.imgdir, self.resizedir,\
                self.parent_audio, self.auddir, self.url_dir, self.viddir]:
            if not d.exists():
                d.mkdir()
                print(d, "directory created")
            elif d.exists():
                print(d, "exists")

    def _resize_images(self):
        self._imgpaths = []
        contents = self.imgdir.glob('*')
        fnames =  [x for x in contents if x.is_file() and x.parts[-1][0] != '.']
        self.fixed_durations = [IMG_DISPLAY_DURATION for _ in fnames]
        
        n_imgs = len(fnames)
        for i, fname in enumerate(fnames):
            sys.stdout.write(f"Resizing Images [{'#' * (i+1) + ' ' * (n_imgs-i-1)}]   \r")
            sys.stdout.flush()
            
            path = str(self.imgdir / fname)
            print(path)
            save_path = str(self.resizedir / fname)
            print(self.resizedir)
            print(save_path)
            try:
                maxsize_pad(path, save_path)
            except Exception:
                continue
            self._imgpaths.append(save_path)


    def _make_narration(self, string, mp3path):
        tts = gTTS(string)
        tts.save(mp3path)
        return AudioFileClip(mp3path)


    def _add_ImageSequence(self, audioclip):
        """add image with soundtrack audioclip of narrated text"""
        ### Cycle through images so it doesn't always start at the first one
        tmp_imgpaths = self._imgpaths[self._imgidx:] + self._imgpaths[:self._imgidx]
        self._imgidx += 1
        image_sequence = ImageSequenceClip(sequence=tmp_imgpaths,
                                durations=self.fixed_durations, load_images=True).\
                            set_position(('center', 400)).\
                            fx(vfx.loop, duration=audioclip.duration).\
                            set_audio(audioclip)
        self.cliplist.append(image_sequence)


    def _add_subsection(self, section, level):
        """
        Add textclip of section titles.
        If it's just a main header followed by subsections, NO image sequence.
        If section contains text, create narratation and image sequence.
        """

        mp3path_header = os.path.join(self.auddir, section.title + '_header.mp3')
        ac_header = self._make_narration(section.title, mp3path_header)
        fontsize = 130 - (30 * level) # higher level means deeper 'indentation'
        tc_header = TextClip(section.title, color='white', fontsize=fontsize, 
                    size=VIDEO_SIZE, method='caption').\
                    set_audio(ac_header).set_duration(ac_header.duration)
        self.cliplist.append(tc_header)
        ## if there is an actual paragraph in the section, create an image sequence for it
        if section.text:
            mp3path_text = os.path.join(self.auddir, section.title + '_text.mp3')
            ac_text = self._make_narration(section.text[:self.cutoff], mp3path_text)
            self._add_ImageSequence(ac_text)

        print(section.title, "complete")


    def _flush_sections(self, sections, level=0):
        """Recursively get text from all levels in sections,
        and generate narrations"""

        for s in sections:
            if s.title in exclude_set:
                continue
            else:
                self._add_subsection(s, level) # clip creation
                self._flush_sections(s.sections, level+1) # recursion


    def _flush_page(self):
        # add main title and summary
        mp3path_title = os.path.join(self.auddir, self.title + '_title.mp3')
        ac_title = self._make_narration(self.title, mp3path_title)
        tc_title = TextClip(self.title, color='white', fontsize=150, 
                    size=VIDEO_SIZE, method='caption').\
                    set_audio(ac_title).set_duration(ac_title.duration)
        self.cliplist.append(tc_title)
        
        mp3path_summary = os.path.join(self.auddir, self.title + '_summary.mp3')
        ac_summary = self._make_narration(self.page.summary[:self.cutoff], mp3path_summary)
        self._add_ImageSequence(ac_summary)
        print('Title and Summary complete')
        # create clips for rest of sections
        self._flush_sections(self.page.sections)


    def make_movie(self, cutoff=None):
        """
        Args:
            cutoff (int): Limit the length of the script. Used like script[:cutoff]
        Returns:
            None
        """
        print("Video Title: ", self.title)
        self.cutoff = cutoff
        self._create_paths()

        # Download and resize images
        master_download(main_keyword=self.title, url_dir=self.url_dir,
                        img_dir=self.imgdir, num_requested=100)
        self._resize_images()
        print('\n') 

        # Create Video Clips
        print("Creating clips. . .")
        self._flush_page()

        thanks = TextClip("Thanks for watching \n and listening",
                            color='white', fontsize=72, size=VIDEO_SIZE, method='caption').\
                            set_duration(2)

        subscribe = TextClip("Please Subscribe!",
                                color='white', fontsize=72, size=VIDEO_SIZE, method='caption').\
                                set_duration(2)

        self.video = concatenate_videoclips(self.cliplist + [thanks, subscribe],
                                            method='compose').\
                                            on_color(color=BLACK, col_opacity=1)
        # Encode Video
        start = datetime.now()
        self.video.write_videofile(str(self.vidpath) , fps=1, codec='mpeg4', 
                                    audio_codec="aac", preset='ultrafast')
        dur = datetime.now() - start
        print("Video Encoding completed in time: ", dur)

        # self.audio_clip.close()
        # title_text.close()
        thanks.close()
        subscribe.close()
        self.video.close()


if __name__ == "__main__":
    wiki = wikipediaapi.Wikipedia('en')
    page = wiki.page(input("What would you like the video to be about? "))
    WMM = WikiMovie(page)
    WMM.make_movie(cutoff=None)
