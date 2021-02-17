## Video Creater From Wikipedia


### Installation:

Install firefox, geckodriver:

`sudo apt install firefox`

`sudo apt-get install firefox-geckodriver`

Or use homebrew.

`brew install --cask firefox'
`brew install geckodriver`

(Selenium installs with python dependencies in requirements.txt)


Install [ImageMagick](https://imagemagick.org/script/download.php), and [Ghostscript](https://www.ghostscript.com/doc/9.53.3/Install.htm)
    
- method depends on operating system (Linux, macOS, Windows)
- Linux:
    
    `sudo apt install imagemagick` or `brew install imagemagick`
  
    You may need to alter the policy.xml file of ImageMagick. To find where the file is located, run:
    
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

Install [SoundFile](https://pysoundfile.readthedocs.io/en/latest/#installation)
   
- Linux: `sudo apt-get install libsndfile1-dev`
- MacOS, Windows: `pip install soundfile`

*Recommended: Create and activate a virtual environment before next steps[python venv, conda, pipenv].*

Install python dependencies

`pip install -r requirements`

Optional: Install PyGame, if wanting to run inline previews in notebooks

`pip install pygame`

Notes:
 - Python above 3.7.6 is unstable
 - First run of `create.py` may prompt for a key-code.