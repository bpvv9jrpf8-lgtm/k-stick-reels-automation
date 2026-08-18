import json, math, pathlib, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
EP = json.loads((ROOT/'episode.json').read_text())
W,H,FPS = 720,1280,30
DUR=float(EP['duration'])
OUT=ROOT/'silent_vehicle.mp4'

try:
    F_BIG=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',52)
    F_SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
except:
    F_BIG=F_SMALL=ImageFont.load_default()

SKY=(177,224,255); GRASS=(116,194,86); ROAD=(104,111,120); MUD=(110,72,42)

def clamp(v,a=0,b=1): return max(a,min(b,v))
def lerp(a,b,t): return a+(b-a)*t
def smooth(t):
    t=clamp(t); return t*t*(3-2*t)
def beat_at(t):
    for b in EP['beats']:
        if b['start']<=t<b['end']: return b
    return EP['beats'][-1]
def local_p(b,t): return clamp((t-b['start'])/(b['end']-b['start']))

def background(draw, b, t):
    draw.rectangle((0,0,W,H),fill=SKY)
    for cx,cy,s in [(110,170,1.0),(510,130,0.8)]:
        draw.ellipse((cx-55*s,cy-22*s,cx+15*s,cy+28*s),fill='white')
        draw.ellipse((cx-10*s,cy-38*s,cx+60*s,cy+26*s),fill='white')
        draw.ellipse((cx+35*s,cy-18*s,cx+90*s,cy+28*s),fill='white')
    draw.rectangle((0,520,W,820),fill=GRASS)
    draw.pieslice((-180,300,380,760),180,360,fill=(94,172,77))
    draw.pieslice((330,330,930,790),180,360,fill=(87,164,75))
    draw.polygon([(0,760),(W,710),(W,H),(0,H)],fill=ROAD)
    for x in range(-100,900,180):
        draw.rounded_rectangle((x,980,x+90,997),8,fill=(246,225,100))
    if b.get('scene')=='mud':
        draw.ellipse((235,920,495,1075),fill=(89,58,37),outline=(70,44,29),width=6)
        draw.ellipse((275,946,455,1048),fill=MUD)
        for i in range(5):
            xx=292+i*35
            draw.ellipse((xx,970+(i%2)*18,xx+28,985+(i%2)*18),fill=(130,87,49))


def wheel(draw, cx, cy, r, rot):
    draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(30,33,38),outline=(10,10,12),width=5)
    draw.ellipse((cx-r*0.55,cy-r*0.55,cx+r*0.55,cy+r*0.55),fill=(185,192,198),outline=(70,74,80),width=4)
    for a in [0,math.pi/2]:
        aa=a+rot
        dx=math.cos(aa)*r*0.5; dy=math.sin(aa)*r*0.5
        draw.line((cx-dx,cy-dy,cx+dx,cy+dy),fill=(70,74,80),width=4)


def eyes(draw, x, y, scale, emotion='happy', look=0):
    ew,eh=32*scale,42*scale
    for off in [-22,22]:
        cx=x+off*scale
        draw.ellipse((cx-ew/2,y-eh/2,cx+ew/2,y+eh/2),fill='white',outline=(35,45,60),width=max(2,int(3*scale)))
        px=cx+look*7*scale
        py=y+(7*scale if emotion=='sad' else 2*scale)
        rr=8*scale
        draw.ellipse((px-rr,py-rr,px+rr,py+rr),fill=(25,35,45))
        draw.ellipse((px-rr*0.35,py-rr*0.45,px,py-rr*0.1),fill='white')
    if emotion in ('worried','sad'):
        draw.line((x-42*scale,y-36*scale,x-10*scale,y-46*scale),fill=(35,45,60),width=max(3,int(5*scale)))
        draw.line((x+10*scale,y-46*scale,x+42*scale,y-36*scale),fill=(35,45,60),width=max(3,int(5*scale)))
        draw.arc((x-26*scale,y+38*scale,x+26*scale,y+70*scale),180,360,fill=(35,45,60),width=max(3,int(5*scale)))
    elif emotion=='shocked':
        draw.ellipse((x-10*scale,y+40*scale,x+10*scale,y+65*scale),fill=(35,45,60))
    elif emotion in ('laughing','happy','excited','hopeful'):
        draw.arc((x-28*scale,y+30*scale,x+28*scale,y+66*scale),0,180,fill=(35,45,60),width=max(3,int(5*scale)))
    else:
        draw.line((x-18*scale,y+52*scale,x+18*scale,y+52*scale),fill=(35,45,60),width=max(3,int(4*scale)))


def car(draw, x, y, color, emotion, p, action, scale=1.0, kind='car'):
    bounce=0; wheel_rot=0
    if action in ('drive','drive_left','tow','pull'):
        bounce=math.sin(p*math.pi*10)*5*scale; wheel_rot=p*math.pi*12
    elif action=='spin':
        bounce=math.sin(p*math.pi*18)*8*scale; wheel_rot=p*math.pi*28
    elif action in ('celebrate','laugh'):
        bounce=abs(math.sin(p*math.pi*7))*14*scale
    elif action=='bounce':
        bounce=abs(math.sin(p*math.pi*5))*10*scale
    x=float(x); y=float(y-bounce)
    draw.ellipse((x-110*scale,y+72*scale,x+110*scale,y+100*scale),fill=(73,76,81))
    wheel(draw,x-70*scale,y+62*scale,30*scale,wheel_rot)
    wheel(draw,x+70*scale,y+62*scale,30*scale,wheel_rot)
    if kind=='car':
        draw.rounded_rectangle((x-115*scale,y-18*scale,x+115*scale,y+65*scale),22*scale,fill=color,outline=(45,52,60),width=max(4,int(6*scale)))
        draw.polygon([(x-68*scale,y-20*scale),(x-36*scale,y-78*scale),(x+54*scale,y-78*scale),(x+88*scale,y-20*scale)],fill=color,outline=(45,52,60))
        draw.rounded_rectangle((x-33*scale,y-69*scale,x+48*scale,y-26*scale),10*scale,fill=(176,225,250),outline=(55,80,100),width=max(3,int(4*scale)))
        eyes(draw,x+8*scale,y-48*scale,0.62*scale,emotion,look=0.35)
    elif kind=='truck':
        draw.rounded_rectangle((x-125*scale,y-12*scale,x+15*scale,y+65*scale),18*scale,fill=(195,35,42),outline=(45,52,60),width=max(4,int(6*scale)))
        draw.rounded_rectangle((x-15*scale,y-70*scale,x+105*scale,y+65*scale),18*scale,fill=color,outline=(45,52,60),width=max(4,int(6*scale)))
        draw.rounded_rectangle((x+5*scale,y-56*scale,x+86*scale,y-12*scale),10*scale,fill=(176,225,250),outline=(55,80,100),width=max(3,int(4*scale)))
        draw.rectangle((x-90*scale,y-42*scale,x-30*scale,y-20*scale),fill=(245,245,245))
        draw.rectangle((x-70*scale,y-62*scale,x-50*scale,y-2*scale),fill=(245,245,245))
        eyes(draw,x+45*scale,y-35*scale,0.55*scale,emotion,look=-0.15)
        draw.rounded_rectangle((x+25*scale,y-90*scale,x+62*scale,y-72*scale),8*scale,fill=(255,196,55),outline=(80,70,30),width=3)
    else:
        draw.rounded_rectangle((x-105*scale,y-10*scale,x+90*scale,y+65*scale),18*scale,fill=color,outline=(45,52,60),width=max(4,int(6*scale)))
        draw.polygon([(x-125*scale,y-73*scale),(x+15*scale,y-73*scale),(x+45*scale,y-12*scale),(x-105*scale,y-12*scale)],fill=(244,188,35),outline=(45,52,60))
        draw.rounded_rectangle((x+30*scale,y-62*scale,x+105*scale,y+65*scale),16*scale,fill=(252,199,45),outline=(45,52,60),width=max(4,int(6*scale)))
        draw.rounded_rectangle((x+42*scale,y-49*scale,x+92*scale,y-12*scale),8*scale,fill=(176,225,250),outline=(55,80,100),width=max(3,int(4*scale)))
        eyes(draw,x+67*scale,y-33*scale,0.48*scale,emotion,look=-0.2)
    draw.rounded_rectangle((x-112*scale,y+44*scale,x-76*scale,y+56*scale),5*scale,fill=(230,235,238))
    return (x,y)


def state_for(name,b,t):
    s=b.get(name)
    if not s: return None
    p=local_p(b,t)
    x=s.get('x',0.5); tx=s.get('to',x)
    if 'to' in s: x=lerp(x,tx,smooth(p))
    return {'x':x,'p':p,'action':s.get('action','idle'),'emotion':s.get('emotion','happy')}


def camera(im,b,t):
    cam=b.get('camera','wide'); p=local_p(b,t)
    if cam=='wide': return im
    zoom=1.0; cx=W/2; cy=830
    if cam=='medium': zoom=1.12
    elif cam=='push_blue': zoom=1.12+0.18*smooth(p); cx=W*0.48
    elif cam=='punch_yellow': zoom=1.15+0.28*smooth(p); cx=W*0.47
    nw,nh=int(W/zoom),int(H/zoom)
    left=int(clamp(cx-nw/2,0,W-nw)); top=int(clamp(cy-nh/2,0,H-nh))
    return im.crop((left,top,left+nw,top+nh)).resize((W,H),Image.Resampling.LANCZOS)

proc=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(OUT)],stdin=subprocess.PIPE)

for fi in range(int(DUR*FPS)):
    t=fi/FPS; b=beat_at(t)
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    background(d,b,t)
    st_blue=state_for('blue',b,t); st_red=state_for('red',b,t); st_yellow=state_for('yellow',b,t)
    pos={}
    if st_blue: pos['blue']=car(d,st_blue['x']*W,870,(55,135,235),st_blue['emotion'],st_blue['p'],st_blue['action'],1.0,'car')
    if st_red: pos['red']=car(d,st_red['x']*W,845,(225,53,57),st_red['emotion'],st_red['p'],st_red['action'],1.03,'truck')
    if st_yellow: pos['yellow']=car(d,st_yellow['x']*W,850,(250,195,45),st_yellow['emotion'],st_yellow['p'],st_yellow['action'],1.03,'dump')
    if b.get('tow') and 'blue' in pos and 'red' in pos:
        bx,by=pos['blue']; rx,ry=pos['red']
        d.line((bx+112,by+38,rx-130,ry+38),fill=(70,55,40),width=8)
        d.ellipse((bx+103,by+29,bx+121,by+47),outline=(230,195,80),width=5)
        d.ellipse((rx-139,ry+29,rx-121,ry+47),outline=(230,195,80),width=5)
    for key,st in [('blue',st_blue),('yellow',st_yellow)]:
        if st and st['action']=='spin' and key in pos:
            x,y=pos[key]
            for j in range(7):
                a=(j/7)*math.pi
                rr=45+35*abs(math.sin(st['p']*math.pi*10+j))
                sx=x-65+math.cos(a)*rr; sy=y+70-math.sin(a)*rr
                d.ellipse((sx-9,sy-7,sx+9,sy+7),fill=(120,78,44))
    if t<2.2:
        txt=EP['hook']; box=d.textbbox((0,0),txt,font=F_BIG); tw=box[2]-box[0]
        d.rounded_rectangle((W/2-tw/2-26,50,W/2+tw/2+26,126),22,fill=(24,28,35))
        d.text((W/2-tw/2,61),txt,font=F_BIG,fill='white')
    if 8.3<t<10.3 and st_red:
        d.rounded_rectangle((405,250,675,302),16,fill=(255,255,255))
        d.text((430,260),'RESCUE TRUCK!',font=F_SMALL,fill=(200,40,45))
    if 22.2<t<24.2 and st_yellow:
        d.rounded_rectangle((35,250,315,302),16,fill=(255,255,255))
        d.text((62,260),'DUMP TRUCK!',font=F_SMALL,fill=(190,140,20))
    im=camera(im,b,t)
    proc.stdin.write(im.tobytes())
proc.stdin.close(); rc=proc.wait()
if rc!=0: raise SystemExit(rc)
print(OUT)
