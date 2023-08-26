# TODO: Enhance audio feedback to provide more specific cues.
# Suggestions: Different sounds for different errors, voice feedback with card name, etc.

import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Paths to audio files
NO_MATCH_SOUND = "no_match.mp3"
OLD_MATCH_SOUND = "old_match.mp3"
NEW_MATCH_SOUND = "new_match.mp3"

def play_sound(sound_path):
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
