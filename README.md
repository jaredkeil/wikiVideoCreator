[![Build Status](https://www.travis-ci.com/jaredkeil/wikiVideoCreator.svg?branch=master)](https://www.travis-ci.com/jaredkeil/wikiVideoCreator)

# create videos from Wikipedia articles

Turn Wikipedia articles into videos with computer-generated overdubbing, and the option to upload directly to YouTube.
Includes helpful parsers for Wikipedia API requests, as well as a module for downloading pictures from Google image searches.

## Installation:

### Firefox, geckodriver:

`sudo apt install firefox`

`sudo apt-get install firefox-geckodriver`

Or use homebrew.

`brew install --cask firefox'
`brew install geckodriver`

(Selenium installs with python dependencies in requirements.txt)


### [ImageMagick](https://imagemagick.org/script/download.php), and [Ghostscript](https://www.ghostscript.com/doc/9.53.3/Install.htm):
    

  `sudo apt install imagemagick` or `brew install imagemagick`

  Note, because of issue with MoviePy, you may need to alter the policy.xml file of ImageMagick (see [this issue](https://github.com/Zulko/moviepy/issues/401#issuecomment-278679961)). To find where the file is located, run:
  
  `convert -list policy`

  The top line of the output should look like
  `Path: /etc/ImageMagick-6/policy.xml`

  If instead it is `Path: [built-in]`, then no changes may be necessary.
  
  Edit line 88, or whichever line the policy refers to the "path" domain, to allow rights for read and write.
  
  `sudo nano /etc/ImageMagick-6/policy.xml`

  Original:
  
  `<policy domain="path" rights="none" pattern="@*"/>`

  Change:

  `<policy domain="path" rights="read | write" pattern="@*"/>`

- Ghostscript:

    `sudo apt install ghostscript` or `brew install ghostscript`

### [SoundFile](https://pysoundfile.readthedocs.io/en/latest/#installation)
   
- Linux: `sudo apt-get install libsndfile1-dev`
- MacOS, Windows: `pip install soundfile`


### Python dependencies
*Recommended: Create and activate a virtual environment before next steps[python venv, conda, pipenv].*

`pipenv install --skip-lock` (recommended) or `pip install -r requirements.txt`

Optional: Install PyGame, if wanting to run inline previews in notebooks

`pip install pygame`

## Usage


**Note:** To be able to upload to a YouTube account, you must first obtain a client_secrets.json file for the YouTube API,
 and store it in the wiki_movie/ directory.
See [Obtaining authorization credentials](https://developers.google.com/youtube/registering_an_application).



### Command Line

##### Simple usage:

    python main.py [-s SINGLE_PAGE  | -t | --url URL] -o


##### Examples:

    python main.py -s Boston -n py_tts -o
    
    python main.py --top25

    python main.py --url https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report/February_7_to_13,_2021

Required arguments:

    [-s | -t | --url]
    -s --single_page      Title of the article to process
    -t --top25            Use the top25 articles of the week
    --url                 URL of an article, which must contain a list/table of articles            


Optional arguments:

| Parameter                 | Default       | Description   |
| :------------------------ |:-------------:| :-------------|
| -n --narrator   |  sys_tts  | Speech generation engine (string). Accepted values: py_tts, google_tts, dc_tts |
| -o --overwrite  | True      | Flag, which if set, will overwrite any data of an article of the same name |
| -u --upload     | False     | Flag, upload created video to Youtube |
| -p --private    | False     | Flag, upload with 'private' viewing status |
| -d --delete_all | False     | Flag, delete assets(images, audio) after movie is created |
| --n_pages       | 25        | Integer, use with --url arg. Sets limit on number of article links to process from --url.

Narrator arguments:

So far, only arguments for the SystemNarrator have been implemented for the command line.

| Parameter                 | Default       | Description   |
| :------------------------ |:-------------:| :-------------|
| -v, --voice   | MacOS: Alex, Linux: na | narrator voice - available voices dependant on platform |
| -r --rate     | MacOS: 200, Linux: na | words spoken per minute |

ImageDownloader object arguments:

| Parameter                 | Default       | Description   |
| :------------------------ |:-------------:| :-------------|
| -i, --image_count         | 5             | Number of images to loop per article section |
| -c, connect_speed         | 'medium'      | How quickly to timeout scraping search results page |
| -w, --watch               | False         | Flag, run browser in non-headless mode |



 - The first run of `main.py` may prompt on the terminal for a key-code, which will be available in a browser window.

#### Description of available narrator arguments

- sys_tts: Automatically uses the OS built-in speech command
  - MacOSX: NS Speech Synthesizer
  - Linux: espeak
  - Windows: not implemented
- py_tts: Uses pyttsx3
- google_tts: Uses gTTS
- dc_tts: Deep Convolutional TTS
