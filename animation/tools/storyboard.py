"""Assemble rendered key frames into a labelled storyboard sheet.
usage: python3 tools/storyboard.py <episode>   (reads episodes/<ep>/storyboard.json)
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

ep = sys.argv[1]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
panels = json.load(open(os.path.join(root, 'episodes', ep, 'storyboard.json')))
stills = os.path.join(root, 'out', ep, 'stills')
PW, PH, NOTE, PAD, COLS = 880, 495, 150, 36, 2
rows = (len(panels) + COLS - 1) // COLS
sheet = Image.new('RGB', (PAD + COLS * (PW + PAD), 110 + rows * (PH + NOTE + PAD)), '#14121c')
d = ImageDraw.Draw(sheet)
F = lambda s, b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''), s)
d.text((PAD, 34), f'{ep}  ·  storyboard  ·  15s  ·  1920×1080 @ 24fps', font=F(30, True), fill='#f0e6d0')
for i, p in enumerate(panels):
    x = PAD + (i % COLS) * (PW + PAD)
    y = 110 + (i // COLS) * (PH + NOTE + PAD)
    im = Image.open(os.path.join(stills, 't%05.2f.png' % p['t'])).resize((PW, PH), Image.LANCZOS)
    sheet.paste(im, (x, y))
    d.text((x, y + PH + 12), f"{i+1}. {p['title']}   [{p['range']}]", font=F(22, True), fill='#ffd88a')
    yy = y + PH + 44
    for label, key in (('CAM', 'camera'), ('ACT', 'action'), ('SND', 'sound')):
        d.text((x, yy), label, font=F(17, True), fill='#9c93c9')
        d.text((x + 52, yy), p[key], font=F(17), fill='#d8d2e8')
        yy += 30
out = os.path.join(root, 'out', ep, 'storyboard.png')
sheet.save(out)
print(out)
