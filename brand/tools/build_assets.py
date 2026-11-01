#!/usr/bin/env python3
"""
MeowDude asset generator.

Every mascot pose, annotation and UI prop is built from the SAME geometry
defined in this file, so proportions, outlines and colours never drift
between videos. Edit the constants here, re-run, and every SVG updates:

    python3 brand/tools/build_assets.py

Output: brand/mascot/*.svg, brand/annotations/*.svg, brand/ui/*.svg
"""
from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --------------------------------------------------------------------------
# Palette — keep in sync with brand/tokens.json. Flat fills only.
# --------------------------------------------------------------------------
INK = "#17161F"        # every outline, all text, eyes
PAPER = "#ECEAF3"      # light video ground, belly screen
NIGHT = "#22223A"      # dark video ground
TANGERINE = "#FF7A2F"  # MeowDude's body. Reserved for the mascot + logo.
MARKER = "#FFD84A"     # highlight / emphasis
SIGNAL = "#3EC5E8"     # UI, "do this", interactive
ALERT = "#FF5C8A"      # warning, "don't do this"

# --------------------------------------------------------------------------
# Line weights at 1x (the mascot canvas is drawn for ~330px tall).
# Scale the whole SVG, never individual strokes.
# --------------------------------------------------------------------------
W_BODY = 6      # silhouette outline
W_DETAIL = 5    # screen, crease, mouth, hands
W_LIMB = 6      # arms, legs, tail
W_NOTE = 5      # annotations
W_MARK = 9      # check / cross marks

MASCOT_VIEWBOX = "-30 0 320 330"

# One closed path: head, body and both ears. The right ear is folded —
# that bent ear is the single most recognisable part of the silhouette.
SILHOUETTE = (
    "M 70 262 "
    "C 60 220, 58 160, 64 112 "     # left flank
    "L 74 34 "                       # left ear tip (sharp)
    "L 118 80 "                      # left ear inner base
    "Q 140 74, 160 80 "              # crown
    "L 190 44 "                      # right ear rises...
    "L 210 58 "                      # ...and folds outward (flat top)
    "L 200 116 "                     # back to the head
    "C 210 168, 208 222, 198 262 "  # right flank
    "C 192 286, 162 292, 134 292 "  # base
    "C 104 292, 76 288, 70 262 Z"
)
EAR_CREASE = "M 190 46 L 195 82"

SCREEN = dict(x=100, y=196, w=68, h=58, rx=12)  # the belly HUD
SCREEN_CX, SCREEN_CY = 134, 225

LEGS = "M 112 290 L 110 308 L 98 308 M 158 290 L 160 308 L 172 308"

# --------------------------------------------------------------------------
# Expression parts
# --------------------------------------------------------------------------
def eyes_pill(dx=0, dy=0, h=28):
    off = (28 - h) / 2
    return (
        f'<rect x="{104+dx}" y="{128+dy+off}" width="15" height="{h}" rx="7.5" fill="{INK}"/>'
        f'<rect x="{148+dx}" y="{126+dy+off}" width="15" height="{h}" rx="7.5" fill="{INK}"/>'
    )


def eyes_happy():
    return (
        f'<path d="M 102 148 Q 111 132 120 148 M 146 146 Q 155 130 164 146" '
        f'fill="none" stroke="{INK}" stroke-width="{W_DETAIL+1}" stroke-linecap="round"/>'
    )


def eyes_squeeze():
    return (
        f'<path d="M 102 130 L 118 141 L 102 152 M 164 128 L 148 139 L 164 150" '
        f'fill="none" stroke="{INK}" stroke-width="{W_DETAIL+1}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
    )


def eyes_flat():  # deadpan / unimpressed half-lids
    return (
        f'<path d="M 102 140 L 120 140 M 146 138 L 164 138" fill="none" stroke="{INK}" '
        f'stroke-width="{W_DETAIL+1}" stroke-linecap="round"/>'
        f'<rect x="104" y="140" width="15" height="12" rx="6" fill="{INK}"/>'
        f'<rect x="148" y="138" width="15" height="12" rx="6" fill="{INK}"/>'
    )


def stroke(d, w=W_DETAIL, color=INK):
    return (
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
    )


MOUTH = {
    "cat": stroke("M 122 174 q 6 7 12 0 q 6 7 12 0"),
    "open": f'<path d="M 123 171 Q 134 194 146 171 Z" fill="{INK}" stroke="{INK}" '
            f'stroke-width="{W_DETAIL}" stroke-linejoin="round"/>',
    "wobble": stroke("M 119 178 q 5 -5 10 0 q 5 5 10 0 q 5 -5 10 0"),
    "smirk": stroke("M 124 177 q 12 6 24 -6"),
}

# --------------------------------------------------------------------------
# Belly screen: its colour shows MeowDude's state, the glyph shows content.
# --------------------------------------------------------------------------
GLYPH = {
    "play": f'<path d="M 126 211 L 126 239 L 149 225 Z" fill="{INK}" '
            f'stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>',
    "arrow": stroke("M 116 225 H 151 M 140 213 L 152 225 L 140 237", W_DETAIL + 1),
    "dots": "".join(f'<circle cx="{x}" cy="225" r="4.5" fill="{INK}"/>' for x in (119, 134, 149)),
    "check": stroke("M 117 226 L 129 238 L 152 211", W_DETAIL + 2),
    "bang": stroke("M 134 208 L 134 230", W_DETAIL + 2) + f'<circle cx="134" cy="241" r="4.5" fill="{INK}"/>',
    "none": "",
}


def screen(fill, glyph):
    s = SCREEN
    return (
        f'<rect x="{s["x"]}" y="{s["y"]}" width="{s["w"]}" height="{s["h"]}" rx="{s["rx"]}" '
        f'fill="{fill}" stroke="{INK}" stroke-width="{W_DETAIL}"/>' + GLYPH[glyph]
    )


# --------------------------------------------------------------------------
# Limbs: single-weight ink lines ("noodle limbs") ending in round mittens.
# --------------------------------------------------------------------------
def hand(x, y):
    return f'<circle cx="{x}" cy="{y}" r="9" fill="{TANGERINE}" stroke="{INK}" stroke-width="{W_DETAIL}"/>'


def arm(d, end):
    return stroke(d, W_LIMB) + (hand(*end) if end else "")


ARMS = {
    "down_l": ("M 66 198 C 50 214, 46 234, 50 250", (50, 252)),
    "down_r": ("M 202 198 C 216 214, 216 234, 210 248", (209, 251)),
    "hip_l": ("M 66 200 C 42 204, 40 228, 62 232", (62, 232)),
    "point_r": ("M 202 192 C 228 182, 248 160, 262 140", (264, 137)),
    "chin_r": ("M 202 204 C 190 222, 166 212, 160 190", (158, 184)),
    "up_l": ("M 68 186 C 44 168, 36 140, 40 112", (40, 108)),
    "up_r": ("M 200 186 C 224 168, 232 140, 228 112", (228, 108)),
    "head_r": ("M 202 196 C 232 176, 232 130, 208 112", (206, 110)),
    "shrug_l": ("M 66 196 C 40 196, 30 176, 26 160", (24, 156)),
    "shrug_r": ("M 202 196 C 228 196, 238 176, 242 160", (244, 156)),
}


def arrowhead(tip, direction, length=24, width=22):
    """Filled tangerine triangle — MeowDude's pointer tail tip."""
    dx, dy = direction
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    tx, ty = tip[0] + ux * length * 0.75, tip[1] + uy * length * 0.75
    bx, by = tip[0] - ux * length * 0.25, tip[1] - uy * length * 0.25
    pts = [
        (tx, ty),
        (bx + px * width / 2, by + py * width / 2),
        (bx - px * width / 2, by - py * width / 2),
    ]
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (
        f'<polygon points="{p}" fill="{TANGERINE}" stroke="{INK}" '
        f'stroke-width="{W_DETAIL}" stroke-linejoin="round"/>'
    )


def tail(d, end, ctrl):
    return stroke(d, W_LIMB) + arrowhead(end, (end[0] - ctrl[0], end[1] - ctrl[1]))


TAILS = {
    "up": ("M 196 256 C 236 262, 252 222, 238 192", (238, 192), (252, 222)),
    "point": ("M 196 256 C 236 260, 262 250, 276 230", (276, 230), (262, 250)),
    "high": ("M 196 256 C 240 262, 252 214, 252 180", (252, 180), (252, 214)),
    "droop": ("M 196 258 C 230 266, 250 276, 262 298", (262, 298), (250, 276)),
}

# --------------------------------------------------------------------------
# Poses. Each one is a recurring "beat" in a tutorial.
# --------------------------------------------------------------------------
POSES = {
    "neutral": dict(eyes=eyes_pill(), mouth="cat", arms=("down_l", "down_r"),
                    tail="up", screen=(PAPER, "play"),
                    use="Default. Intros, listening, idle between beats."),
    "point": dict(eyes=eyes_pill(dx=4), mouth="smirk", arms=("hip_l", "point_r"),
                  tail="point", screen=(SIGNAL, "arrow"),
                  use="Directing attention to a UI element or map location."),
    "think": dict(eyes=eyes_pill(dx=-3, dy=-6), mouth="wobble", arms=("down_l", "chin_r"),
                  tail="up", screen=(PAPER, "dots"),
                  use="Setting up a problem or a question."),
    "hype": dict(eyes=eyes_happy(), mouth="open", arms=("up_l", "up_r"),
                 tail="high", screen=(MARKER, "check"),
                 use="Payoff: the trick worked, the secret is revealed."),
    "oops": dict(eyes=eyes_squeeze(), mouth="wobble", arms=("down_l", "head_r"),
                 tail="droop", screen=(ALERT, "bang"),
                 use="Common mistake, warning, what NOT to do."),
    "deadpan": dict(eyes=eyes_flat(), mouth="smirk", arms=("shrug_l", "shrug_r"),
                    tail="up", screen=(PAPER, "none"),
                    use="Dry humour, 'well, that happened', obvious bad idea."),
}


def mascot_group(pose: dict) -> str:
    parts = []
    parts.append(tail(*TAILS[pose["tail"]]))           # tail sits behind the body
    parts.append(stroke(LEGS, W_LIMB))
    parts.append(
        f'<path d="{SILHOUETTE}" fill="{TANGERINE}" stroke="{INK}" '
        f'stroke-width="{W_BODY}" stroke-linejoin="round"/>'
    )
    parts.append(stroke(EAR_CREASE))
    parts.append(pose["eyes"])
    parts.append(MOUTH[pose["mouth"]])
    parts.append(screen(*pose["screen"]))
    for key in pose["arms"]:                            # arms on top
        parts.append(arm(*ARMS[key]))
    return "\n  ".join(parts)


def svg(viewbox: str, body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" role="img">\n'
        f"  <title>{title}</title>\n  {body}\n</svg>\n"
    )


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print("wrote", path.relative_to(ROOT.parent))


# --------------------------------------------------------------------------
# Annotations: hand-drawn marks, always the same stroke weight.
# --------------------------------------------------------------------------
ANNOTATIONS = {
    "arrow-curve": ("0 0 200 120", INK, W_NOTE,
                    "M 14 100 C 40 30, 120 14, 178 46 M 154 28 L 180 48 L 150 62"),
    "arrow-straight": ("0 0 200 60", INK, W_NOTE,
                       "M 12 34 C 70 28, 120 31, 182 26 M 162 10 L 184 26 L 164 44"),
    "arrow-loop": ("0 0 220 140", INK, W_NOTE,
                   "M 12 110 C 40 120, 70 110, 84 82 C 96 54, 60 40, 56 70 "
                   "C 52 100, 120 112, 196 58 M 172 50 L 198 56 L 186 80"),
    "circle-scribble": ("0 0 240 140", INK, W_NOTE,
                        "M 40 30 C 110 6, 220 22, 222 72 C 224 120, 120 132, 60 116 "
                        "C 14 104, 12 54, 60 34 C 82 26, 106 24, 124 27"),
    "underline": ("0 0 240 40", INK, W_NOTE, "M 10 24 C 60 16, 130 30, 230 18"),
    "underline-double": ("0 0 240 50", INK, W_NOTE,
                         "M 10 20 C 60 14, 130 26, 230 16 M 24 36 C 80 30, 150 40, 218 32"),
    "bracket": ("0 0 40 120", INK, W_NOTE,
                "M 30 8 C 14 8, 18 50, 6 60 C 18 70, 14 112, 30 112"),
    "emphasis-ticks": ("0 0 60 60", INK, W_NOTE,
                       "M 22 50 L 6 44 M 28 30 L 14 14 M 46 22 L 44 6"),
    "check": ("0 0 100 100", SIGNAL, W_MARK, "M 16 54 L 40 80 L 86 18"),
    "cross": ("0 0 100 100", ALERT, W_MARK, "M 20 18 L 82 84 M 80 16 L 22 82"),
}

HIGHLIGHT = f'<path d="M 6 14 L 234 6 L 230 46 L 10 52 Z" fill="{MARKER}"/>'


def build_annotations():
    for name, (vb, color, w, d) in ANNOTATIONS.items():
        write(ROOT / "annotations" / f"{name}.svg", svg(vb, stroke(d, w, color), f"MeowDude {name}"))
    write(ROOT / "annotations" / "highlight.svg", svg("0 0 240 58", HIGHLIGHT, "MeowDude marker highlight"))


# --------------------------------------------------------------------------
# UI props: flat, outlined, consistent with the mascot.
# --------------------------------------------------------------------------
def build_ui():
    key = (
        f'<rect x="6" y="10" width="88" height="84" rx="16" fill="{INK}"/>'
        f'<rect x="6" y="6" width="88" height="78" rx="16" fill="{PAPER}" stroke="{INK}" stroke-width="{W_DETAIL}"/>'
    )
    write(ROOT / "ui" / "key.svg", svg("0 0 100 100", key, "Key cap (add the letter in the edit)"))
    wide = (
        f'<rect x="6" y="10" width="228" height="84" rx="16" fill="{INK}"/>'
        f'<rect x="6" y="6" width="228" height="78" rx="16" fill="{PAPER}" stroke="{INK}" stroke-width="{W_DETAIL}"/>'
    )
    write(ROOT / "ui" / "key-wide.svg", svg("0 0 240 100", wide, "Wide key cap (Space, Shift, Ctrl)"))
    mouse = (
        f'<path d="M 50 8 C 22 8, 12 30, 12 60 L 12 104 C 12 132, 30 150, 50 150 '
        f'C 70 150, 88 132, 88 104 L 88 60 C 88 30, 78 8, 50 8 Z" fill="{PAPER}" '
        f'stroke="{INK}" stroke-width="{W_DETAIL}"/>'
        f'<path d="M 50 8 C 22 8, 12 30, 12 60 L 12 70 L 50 70 Z" fill="{SIGNAL}" '
        f'stroke="{INK}" stroke-width="{W_DETAIL}" stroke-linejoin="round"/>'
        + stroke("M 50 8 L 50 70 M 12 70 L 88 70")
    )
    write(ROOT / "ui" / "mouse-left.svg", svg("0 0 100 160", mouse, "Mouse, left click"))
    mouse_r = mouse.replace(
        "M 50 8 C 22 8, 12 30, 12 60 L 12 70 L 50 70 Z", "M 50 8 C 78 8, 88 30, 88 60 L 88 70 L 50 70 Z"
    )
    write(ROOT / "ui" / "mouse-right.svg", svg("0 0 100 160", mouse_r, "Mouse, right click"))
    cursor = (
        f'<path d="M 14 8 L 14 82 L 32 64 L 46 94 L 60 88 L 46 58 L 72 58 Z" fill="{PAPER}" '
        f'stroke="{INK}" stroke-width="{W_DETAIL}" stroke-linejoin="round"/>'
    )
    write(ROOT / "ui" / "cursor.svg", svg("0 0 86 104", cursor, "Pointer cursor"))
    button = (
        f'<circle cx="50" cy="54" r="40" fill="{INK}"/>'
        f'<circle cx="50" cy="48" r="40" fill="{SIGNAL}" stroke="{INK}" stroke-width="{W_DETAIL}"/>'
    )
    write(ROOT / "ui" / "pad-button.svg", svg("0 0 100 100", button, "Controller face button (add the glyph)"))
    panel = (
        f'<rect x="6" y="6" width="388" height="208" rx="18" fill="{PAPER}" stroke="{INK}" stroke-width="{W_DETAIL}"/>'
        f'<path d="M 6 52 L 394 52" stroke="{INK}" stroke-width="{W_DETAIL}"/>'
        + "".join(f'<circle cx="{x}" cy="29" r="7" fill="{c}" stroke="{INK}" stroke-width="3"/>'
                  for x, c in ((32, ALERT), (56, MARKER), (80, SIGNAL)))
    )
    write(ROOT / "ui" / "panel.svg", svg("0 0 400 220", panel, "Simplified game UI panel"))


def build_mascot():
    for name, pose in POSES.items():
        write(ROOT / "mascot" / f"meowdude-{name}.svg",
              svg(MASCOT_VIEWBOX, mascot_group(pose), f"MeowDude — {name}"))
    # Channel avatar: neutral pose cropped to the head on the dark ground.
    head = mascot_group(POSES["neutral"])
    avatar = (
        f'<circle cx="200" cy="200" r="200" fill="{NIGHT}"/>'
        f'<g transform="translate(200 222) scale(1.5) translate(-136 -150)">{head}</g>'
    )
    write(ROOT / "mascot" / "meowdude-avatar.svg",
          f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" role="img">'
          f'<title>MeowDude avatar</title><defs><clipPath id="c"><circle cx="200" cy="200" r="200"/></clipPath></defs>'
          f'<g clip-path="url(#c)">{avatar}</g></svg>\n')
    # Silhouette-only mark: for watermarks and end cards.
    mark = f'<path d="{SILHOUETTE}" fill="{INK}"/>'
    write(ROOT / "mascot" / "meowdude-silhouette.svg", svg("56 26 162 274", mark, "MeowDude silhouette mark"))
    # Construction sheet: the proportion rules drawn on top of the neutral pose.
    E = 28  # one "eye" — the unit every proportion is measured in
    grid = "".join(
        f'<line x1="-30" y1="{y}" x2="290" y2="{y}" stroke="{SIGNAL}" stroke-width="1.5" stroke-dasharray="4 6"/>'
        for y in range(34, 34 + 11 * E, E)
    )
    marks = (
        f'<line x1="64" y1="318" x2="208" y2="318" stroke="{ALERT}" stroke-width="3"/>'
        f'<text x="136" y="328" font-family="Archivo, Arial, sans-serif" font-size="11" font-weight="700" '
        f'text-anchor="middle" fill="{INK}">5 E wide</text>'
        f'<line x1="-18" y1="34" x2="-18" y2="308" stroke="{ALERT}" stroke-width="3"/>'
        f'<text x="-22" y="171" font-family="Archivo, Arial, sans-serif" font-size="11" font-weight="700" '
        f'text-anchor="middle" fill="{INK}" transform="rotate(-90 -22 171)">10 E tall</text>'
    )
    write(ROOT / "mascot" / "meowdude-construction.svg",
          svg("-40 0 340 336", f'<rect x="-40" y="0" width="340" height="336" fill="{PAPER}"/>'
              + grid + mascot_group(POSES["neutral"]) + marks, "MeowDude construction sheet"))


if __name__ == "__main__":
    build_mascot()
    build_annotations()
    build_ui()
