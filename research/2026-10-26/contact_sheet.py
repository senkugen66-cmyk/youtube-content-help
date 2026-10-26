import sys
from PIL import Image, ImageDraw
src, out, w, cols = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
items = [a.split("=",1) for a in sys.argv[5:]]
h = w*9//16; pad = 22
rows = (len(items)+cols-1)//cols
sheet = Image.new("RGB", (cols*(w+8)+8, rows*(h+pad+8)+8), "white")
d = ImageDraw.Draw(sheet)
for i,(vid,label) in enumerate(items):
    im = Image.open(f"{src}/{vid}.jpg").convert("RGB")
    # center-crop to 16:9 (hqdefault has letterbox bars)
    W,H = im.size; th = W*9//16
    if H > th: im = im.crop((0,(H-th)//2,W,(H-th)//2+th))
    im = im.resize((w,h), Image.LANCZOS)
    x = 8 + (i%cols)*(w+8); y = 8 + (i//cols)*(h+pad+8)
    sheet.paste(im,(x,y+pad)); d.text((x,y+4), label, fill="black")
sheet.save(out, quality=90)
