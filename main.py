# Standard modules
import random
from sys import maxsize
from os import listdir, mkdir, path

# MoviePy modules
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip, concatenate_videoclips, vfx, VideoClip

from src import custom_effects

# Progress bars
from tqdm import tqdm

"""

    TODO:
        try to overlap videos more and distort them
        spread out audio duplication a bit, so they don't end up directly next to one another
"""

VIDEO_SOURCE_FOLDER = "input_video_sources"
AUDIO_SOURCE_FOLDER = "input_audio_sources"
IMAGE_SOURCE_FOLDER = "input_image_sources"

videoFiles = [VIDEO_SOURCE_FOLDER + "/" + vid for vid in listdir(VIDEO_SOURCE_FOLDER)]
audioFiles = [AUDIO_SOURCE_FOLDER + "/" + vid for vid in listdir(AUDIO_SOURCE_FOLDER)]
imageFiles = [IMAGE_SOURCE_FOLDER + "/" + vid for vid in listdir(IMAGE_SOURCE_FOLDER)]

# All video clips will be trimmed to be between these two lengths
# default: 0.4, 3.0 | chaos: 0.3, 1.2
video_clip_times = (0.4, 3.0)
# All audio clips will be trimmed to be between these two lengths
# default: 0.7, 3.0 | chaos: 0.2, 1.0
audio_clip_times = (0.7, 3.0)
# All image clips will be trimmed to be between these two lengths
# default: 0.3, 0.8 | chaos: 0.1, 0.5
image_clip_times = (0.3, 0.8)

# Audio amount multiplier (based off the amount of videos)
# e.g. 60 videos with a multiplier of 0.75 means 45 audio clips will be put into the final result.
# default: 0.75 | chaos: 1.5
AUDIO_AMOUNT_MULTIPLIER = 0.75

# Image amount multiplier (pretty much ditto as audio amount multiplier)
# default: 0.6 | chaos: 2.0
IMAGE_AMOUNT_MULTIPLIER = 2

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
while not chosenSeed.isdecimal() and chosenSeed not in ("any", "skip", "default", "time"):
    chosenSeed = input("Video seed (or 'any' to pick one automatically): ")

seed = int(chosenSeed) if chosenSeed.isdecimal() else random.randrange(maxsize) #get a chosen or random seed to use and reference later

print(f"Chose seed: {seed}")

rng = random.Random(seed)

print("")
print(f"Found {len(videoFiles)} videos and {len(audioFiles)} sounds")

videoEffects = [
    # Speed up or slow down
    (vfx.MultiplySpeed(rng.uniform(*random_speed_amount)),),
    # Mirror horizontally
    (vfx.MirrorX(),),
    # Reverse the video
    (vfx.TimeMirror(),),
    # 1. Play the clip forwards and then backwards
    # 2. Speed up both clips a bit
    (vfx.TimeSymmetrize(), vfx.MultiplySpeed(rng.uniform(1.4, 2.3))),
    # Change contrast
    (vfx.LumContrast(lum=0, contrast=rng.uniform(*contrast_amount)),),

    # Custom effects we use to mimic various YTP-like effects
    (custom_effects.RepeatMultiple(rng, *repeat_video_amount),),
    (custom_effects.ContinuousFlipVideo(rng, *continuous_flip_amount),),
    (custom_effects.ShuffleVideo(rng, *shuffle_video_amount),),
    (custom_effects.FlipRotationVideo(rng, *flip_rotation_amount),)
]

videoObjects = []
audioObjects = []
imageObjects = []

videoAmount = input("Amount of videos: ")
while not videoAmount.isdecimal():
    videoAmount = input("Amount of videos: ")

videoAmount = int(videoAmount)

shouldUseEffects = input("Apply video effects? (y/n): ")
while shouldUseEffects.lower() not in ("y", "yes", "true", "n", "no", "false"):
    shouldUseEffects = input("Apply video effects? (y/n): ")

shouldUseEffects = True if shouldUseEffects.lower() in ("y", "yes", "true") else False

randomVideos = rng.sample(videoFiles, min(videoAmount, len(videoFiles)))
#randomVideos = rng.choices(videoFiles, k=min(videoAmount, len(videoFiles)))
if videoAmount > len(videoFiles): #if there is a higher chosen amount than total, re-use videos
    videoAmountToAdd = videoAmount - len(videoFiles)
    print(f"Chosen video amount is higher than available video amount - re-using {videoAmountToAdd} videos...")
    additionalVideos = rng.choices(videoFiles, k=videoAmountToAdd)
    randomVideos += additionalVideos

print("")

with tqdm(desc="Compiling videos", total=len(randomVideos)) as pbar:
    for index, video in enumerate(randomVideos):
        newClip = VideoFileClip(video)
        sizedClip = newClip.with_effects([vfx.Resize(height=480)])

        randomDuration = rng.uniform(*video_clip_times)
        if sizedClip.duration > randomDuration:
            startOffset = rng.uniform(0, sizedClip.duration - randomDuration)
            sizedClip = sizedClip.subclipped(startOffset, startOffset+randomDuration)

        if rng.choice([True, True, False]) and shouldUseEffects:
            # Apply a random effect to this video
            effect_to_use = rng.choice(videoEffects)

            sizedClip = sizedClip.with_effects(effect_to_use)

        videoObjects.append(sizedClip)

        pbar.update(1)

print("Finished compiling videos.")

finalVideo: VideoClip = concatenate_videoclips(videoObjects, method="compose")

audioAmount = int(videoAmount*AUDIO_AMOUNT_MULTIPLIER)

randomSounds = rng.sample(audioFiles, min(audioAmount, len(audioFiles)))

if audioAmount > len(audioFiles):
    audioAmountToAdd = audioAmount - len(audioFiles)
    print(f"Chosen audio amount is higher than available audio amount - re-using {audioAmountToAdd} audio sources...")
    additionalAudio = rng.choices(audioFiles, k=audioAmountToAdd)
    randomSounds += additionalAudio

print("")

copiedSoundAmount = 0
with tqdm(desc="Compiling sounds", total=len(randomSounds)) as pbar:
    for index, audio in enumerate(randomSounds):
        newClip = AudioFileClip(audio)
        # Modify the volume of audio clips so that they (hopefully) won't drown out
        #  the audio coming from the video clips
        newClip = newClip.with_volume_scaled(0.6)

        if newClip.duration > 5: #for long clips
            randomDuration = rng.uniform(*audio_clip_times) # crop audio duration
            # if the audio is longer than the cropped duration, crop the audio at a random position
            if newClip.duration > randomDuration:
                #either use a random offset, or start at beginning of audio clip
                startOffset = rng.choice([rng.uniform(0, newClip.duration - randomDuration), 0])
                newClip = newClip.subclipped(startOffset, startOffset+randomDuration)

            newClip = newClip.with_start(rng.uniform(0, finalVideo.duration-newClip.duration)) # move audio around video length
            audioObjects.append(newClip)
        else:
            # Place to position the audio clip - could be anywhere from the final video's start all the way to its full duration
            clipPosition = rng.uniform(0, finalVideo.duration - newClip.duration)

            newClip = newClip.with_start(clipPosition) # move audio around video length
            audioObjects.append(newClip)

            # Add duplicates of this audio clip
            for i in range(rng.randint(1, 5)):
                copiedSoundAmount += 1

                dupe_clip_position = clipPosition + ((i * 0.9) * rng.uniform(0.8, 1.2))
                # If the duplicate clip goes over the final video duration, simply discard that duplicate clip
                if dupe_clip_position > finalVideo.duration:
                    continue

                """# Max 0 and clip position - 2 so it doesn't go into negative clip position (if near beginning of video)
                minimumRange = max(0, clipPosition - 2)
                # Minimum between final video duration and clip position + 2 so it doesn't go over video length (if near end of video)
                maximumRange = min(finalVideo.duration, clipPosition + 2) - newClip.duration

                copiedClip = newClip.with_start(rng.uniform(minimumRange, maximumRange)) # move audio around video length"""
                copiedClip = newClip.with_start(dupe_clip_position)
                audioObjects.append(copiedClip)

        pbar.update(1)

print(f"Finished compiling audio. Added {copiedSoundAmount} duplicate sounds, total {audioAmount+copiedSoundAmount}.")

imageAmount = int(videoAmount * IMAGE_AMOUNT_MULTIPLIER)

randomImages = rng.sample(imageFiles, k=min(audioAmount, len(imageFiles)))

if imageAmount > len(imageFiles):
    imageAmountToAdd = imageAmount - len(imageFiles)
    print(f"Chosen image amount is higher than available image amount - re-using {imageAmountToAdd} image sources...")
    additionalImages = rng.choices(imageFiles, k=imageAmountToAdd)
    randomImages += additionalImages

print("")

with tqdm(desc="Compiling images", total=len(randomImages)) as pbar:
    for index, imagePath in enumerate(randomImages):
        # Load the image as a clip
        clipDuration = rng.uniform(*image_clip_times)
        newClip = ImageClip(imagePath, duration=clipDuration)
        
        # Resize the image randomly, relative to the video's output resolution
        clipWidthNormal = rng.uniform(0.15, 1)
        clipWidth = int(finalVideo.w * clipWidthNormal)
        clipHeightNormal = rng.uniform(0.15, 1)
        clipHeight = int(finalVideo.h * clipHeightNormal)
        newClip = newClip.with_effects([vfx.Resize((clipWidth, clipHeight))])

        # Place the image randomly (coordinates-wise) in the final video
        clipOffsetXNormal = rng.uniform(0, 1)
        clipOffsetX = min(
            int(finalVideo.w * clipOffsetXNormal),
            finalVideo.w - clipWidth
        )
        clipOffsetYNormal = rng.uniform(0, 1)
        clipOffsetY = min(
            int(finalVideo.h * clipOffsetYNormal),
            finalVideo.h - clipHeight
        )
        newClip = newClip.with_position((clipOffsetX, clipOffsetY))

        # Place the image at a random spot (duration-wise) in the final video
        newClip = newClip.with_start(rng.uniform(0, finalVideo.duration - newClip.duration))

        imageObjects.append(newClip)

        pbar.update(1)

finalVideo = CompositeVideoClip([finalVideo] + imageObjects)

# The video's filename
finalVideoFilename = f"output/result_seed-{seed}_{videoAmount}{'_effects' if shouldUseEffects else ''}.mp4"

# Create output directory if it doesn't exist
if not path.exists("output"):
    mkdir("output")

print("")
print("Rendering final video...")
print("")
finalVideo.audio = CompositeAudioClip([finalVideo.audio] + audioObjects)
finalVideo.write_videofile(
    finalVideoFilename,
    fps=30,
    preset="faster",
    codec="libx264",
    pixel_format="yuv420p",
    audio_codec="libmp3lame",
    audio_bitrate="96k"
)

# Close all file streams
for video in videoObjects:
    video.close()
for audio in audioObjects:
    audio.close()
for image in imageObjects:
    image.close()
