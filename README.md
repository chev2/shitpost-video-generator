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

## How to use
1. Put a list of desired video sources into the `input_video_sources/` directory, and a list of desired audio sources into the `input_audio_sources` directory. I recommend keeping the video file formats the same, but it shouldn't matter. The resolution of videos does not matter, either.
2. Run the script (`python3 main.py`), and choose a seed if you want to reproduce the same video. Otherwise, type 'any' to choose a random seed.
3. Choose the amount of videos you want the script to merge together to produce the final result. I recommend 30 for roughly minute-long videos.
4. The script will do the rest, and generate the final video in the root directory, which will be formatted as `result_seed-<seed>_<number-of-videos>_<effects-enabled>.mp4`.

## Performance
This script uses moviepy - due to the amount of ffmpeg processes moviepy opens from this script, it has really high memory usage. I have seen this script use upwards of about ~2.5GB of memory for 40 random loaded videos. I don't know of a way around this.

## Requirements
- Python `3.8` or greater (this project was tested on Python `3.8`).
- Python module `moviepy`
