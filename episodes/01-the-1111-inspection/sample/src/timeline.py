# Shared timeline (seconds) for "The 11:11 Inspection" cold-open sample
DUR = 68.0
FPS = 24
W, H = 1920, 1080
BAR = 132  # letterbox bar height (≈2.39:1)

# shots: (name, start, end)
SHOTS = [
    ("clock_wide", 0.0, 4.5),
    ("hallway", 4.5, 13.0),
    ("clock_flip", 13.0, 17.0),
    ("door_knock", 17.0, 26.5),
    ("faces", 26.5, 29.6),
    ("door_push", 29.6, 34.2),
    ("handle", 34.2, 38.5),
    ("black", 38.5, 40.0),
    ("narration", 40.0, 55.0),
    ("title", 55.0, 62.0),
    ("dli", 62.0, 68.0),
]

FLIP = 15.6                 # 11:10 -> 11:11
KNOCKS = [18.0, 18.85, 19.7]
SILHOUETTE_IN = 22.0        # figure fades in behind the frosted glass
HANDLE_TURN = (35.0, 37.6)
CUT = 38.5

# voice cues: (file, start, subtitle, speaker)
VO = [
    ("dad1", 24.0, "Alex? ... It's Dad.", "VOICE OUTSIDE"),
    ("mara1", 27.7, "Don't.", "MARA"),
    ("dad2", 30.1, "Alex, please. I've been looking for you.", "VOICE OUTSIDE"),
    ("narr1", 40.3, "In Bellwether, everyone follows one rule.", "NARRATOR"),
    ("narr2", 43.7, "At exactly 11:11 PM, you never open your front door.", "NARRATOR"),
    ("narr3", 48.1, "Not for your friends. Not for your family.", "NARRATOR"),
    ("narr4", 51.4, "And especially... not for someone you thought was gone.", "NARRATOR"),
    ("dli", 62.6, "", "DLI"),
]
TITLE_HIT = 55.0
DLI_CHIME = 62.0
