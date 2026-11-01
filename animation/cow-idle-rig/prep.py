import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter
SRC, OUT = sys.argv[1], sys.argv[2]
im = Image.open(SRC).convert('RGB')
X0,Y0,X1,Y1 = 160,15,485,795
c = im.crop((X0,Y0,X1,Y1))
a = np.asarray(c).astype(np.int16)
# background = near-white region connected to the crop border
white = (a.min(axis=2) > 228).astype(np.uint8)*255
wm = white>0
bg = np.zeros_like(wm); bg[0,:]=wm[0,:]; bg[-1,:]=wm[-1,:]; bg[:,0]=wm[:,0]; bg[:,-1]=wm[:,-1]
H,W = wm.shape
while True:
    g = bg.copy()
    g[1:]|=bg[:-1]; g[:-1]|=bg[1:]; g[:,1:]|=bg[:,:-1]; g[:,:-1]|=bg[:,1:]
    g &= wm
    if (g==bg).all(): break
    bg = g
# soft edge: grow background mask by anti-aliased amount based on brightness
lum = a.mean(axis=2)
alpha = np.where(bg, 0.0, 1.0)
# pixels next to background: alpha from darkness (line anti-aliasing against white)
near = np.asarray(Image.fromarray((bg*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)))>0
edge = near & ~bg
alpha[edge] = np.clip((255-lum[edge])/(255-150),0,1)
# un-mix white from edge colours: c = a*fg + (1-a)*255
fg = a.astype(np.float32)
with np.errstate(divide='ignore', invalid='ignore'):
    unm = (fg - (1-alpha[...,None])*255)/np.maximum(alpha[...,None],1e-3)
fg = np.where(edge[...,None], np.clip(unm,0,255), fg)
yy_,xx_ = np.mgrid[0:alpha.shape[0],0:alpha.shape[1]]
alpha[((xx_+X0)>462)&((yy_+Y0)<600)] = 0   # drop the back-view figure
rgba = np.dstack([fg, alpha*255]).astype(np.uint8)
# tail tuft layer (crop coords): dark pixels left of the right leg
tx0,ty0,tx1,ty1 = 330-X0, 555-Y0, 388-X0, 610-Y0
tail = np.zeros_like(rgba)
yy,xx = np.mgrid[0:rgba.shape[0],0:rgba.shape[1]]
skin = (a[...,0]-a[...,2] > 18) & (a.mean(2) > 150)
tm = (xx>=tx0)&(xx<tx1-2)&(yy>=ty0)&(yy<ty1)&(rgba[...,3]>0)&~skin
tail[tm] = rgba[tm]
rgba[tm,3] = 0
Image.fromarray(rgba,'RGBA').save(OUT+'/body.png')
Image.fromarray(tail,'RGBA').save(OUT+'/tail.png')
prev = Image.new('RGBA', (W,H), (255,120,180,255))
prev.alpha_composite(Image.fromarray(tail,'RGBA')); prev.alpha_composite(Image.fromarray(rgba,'RGBA'))
prev.save(OUT+'/matte_check.png')
t = Image.new('RGBA',(W,H),(80,200,255,255)); t.alpha_composite(Image.fromarray(tail,'RGBA'))
t.crop((tx0-10,ty0-10,tx1+20,ty1+10)).resize(((tx1-tx0+30)*5,(ty1-ty0+20)*5),Image.NEAREST).save(OUT+'/tail_check.png')
