# Standard modules
import random
from dataclasses import dataclass

# MoviePy modules
from moviepy import concatenate_videoclips, Effect, vfx
from moviepy.Clip import Clip

@dataclass
class ContinuousFlipVideo(Effect):
    """Flip a video on its X-axis or Y-axis at random."""

    rng: random.Random
    flip_amount_min: int = 1
    flip_amount_max: int = 7

    def apply(self, clip: Clip): #flip a video multiple times over its duration
        #how many times the clip will be flipped
        flip_amt = self.rng.randint(self.flip_amount_min, self.flip_amount_max)
        #random periods at which to shuffle
        flip_periods = [self.rng.uniform(0, clip.duration) for _ in range(flip_amt)]

        flip_periods.sort() #in ascending order
        all_clips = []
        last_period = 0

        for period in flip_periods:
            new_clip = clip.subclipped(last_period, period)
            all_clips.append(new_clip)
            last_period = period

        new_clip = clip.subclipped(last_period, clip.duration)
        all_clips.append(new_clip)

        for i in range(len(all_clips)):
            # Either flip on the X, or Y, or don't flip at all
            effect_to_use = self.rng.choice((vfx.MirrorX(), vfx.MirrorY(), None))

            if effect_to_use is not None:
                all_clips[i] = all_clips[i].with_effects((effect_to_use,))

        final_clip = concatenate_videoclips(all_clips)

        return final_clip

@dataclass
class RepeatMultiple(Effect):
    """Repeat a video clip multiple times in quick succession."""

    rng: random.Random
    repeat_video_duration_min: float = 0.01
    repeat_video_duration_max: float = 2

    def apply(self, clip: Clip) -> Clip:
        random_dur = self.rng.uniform(self.repeat_video_duration_min, self.repeat_video_duration_max)
        repeat_amt = int((clip.duration / random_dur) * 0.5)

        start_offset = self.rng.uniform(0, clip.duration - random_dur)
        new_clip = clip.subclipped(start_offset, start_offset + random_dur)

        final_clip = concatenate_videoclips([new_clip]*repeat_amt)
        return final_clip

@dataclass
class ShuffleVideo(Effect):
    """Splice a video into multiple parts and then shuffle those parts."""

    rng: random.Random
    shuffle_amount_min: int = 20
    shuffle_amount_max: int = 50

    def apply(self, clip: Clip):
        #how many times the clip will be split and shuffled
        shuffle_amt = self.rng.randint(self.shuffle_amount_min, self.shuffle_amount_max)
        #random periods at which to shuffle
        shuffle_periods = [self.rng.uniform(0, clip.duration) for _ in range(shuffle_amt)]

        shuffle_periods.sort() #in ascending order
        all_clips = []
        last_period = 0

        for period in shuffle_periods:
            new_clip = clip.subclipped(last_period, period)
            all_clips.append(new_clip)
            last_period = period

        new_clip = clip.subclipped(last_period, clip.duration)
        all_clips.append(new_clip)
        self.rng.shuffle(all_clips) #shuffle around the clips to get the final result
        final_clip = concatenate_videoclips(all_clips)

        return final_clip

@dataclass
class FlipRotationVideo(Effect):
    """Makes a clip mimic rotation by duplicating the clip, then reversing and flipping that second clip."""

    rng: random.Random
    flip_rotation_min: int = 1
    flip_rotation_max: int = 4

    def apply(self, clip: Clip):
        random_duration = self.rng.uniform(0.1, 0.3)

        start_offset = self.rng.uniform(0, clip.duration - random_duration)
        first_clip = clip.subclipped(start_offset, start_offset+random_duration)

        # Flip horizontal, then reverse video
        second_clip = first_clip.copy().with_effects((vfx.MirrorX(), vfx.TimeMirror()))

        # Speed up the clips
        first_clip = first_clip.with_effects((vfx.MultiplySpeed(1.5),))
        second_clip = second_clip.with_effects((vfx.MultiplySpeed(1.5),))

        # Number of times to do this flip-rotation
        flip_rotation_count = self.rng.randint(self.flip_rotation_min, self.flip_rotation_max)

        return concatenate_videoclips([first_clip, second_clip] * flip_rotation_count)

