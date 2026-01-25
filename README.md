# shitpost-video-generator
Generates an output video with overlayed audio and effects using a list of audio and video inputs.

## How it works
Here's how it works:
1. Gets all video & audio sources to use from the `input_video_sources/` and `input_audio_sources/` directories. This is where you put your sources.
2. Gets a seed for the random number generator, which can be used if a user wants to re-generate the same exact video again.
3. Chooses _n_ random videos where _n_ is the number of videos the user wants to merge into the final results (e.g. if you want to merge 40 different videos, it chooses 40 random videos). The script will first to attempt to avoid duplicate videos. If the chosen video amount is higher than the available videos, then the script will add duplicate videos to meet that amount.
4. Applies a bunch of random effects to the video files, which include trimming the video to be a random short length, mirroring the video, speeding it up or slowing it down, reversing the video, as well as other effects.
5. Merges all the now effect-applied videos into one big video.
6. Applies effects to the audio files, which include trimming the audio to be a random short length. The script will also attempt to repeat audio clips less than 5 seconds to give a repetitive-like nature to the end result.
7. The merged video clip & merged audio clip is then merged together to produce the final result, which is put into the `output/` directory.

## Requirements
Python `3.9` or greater is required. This project has been tested on Python `3.11`.

### uv

**uv** is the recommended installation method. You can find how to install uv [here](https://docs.astral.sh/uv/getting-started/installation/).

After uv is installed, simply run `uv run main.py` in whatever folder you downloaded this from. That's all!

### pip

If you'd prefer to use traditional pip/venv:

1. Ensure you're using a compatible Python version: `python --version`
2. Remove any existing virtual environment if it exists. (Usually `venv/` or `.venv/`)
3. Create a new virtual environment: `python -m pip venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install MoviePy: `pip install moviepy==2.2.1 tqdm`
6. Run the script with `python main.py`

## How to use
Please take a look at the **requirements** above before following these steps. **uv** is the recommended install method.

1. Download the GitHub repo (click the green 'code' button, then 'Download ZIP') and extract it somewhere.
2. Put a list of desired video sources into the `input_video_sources/` directory, and a list of desired audio sources into the `input_audio_sources` directory. I recommend keeping the video file formats the same, but it shouldn't matter. The resolution of videos does not matter, either.
3. Run the script, and choose a seed if you want to reproduce the same video later. Otherwise, type 'any' to choose a random seed.
4. Choose the amount of videos you want the script to merge together to produce the final result.
5. The script will do the rest, and generate the final video in the root directory, which will be formatted as `result_seed-<seed>_<number-of-videos>_<effects-enabled>.mp4`.

## Performance
This script uses moviepy - due to the amount of ffmpeg processes moviepy opens from this script, it has really high memory usage. I have seen this script use upwards of about ~2.5GB of memory for 40 random loaded videos. I don't know of a way around this.
