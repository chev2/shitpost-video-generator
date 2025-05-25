# Standard modules
import random
from sys import maxsize
from os import listdir, mkdir, path

# MoviePy modules
import moviepy.audio
from moviepy import editor
from moviepy.video import fx
from moviepy.video.fx import resize

"""
    TODO:
        flash random images in short bursts at long intervals
        try to overlap videos more and distort them
        spread out audio duplication a bit, so they don't end up directly next to one another
"""

VIDEO_SOURCE_FOLDER = "input_video_sources"
AUDIO_SOURCE_FOLDER = "input_audio_sources"

videoFiles = [VIDEO_SOURCE_FOLDER + "/" + vid for vid in listdir(VIDEO_SOURCE_FOLDER)]
audioFiles = [AUDIO_SOURCE_FOLDER + "/" + vid for vid in listdir(AUDIO_SOURCE_FOLDER)]

# All video clips will be trimmed to be between these two lengths
# default: 0.5, 3.5 | chaos: 0.3, 1.2
video_clip_times = (0.4, 0.8)
# All audio clips will be trimemd to be between these two lengths
# default: 0.7, 13. chaos: 0.7, 3.0
audio_clip_times = (0.7, 3.0)

# Audio amount multiplier (based off the amount of videos)
# e.g. 60 videos with a multiplier of 0.75 means 45 audio clips will be put into the final result.
# default: 0.75. chaos: 1.5
AUDIO_AMOUNT_MULTIPLIER = 1.5

# (min, max) random values range, inclusive
#integer. default: 1, 7
continuous_flip_amount = (1, 7)

#float. default: 0.01, 0.2
repeat_video_amount = (0.01, 0.2)

#integer. default: 20, 50
shuffle_video_amount = (20, 50)

#integer. default: 1, 4
flip_rotation_amount = (1, 4)

#float. default: 0.7, 3
random_speed_amount = (0.7, 3)

#float. default: 0.3, 2
contrast_amount = (0.3, 2)

chosenSeed = input("Video seed (or 'any' to pick one automatically): ")
while not chosenSeed.isdecimal() and not chosenSeed in ["any", "skip", "default", "time"]:
    chosenSeed = input("Video seed (or 'any' to pick one automatically): ")

seed = int(chosenSeed) if chosenSeed.isdecimal() else random.randrange(maxsize) #get a chosen or random seed to use and reference later

print(f"Chose seed: {seed}")

rng = random.Random(seed)

print("")
print(f"Found {len(videoFiles)} videos and {len(audioFiles)} sounds")

# Returns a progress bar string, useful for measuring progress in command-line
def get_progress_bar_str(current_index, max_index, progress_bar_len:int = 20, include_percent:bool = True, percent_digits:int = 2,
                symbol_middle:str = "█", symbol_begin:str = "|", symbol_end:str = "|"):
    # Used for the progress bar - gets progress 0-1 range,
    # then multiplies it by the progress bar length
    percent_done = int(current_index / max_index * progress_bar_len)

    percentage = f" {round((current_index / max_index) * 100, percent_digits)}%" if include_percent else ""

    return symbol_begin + (symbol_middle * percent_done + " " * (progress_bar_len - percent_done)) + symbol_end + percentage

def ContinuousFlipVideo(clip): #flip a video multiple times over its duration
    #how many times the clip will be flipped
    flip_amt = rng.randint(*continuous_flip_amount)
    #random periods at which to shuffle
    flip_periods = [rng.uniform(0, clip.duration) for _ in range(flip_amt)]

    flip_periods.sort() #in ascending order
    all_clips = []
    last_period = 0

    for period in flip_periods:
        new_clip = clip.subclip(last_period, period)
        all_clips.append(new_clip)
        last_period = period

    new_clip = clip.subclip(last_period, clip.duration)
    all_clips.append(new_clip)

    for i in range(len(all_clips)):
        clip = all_clips[i]
        all_clips[i] = rng.choice([fx.mirror_x.mirror_x, fx.mirror_y.mirror_y, lambda v: v])(all_clips[i]) #flip on the x, or y, or don't flip

    final_clip = editor.concatenate_videoclips(all_clips)

    return final_clip

def RepeatVideo(clip): #repeat a video multiple times
    random_dur = rng.uniform(*repeat_video_amount)
    repeat_amt = int((clip.duration/random_dur)*0.5)

    start_offset = rng.uniform(0, clip.duration - random_dur)
    new_clip = clip.subclip(start_offset, start_offset+random_dur)

    final_clip = editor.concatenate_videoclips([new_clip]*repeat_amt)
    return final_clip

def ShuffleVideo(clip): #take a clip, split it into multiple parts, shuffle those parts
    #how many times the clip will be split and shuffled
    shuffle_amt = rng.randint(*shuffle_video_amount)
    #random periods at which to shuffle
    shuffle_periods = [rng.uniform(0, clip.duration) for _ in range(shuffle_amt)]

    shuffle_periods.sort() #in ascending order
    all_clips = []
    last_period = 0

    for period in shuffle_periods:
        new_clip = clip.subclip(last_period, period)
        all_clips.append(new_clip)
        last_period = period

    new_clip = clip.subclip(last_period, clip.duration)
    all_clips.append(new_clip)
    rng.shuffle(all_clips) #shuffle around the clips to get the final result
    final_clip = editor.concatenate_videoclips(all_clips)

    return final_clip

def FlipRotationVideo(clip): #makes the clip "rotate" by flipping and reversing the second part of the clip
    random_duration = rng.uniform(0.1, 0.3)

    start_offset = rng.uniform(0, clip.duration - random_duration)
    first_clip = clip.subclip(start_offset, start_offset+random_duration)

    second_clip = fx.time_mirror.time_mirror(fx.mirror_x.mirror_x(first_clip.copy())) #flip horizontal, then reverse video

    both_clips = [fx.speedx.speedx(first_clip, 1.5), fx.speedx.speedx(second_clip, 1.5)]

    return editor.concatenate_videoclips(both_clips*random.randint(*flip_rotation_amount))

videoEffects = [
    lambda v: fx.speedx.speedx(v, rng.uniform(*random_speed_amount)), #speed up/slow down
    lambda v: fx.mirror_x.mirror_x(v), #mirror on the x axis
    lambda v: fx.time_mirror.time_mirror(v), #reverse the video
    lambda v: v.fx(fx.time_symmetrize.time_symmetrize).fx(fx.speedx.speedx, factor=rng.uniform(1.4, 2.3)), #forward + reverse with speed up
    lambda v: RepeatVideo(v), #repeat the video multiple times
    lambda v: ShuffleVideo(v), #shuffle up parts of the video for a glitch-like effect
    lambda v: ContinuousFlipVideo(v), #flip the video on the x and y axis multiple times
    lambda v: FlipRotationVideo(v),
    lambda v: fx.lum_contrast.lum_contrast(v, lum=0, contrast=rng.uniform(*contrast_amount)) #change contrast
]

videoObjects = []
audioObjects = []

videoAmount = input("Amount of videos: ")
while not videoAmount.isdecimal():
    videoAmount = input("Amount of videos: ")

videoAmount = int(videoAmount)

shouldUseEffects = input("Apply video effects? (y/n): ")
while not shouldUseEffects.lower() in ["y", "yes", "true", "n", "no", "false"]:
    shouldUseEffects = input("Apply video effects? (y/n): ")

shouldUseEffects = True if shouldUseEffects.lower() in ["y", "yes", "true"] else False

randomVideos = rng.sample(videoFiles, min(videoAmount, len(videoFiles)))
#randomVideos = rng.choices(videoFiles, k=min(videoAmount, len(videoFiles)))
if videoAmount > len(videoFiles): #if there is a higher chosen amount than total, re-use videos
    videoAmountToAdd = videoAmount - len(videoFiles)
    print(f"Chosen video amount is higher than available video amount - re-using {videoAmountToAdd} videos...")
    additionalVideos = rng.choices(videoFiles, k=videoAmountToAdd)
    randomVideos += additionalVideos

print("")
print(f"Compiling {videoAmount} videos... ", end="\r")

for index, video in enumerate(randomVideos):
    print(f"Compiling {videoAmount} videos... {get_progress_bar_str(index, len(randomVideos), progress_bar_len=40)}", end="\r")

    newClip = editor.VideoFileClip(video)
    sizedClip = fx.resize.resize(newClip, height=480)

    randomDuration = rng.uniform(*video_clip_times)
    if sizedClip.duration > randomDuration:
        startOffset = rng.uniform(0, sizedClip.duration - randomDuration)
        sizedClip = sizedClip.subclip(startOffset, startOffset+randomDuration)

    if rng.choice([True, True, False]) and shouldUseEffects:
        sizedClip = rng.choice(videoEffects)(sizedClip) #apply a random effect

    videoObjects.append(sizedClip)

print(f"Compiling {videoAmount} videos... {get_progress_bar_str(1, 1, progress_bar_len=40)}")
print("Finished compiling videos.")

finalVideo = editor.concatenate_videoclips(videoObjects, method="compose") # method="compose"

audioAmount = int(videoAmount*audio_multiplier)

randomSounds = rng.sample(audioFiles, min(audioAmount, len(audioFiles)))

if audioAmount > len(audioFiles):
    audioAmountToAdd = audioAmount - len(audioFiles)
    print(f"Chosen audio amount is higher than available audio amount - re-using {audioAmountToAdd} audio sources...")
    additionalAudio = rng.choices(audioFiles, k=audioAmountToAdd)
    randomSounds += additionalAudio

print("")
print(f"Compiling {audioAmount} sounds...", end="\r")

copiedSoundAmount = 0
for index, audio in enumerate(randomSounds):
    print(f"Compiling {audioAmount} sounds... {get_progress_bar_str(index, len(randomSounds), progress_bar_len=40)}", end="\r")

    newClip = editor.AudioFileClip(audio)
    newClip = moviepy.audio.fx.volumex.volumex(newClip, 0.8) # modify volume

    if newClip.duration > 5: #for long clips
        randomDuration = rng.uniform(*audio_clip_times) # crop audio duration
        # if the audio is longer than the cropped duration, crop the audio at a random position
        if newClip.duration > randomDuration:
            #either use a random offset, or start at beginning of audio clip
            startOffset = rng.choice([rng.uniform(0, newClip.duration - randomDuration), 0])
            newClip = newClip.subclip(startOffset, startOffset+randomDuration)

        newClip = newClip.set_start(rng.uniform(0, finalVideo.duration-newClip.duration)) # move audio around video length
        audioObjects.append(newClip)
    else:
        # Place to position the audio clip - could be anywhere from the final video's start all the way to its full duration
        clipPosition = rng.uniform(0, finalVideo.duration-newClip.duration)

        newClip = newClip.set_start(clipPosition) # move audio around video length
        audioObjects.append(newClip)

        # Add duplicates of this audio clip
        for i in range(rng.randint(1, 5)):
            copiedSoundAmount += 1

            # Max 0 and clip position - 2 so it doesn't go into negative clip position (if near beginning of video)
            minimumRange = max(0, clipPosition - 2)
            # Minimum between final video duration and clip position + 2 so it doesn't go over video length (if near end of video)
            maximumRange = min(finalVideo.duration, clipPosition + 2) - newClip.duration

            copiedClip = newClip.set_start(rng.uniform(minimumRange, maximumRange)) # move audio around video length
            audioObjects.append(copiedClip)

print(f"Compiling {audioAmount} sounds... {get_progress_bar_str(1, 1, progress_bar_len=40)}")
print(f"Finished compiling audio. Added {copiedSoundAmount} duplicate sounds, total {audioAmount+copiedSoundAmount}.")

# The video's filename
finalVideoFilename = f"output/result_seed-{seed}_{videoAmount}{'_effects' if shouldUseEffects else ''}.mp4"

# Create output directory if it doesn't exist
if not path.exists("output"): mkdir("output")

print("")
print("Rendering final video...")
print("")
finalVideo.audio = editor.CompositeAudioClip([finalVideo.audio] + audioObjects)
finalVideo.write_videofile(finalVideoFilename, fps=30, audio_bitrate="96k")

# Close all file streams
for video in videoObjects:
    video.close()
for audio in audioObjects:
    audio.close()
