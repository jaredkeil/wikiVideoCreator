import os
import sys
from pathlib import Path
import argparse

import wikipediaapi

from moviepy.video.VideoClip import TextClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import moviepy.video.fx.all as vfx
from moviepy.video.compositing.concatenate import concatenate_videoclips
# import gizeh as gz


import pyttsx3

from pydub import AudioSegment

import time
from datetime import datetime

import image_downloader_old
from wiki_movie.image_downloader import ImageDownloader
from wiki_movie import im_funcs
# from dc_tts.synthesize import synthesize as dctts_synthesize
# from dc_tts.hyperparams import Hyperparams as hp

# Default Parameters
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WHITE_GIZEH = (1, 1, 1)
BLACK_GIZEH = (0, 0, 0)

VIDEO_SIZE = (1920, 1080)
IMG_SHAPE = (1080, 1920)
IMG_DISPLAY_DURATION = 4  # duration in seconds to display each image

excluded_sections = {'See also', 'References', 'Further reading', 'External links',
                     'Formats and track listings', 'Credits and personnel', 'Charts',
                     'Certifications', 'Release history'}

stops = {'\n', '\t', 'e.g.', '[sic]', '[...]', 'i.e.', }  # strings to remove from article text


class WikiMovie:
    """
    Make movies in standard format (.mp4) from wikipedia pages.

    Initialize with 'page' object from wikipedia Python module.
    Primary function is make_movie().
    """

    def __init__(self, page, narrator='gtts', overwrite=True):
        """
        Args:
        page (wikipediaapi.WikipediaPage) -- Specific page object used to make movie.
        narrator (str) -- text-to-speech engine ["gtts" = google TTS API,
                                                "dctts" = neural net,
                                                "pytts" = pyttsx3 engine] (default "gtts")
        overwrite (bool) -- Overwrite audio (default True) 
        """
        self.page = page
        self.narrator = narrator
        self._validate_narrator()
        self.overwrite = overwrite

        self.title = self.page._attributes['title']
        self.script = [{'title': page.title,
                        'level': 0,
                        'text': self.clean_text(page.summary)}]  # page.summary is first paragraph of article
        self.keywords = [' ']
        self.clip_list = []

        self.p = Path(__file__).resolve().parents[0]
        # self.p = Path(os.path.abspath('')).resolve() ## For jupyter notebook
        self._imgidx = 0  # For starting image sequences on unique image
        self.cutoff = None

    def _validate_narrator(self):
        if self.narrator not in {'gtts', 'pytts', 'dctts'}:
            raise NotImplementedError
        if self.narrator == 'pytts':
            self.engine = pyttsx3.init()

    def create_paths(self):
        # Image directories
        self.parent_images = self.p / 'images'
        self.imgdir = self.p / 'images' / self.title
        self.resizedir = self.imgdir / 'resize'

        # audio directories
        self.parent_audio = self.p / 'audio'
        self.auddir = self.p / 'audio' / self.title

        # URL lists text files directory
        self.url_dir = self.p / 'url_files'

        # Video directory (all article videos stored in folder, files named by title)
        self.viddir = self.p / 'videos'
        # Video save path
        self.vidpath = self.viddir / (self.title + ".mp4")

        to_create = [self.parent_images, self.imgdir, self.resizedir, self.parent_audio, self.auddir, self.url_dir,
                     self.viddir]

        if self.narrator == 'dctts':
            self.dctts_dir = self.p / 'dc_tts'
            self.dctts_in = self.dctts_dir / 'text_input'
            self.dctts_samples = self.dctts_dir / 'samples'  # audio ouput from dctts, which is created in small chunks
            self.dctts_out = self.dctts_dir / 'samples' / self.title
            to_create += [self.dctts_dir, self.dctts_in, self.dctts_samples, self.dctts_out]

        print('creating paths...')
        for d in to_create:
            if not d.exists():
                d.mkdir()
                print(d, "directory created")
            elif d.exists():
                print(d, "exists")

    def clean_text(self, text):
        """
        Remove stop words
        """
        for x in stops:
            text = text.replace(x, '')
        return text

    def flush_sections(self, sections, level=0):
        """
        Recurse through text under all levels (sections, subsections) in page order, and clean the  text.
        """
        for s in sections:
            if s.title in excluded_sections:
                print('exluding', s.title)
                continue
            else:
                self.script.append({'title': s.title,
                                    'level': level + 1,
                                    'text': self.clean_text(s.text)})
                # recursion to next level. Once lowest level is reached, next main section will be accessed
                self.flush_sections(s.sections, level + 1)

    def process_text_dctts(self):
        """
        Process article text into lines of pre-defined character limit of DC_TTS model.
        Uses the model's hyperparameter hp.max_N . . . currently at 180
        """
        self.sent_path = self.dctts_in / f"{self.title}.txt"
        hp.test_data = self.sent_path

        with self.sent_path.open('w') as sf:
            sf.write(f"Script for Wikipedia article {self.title}\n")
            sample_ct = 0

            # iterate over self.script(list of section dictionaries, "sd")
            for sd in self.script:
                # reminder of dictionary format:
                # sd = {'title': section title (str), 'level': level (int), 'text': section text (str)}

                # Full length sentences, possibly greater than max number of characters for model.
                # Split simply on period. Problematic for titles like Dr. and abbreviations like T.M.Z.
                full_sents = [sd['title']] + sd['text'].split('.')

                # break section down into max 180 character chunks 
                sents = []
                for sent in (full_sents):
                    sent = sent.strip()
                    if not sent:
                        continue

                    # if the sentence is longer than <hp.max_n>, find good split location and continue processing remainder
                    if len(sent) > hp.max_N:
                        split_on = sent[:hp.max_N].rfind(" ")
                        tmp_split = [sent[:split_on], sent[split_on:]]

                        while len(tmp_split[-1]) > hp.max_N:
                            last = tmp_split.pop()
                            split_on = last[:hp.max_N].rfind(" ")
                            tmp_split += [last[:split_on], last[split_on:]]

                        sents.extend(tmp_split)

                    else:
                        sents.append(sent)

                sd['n_segments'] = len(sents)
                sample_ct += len(sents)
                pre = sd['title'].replace(" ", "")
                for i, sent in enumerate(sents):
                    # write to sentence file
                    sf.write(f"{pre}:{i} {sent}\n")

    def get_keywords(self):
        self.keywords += [sd['title'] for sd in self.script[1:] if sd['text']]

    def process_images(self):
        for sd in self.script:
            if sd['title'] in self.keywords or sd['level'] == 0:
                self.resize_images(sd)

    def resize_images(self, sd):

        sk_imgdir = self.imgdir / sd['title']  # supplemented keyword used earlier by image search/download
        contents = sk_imgdir.glob('*')
        fnames = [x.parts[-1] for x in contents if x.is_file() and x.parts[-1][0] != '.']
        n_imgs = len(fnames)
        sd['idd'] = [IMG_DISPLAY_DURATION for _ in fnames]  # generate list of constant durations

        sd['imgpaths'] = []  # image paths
        for i, fname in enumerate(fnames, start=1):
            sys.stdout.write(f"Resizing {sd['title']} Images [{'#' * (i) + ' ' * (n_imgs - i)}]   \r")
            sys.stdout.flush()

            path = str(sk_imgdir / fname)
            save_path = str(self.resizedir / fname)
            try:
                im_funcs.maxsize_pad(path, save_path)
            except Exception:
                print(f'error saving resized image: {fname}')
                continue
            sd['imgpaths'].append(save_path)

        print('\ndone')

    def make_narration(self):

        if self.narrator == 'dctts':
            # check if narration already exists
            if len(os.listdir(self.dctts_out)) > 0 and not self.overwrite:
                print('Not going to make narration')
            else:
                dctts_synthesize()
                self.combine_wavs()

        elif self.narrator == 'gtts':
            for sd in self.script:
                prefix = str(self.auddir / sd['title'])
                # Create header speech
                self.google_tts(string=sd['title'], mp3path=prefix + '_header.mp3')
                # If further text is contained in section
                if sd['text']:
                    self.google_tts(string=sd['text'], mp3path=prefix + '_text.mp3')

        elif self.narrator == 'pytts':
            for sd in self.script:
                prefix = str(self.auddir / sd['title'])

                self.pytts(string=sd['title'], aiffpath=prefix + '_header.mp3')

                if sd['text']:
                    self.pytts(string=sd['text'], aiffpath=prefix + '_text.mp3')

    def google_tts(self, string, mp3path):
        error_count = 0
        tts = gTTS(string)
        while True:
            try:
                tts.save(mp3path)
                print('gtts success')
                break

            except Exception as e:
                print(e)
                print(f'gTTS save error, trying again. Error count: {error_count}')
                error_count += 1

                # rsp should be <requests.Response>
                if isinstance(e, gTTSError) and e.rsp:
                    if e.rsp.status_code == 429:
                        # too many requests, sleep
                        time.sleep(60)

    def pytts(self, string, aiffpath):
        self.engine.save_to_file(string, aiffpath)
        self.engine.runAndWait()

    def combine_wavs(self):
        """
        Combine the short wav files outputs from dc-tts into by article section.
        """
        ct = 1  # used in wav filenames, ex: 1.wav, 2.wav, 3.wav, etc.
        for sd in self.script:
            # convert section title to mp3
            print(sd['title'])
            AS_title = AudioSegment.from_wav(str(self.dctts_out / (str(ct) + '.wav')))
            path = str(
                self.auddir / (sd['title'] + '_header.mp3'))  # / audio / {article title} / {section title}_header.mp3}
            AS_title.export(path, format='mp3', codec='libmp3lame')

            # combine rest of speech, convert to mp3                               
            n = sd['n_segments']
            print(n, "segments")
            if sd['title'] in self.keywords or sd['level'] == 0:
                AS_text = AudioSegment.from_wav(str(self.dctts_out / (str(ct + 1) + '.wav')))
                for i in range(ct + 2, ct + n):
                    AS_text += AudioSegment.from_wav(str(self.dctts_out / (str(i) + '.wav')))
                path = str(self.auddir / (sd['title'] + '_text.mp3'))
                AS_text.export(path, format='mp3', codec='libmp3lame')

            ct += n

    def create_clip(self, sd):
        """
        Load back audio and attach it to proper clip.

        Args: 
            sd (dict) -- A dictionary as found in self.script
        Returns:
            V (VideoClip) -- Combined TextClip and (optional) ImageSequence
        """
        prefix = str(self.auddir / sd['title'])
        afc_header = AudioFileClip(prefix + '_header.mp3').set_fps(1)

        font_size = 130 - (30 * sd['level'])  # higher level means deeper 'indentation'
        V = (TextClip(sd['title'], color='white', fontsize=font_size, size=VIDEO_SIZE, method='caption')
             .set_audio(afc_header)
             .set_duration(afc_header.duration))

        if sd['title'] in self.keywords or sd['level'] == 0:
            ACT = AudioFileClip(prefix + '_text.mp3').set_fps(1)
            print(sd['imgpaths'])
            print(sd['idd'])
            IS = (ImageSequenceClip(sequence=sd['imgpaths'], durations=sd['idd'], load_images=True)
                  .set_position(('center', 400))
                  .fx(vfx.loop, duration=ACT.duration)
                  .set_audio(ACT))
            V = concatenate_videoclips([V, IS], method='compose')
        print(sd['title'], 'clip created!')
        V = V.set_fps(1)
        return V

    def make_movie(self, hp=None, cutoff=None):
        """
        Creates and saves movie.

        Args:
        hp (Hyperparams) -- Hyperparams object with attributes test_data, max_N, 
        cutoff (int) -- Limit the length of the script (for testing purposes). Used like script[:cutoff]
        """
        print("Video Title: ", self.title)
        self.cutoff = cutoff
        self.create_paths()

        self.flush_sections(self.page.sections)

        if self.narrator == 'dctts':
            # prepare text for dc tts network
            self.process_text_dctts()
            hp.test_data = str(self.sent_path)
            hp.sampledir = str(self.dctts_out)
            print("test data: " + hp.test_data)

        # Download and resize images
        self.get_keywords()

        # image_downloader_old.master_download(main_keyword=self.title, supplemented_keywords=self.keywords,
        #                                      url_dir=self.url_dir, img_dir=self.imgdir, num_requested=5)

        image_downloader = ImageDownloader(main_keyword=self.title, supplemented_keywords=self.keywords,
                                           url_dir=self.url_dir, img_dir=self.imgdir, num_requested=5,
                                           connection_speed='medium', headless=True)
        image_downloader.find_and_download()

        self.process_images()
        print('\n')

        # Text-to-speech ()
        print('Creating audio. . . ')
        self.make_narration()

        # Create Video Clips
        print("Creating video clips. . .")
        self.clip_list = [self.create_clip(sd) for sd in self.script]

        thanks = TextClip("Thanks for watching \n and listening",
                          color='white', fontsize=72, size=VIDEO_SIZE, method='caption'). \
            set_duration(2)

        subscribe = TextClip("Please Subscribe!",
                             color='white', fontsize=72, size=VIDEO_SIZE, method='caption'). \
            set_duration(2)

        self.video = concatenate_videoclips(self.clip_list + [thanks, subscribe],
                                            method='compose'). \
            on_color(color=BLACK, col_opacity=1)

        # Encode Video
        start = datetime.now()

        self.video.write_videofile(str(self.vidpath), fps=1, codec='mpeg4',
                                   #    audio_codec="aac",
                                   preset='ultrafast')
        dur = datetime.now() - start
        print("Video Encoding completed in time: ", dur)

        thanks.close()
        subscribe.close()
        self.video.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Make movie from wikipedia article. Usage: python test_upload.py <filepath>")
    parser.add_argument('name', default='Tarball', nargs='+')
    parser.add_argument('--mode',
                        default='gtts',
                        const='gtts',
                        nargs='?',
                        choices=['gtts', 'dctts', 'pyttsx'],
                        help='choose text-to-speech method (default: %(default)s)')
    parser.add_argument('--overwrite', action='store_true')
    opt = parser.parse_args()

    name = ' '.join(opt.name.strip("'"))

    wiki = wikipediaapi.Wikipedia('en')

    # User input
    # requested_name = input("What would you like the video to be about? ")
    # page = wiki.page(requested_name)

    page = wiki.page(name)

    WMM = WikiMovie(page, narrator=opt.mode, overwrite=True)

    WMM.make_movie(cutoff=None, hp=hp)  # hp parameter is really only necessary with dctts
