import moviepy.audio
import random
from sys import maxsize
from os import listdir
from moviepy import editor
from moviepy.video import fx

videoSourceFolder = "VideoSources"
audioSourceFolder = "AudioSources"

videoFiles = [videoSourceFolder + "/" + vid for vid in listdir(videoSourceFolder)]
audioFiles = [audioSourceFolder + "/" + vid for vid in listdir(audioSourceFolder)]

chosenSeed = input("Video seed (or 'any' to use system time): ")
while not chosenSeed.isdecimal() and not chosenSeed in ["any", "skip", "default", "time"]:
    chosenSeed = input("Video seed (or 'any' to use system time): ")

seed = int(chosenSeed) if chosenSeed.isdecimal() else random.randrange(maxsize) #get a chosen or random seed to use and reference later

print(f'Chose seed: {seed}')

rng = random.Random(seed)

print(f'Found {len(videoFiles)} videos and {len(audioFiles)} sounds')

def ContinuousFlipVideo(clip): #flip a video multiple times over its duration
    flipAmount = rng.randint(1, 7) #how many times the clip will be flipped
    flipPeriods = [rng.uniform(0, clip.duration) for _ in range(flipAmount)] #random periods at which to shuffle

    flipPeriods.sort() #in ascending order
    allClips = []
    lastPeriod = 0

    for period in flipPeriods:
        newClip = clip.subclip(lastPeriod, period)
        allClips.append(newClip)
        lastPeriod = period

    newClip = clip.subclip(lastPeriod, clip.duration)
    allClips.append(newClip)

    for i in range(len(allClips)):
        clip = allClips[i]
        allClips[i] = rng.choice([fx.mirror_x.mirror_x, fx.mirror_y.mirror_y, lambda v: v])(allClips[i]) #flip on the x, or y, or don't flip

    finalClip = editor.concatenate_videoclips(allClips)

    return finalClip

def RepeatVideo(clip): #repeat a video multiple times
    randomDuration = rng.uniform(0.01, 0.2)
    repeatAmount = int((clip.duration/randomDuration)*0.5)

    startOffset = rng.uniform(0, clip.duration - randomDuration)
    newClip = clip.subclip(startOffset, startOffset+randomDuration)

    finalClip = editor.concatenate_videoclips([newClip]*repeatAmount)
    return finalClip

def ShuffleVideo(clip): #take a clip, split it into multiple parts, shuffle those parts
    shuffleAmount = rng.randint(20, 50) #how many times the clip will be split and shuffled
    shufflePeriods = [rng.uniform(0, clip.duration) for _ in range(shuffleAmount)] #random periods at which to shuffle

    shufflePeriods.sort() #in ascending order
    allClips = []
    lastPeriod = 0

    for period in shufflePeriods:
        newClip = clip.subclip(lastPeriod, period)
        allClips.append(newClip)
        lastPeriod = period

    newClip = clip.subclip(lastPeriod, clip.duration)
    allClips.append(newClip)
    rng.shuffle(allClips) #shuffle around the clips to get the final result
    finalClip = editor.concatenate_videoclips(allClips)

    return finalClip

videoEffects = [
    lambda v: fx.speedx.speedx(v, rng.uniform(0.7, 3)), #speed up/slow down
    lambda v: fx.mirror_x.mirror_x(v), #mirror on the x axis
    lambda v: fx.time_mirror.time_mirror(v), #reverse the video
    lambda v: v.fx(fx.time_symmetrize.time_symmetrize).fx(fx.speedx.speedx, factor=rng.uniform(1.4, 2.3)), #forward + reverse with speed up
    lambda v: RepeatVideo(v), #repeat the video multiple times
    lambda v: ShuffleVideo(v), #shuffle up parts of the video for a glitch-like effect
    lambda v: ContinuousFlipVideo(v), #flip the video on the x and y axis multiple times
    lambda v: fx.lum_contrast.lum_contrast(v, lum=0, contrast=rng.uniform(0.3, 2)) #change contrast
]

videoObjects = []
audioObjects = []

videoAmount = input("Amount of videos: ")
while not videoAmount.isdecimal():
    videoAmount = input("Amount of videos: ")

videoAmount = int(videoAmount)

shouldUseEffects = input("Apply video effects? (y/n): ")
while not shouldUseEffects in ["y", "yes", "true", "n", "no", "false"]:
    shouldUseEffects = input("Apply video effects? (y/n): ")

shouldUseEffects = True if shouldUseEffects in ["y", "yes", "true"] else False

randomVideos = rng.sample(videoFiles, min(videoAmount, len(videoFiles)))
if videoAmount > len(videoFiles): #if there is a higher chosen amount than total, re-use videos
    videoAmountToAdd = videoAmount - len(videoFiles)
    print(f'Chosen video amount is higher than available video amount - re-using {videoAmountToAdd} videos...')
    additionalVideos = rng.choices(videoFiles, k=videoAmountToAdd)
    randomVideos += additionalVideos

print(f"Compiling {videoAmount} videos...", end="")

for video in randomVideos:
    print(".", end="")

    newClip = editor.VideoFileClip(video).resize(height=480) #target_resolution=(512, 512)

    randomDuration = rng.uniform(0.5, 3.5) #0.5, 2.6
    if newClip.duration > randomDuration:
        startOffset = rng.uniform(0, newClip.duration - randomDuration)
        newClip = newClip.subclip(startOffset, startOffset+randomDuration)

    if rng.choice([True, True, False]) and shouldUseEffects:
        newClip = rng.choice(videoEffects)(newClip) #apply a random effect

    videoObjects.append(newClip)

print("Finished compiling videos.")

finalVideo = editor.concatenate_videoclips(videoObjects, method="compose") # method="compose"

audioAmount = int(videoAmount*0.75)

randomSounds = rng.sample(audioFiles, min(audioAmount, len(audioFiles)))

if audioAmount > len(audioFiles):
    audioAmountToAdd = audioAmount - len(audioFiles)
    print(f'Chosen audio amount is higher than available audio amount - re-using {audioAmountToAdd} audio sources...')
    additionalAudio = rng.choices(audioFiles, k=audioAmountToAdd)
    randomSounds += additionalAudio

print(f"Compiling {audioAmount} sounds...", end="")

copiedSoundAmount = 0
for audio in randomSounds:
    print(".", end="")

    newClip = editor.AudioFileClip(audio)
    newClip = moviepy.audio.fx.volumex.volumex(newClip, 0.5) # modify volume

    if newClip.duration > 5: #for long clips
        randomDuration = rng.uniform(0.7, 13) # crop audio duration
        if newClip.duration > randomDuration: # if the audio is longer than the cropped duration, crop the audio at a random position
            startOffset = rng.choice([rng.uniform(0, newClip.duration - randomDuration), 0]) #either use a random offset, or start at beginning of audio clip
            newClip = newClip.subclip(startOffset, startOffset+randomDuration)

        newClip = newClip.set_start(rng.uniform(0, finalVideo.duration-newClip.duration)) # move audio around video length
        audioObjects.append(newClip)
    else:
        clipPosition = rng.uniform(0, finalVideo.duration-newClip.duration)

        newClip = newClip.set_start(clipPosition) # move audio around video length
        audioObjects.append(newClip)
        for i in range(rng.randint(1, 5)): #add a copy of the clip near the original clip
            print(".", end="")
            copiedSoundAmount += 1

            minimumRange = max(0, clipPosition-2)
            maximumRange = min(finalVideo.duration, clipPosition+2) - newClip.duration

            copiedClip = newClip.set_start(rng.uniform(minimumRange, maximumRange)) # move audio around video length
            audioObjects.append(copiedClip)

print(f"Finished compiling audio. Added {copiedSoundAmount} duplicate sounds, total {audioAmount+copiedSoundAmount}.")

newAudioClip = editor.CompositeAudioClip([finalVideo.audio] + audioObjects)

finalVideoFilename = f'final_result_{seed}_{videoAmount}{"_effects" if shouldUseEffects else ""}.mp4'

finalVideo.audio = newAudioClip
finalVideo.write_videofile(finalVideoFilename, fps=30, audio_bitrate="96k")

for video in videoObjects:
    video.close()
for audio in audioObjects:
    audio.close()
