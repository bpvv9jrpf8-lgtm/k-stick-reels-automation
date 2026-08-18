import json, math, pathlib, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
episode = json.loads((ROOT/'episode.json').read_text())
W,H,FPS = 720,1280,30
DUR = float(episode['duration'])
OUT = ROOT/'silent_v3.mp4'

try:
    FONT_BIG = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 54)
    FONT_MED = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 42)
except:
    FONT_BIG = FONT_MED = ImageFont.load_default()

COLORS={'kstick':(232,58,58),'zippy':(45,118,230),'mimi':(242,196,56)}

def clamp(x,a=0,b=1): return max(a,min(b,x))
def ease(t): t=clamp(t); return t*t*(3-2*t)
def lerp(a,b,t): return a+(b-a)*t

def active_beat(t):
    for b in episode['beats']:
        if b['start'] <= t < b['end']: return b
    return episode['beats'][-1]

def char_state(cid,t,b):
    act=next((a for a in b.get('actions',[]) if a['character']==cid),None)
    if not act:
        return None
    p=clamp((t-b['start'])/(b['end']-b['start']))
    x=act.get('x',0.5)
    tx=act.get('to_x',x)
    action=act.get('action','idle')
    move_actions={'walk_right','walk_left','sneak_left','enter_left','enter_right'}
    xx=lerp(x,tx,ease(p)) if action in move_actions else x
    return {'x':xx,'action':action,'emotion':act.get('emotion','happy'),'p':p}

def draw_bg(d):
    d.rectangle((0,0,W,H), fill=(246,238,220))
    d.rectangle((0,760,W,H), fill=(214,186,146))
    d.rectangle((42,110,270,430), fill=(185,220,238), outline=(85,110,125), width=8)
    d.line((156,110,156,430), fill=(85,110,125), width=5)
    d.line((42,270,270,270), fill=(85,110,125), width=5)
    d.rounded_rectangle((520,150,690,570), 20, fill=(229,234,238), outline=(100,110,120), width=7)
    d.rectangle((0,650,W,790), fill=(176,116,76))
    d.rectangle((0,790,W,835), fill=(128,79,47))

def pose_points(cx,cy,action,p):
    bob=math.sin(p*math.pi*8)*5 if 'walk' in action or 'sneak' in action else math.sin(p*math.pi*2)*2
    cy+=bob
    head=(cx,cy-150); neck=(cx,cy-105); hip=(cx,cy+35)
    swing=math.sin(p*math.pi*8)*26 if 'walk' in action or 'sneak' in action else 0
    lsh=(cx-35,cy-90); rsh=(cx+35,cy-90)
    lel=(cx-62+swing,cy-28); rel=(cx+62-swing,cy-28)
    lh=(cx-72+swing,cy+32); rh=(cx+72-swing,cy+32)
    lk=(cx-30-swing*0.4,cy+120); rk=(cx+30+swing*0.4,cy+120)
    lf=(cx-42-swing*0.5,cy+210); rf=(cx+42+swing*0.5,cy+210)
    if action in ('point','reach','swap_prop'):
        rel=(cx+78,cy-62); rh=(cx+135,cy-62)
    if action=='grab_eat':
        rel=(cx+48,cy-65); rh=(cx+25,cy-125)
    if action=='facepalm':
        rel=(cx+45,cy-80); rh=(cx+5,cy-150)
    if action=='shock_recoil':
        lel=(cx-90,cy-65); rel=(cx+90,cy-65); lh=(cx-145,cy-120); rh=(cx+145,cy-120)
    if action=='laugh':
        lel=(cx-70,cy-100); rel=(cx+70,cy-100); lh=(cx-115,cy-145); rh=(cx+115,cy-145)
    if action=='fall':
        ang=math.radians(70*ease(p));
        def rot(pt):
            x,y=pt; dx,dy=x-cx,y-cy
            return (cx+dx*math.cos(ang)-dy*math.sin(ang), cy+dx*math.sin(ang)+dy*math.cos(ang))
        return {k:rot(v) for k,v in {'head':head,'neck':neck,'hip':hip,'lsh':lsh,'rsh':rsh,'lel':lel,'rel':rel,'lh':lh,'rh':rh,'lk':lk,'rk':rk,'lf':lf,'rf':rf}.items()}
    return {'head':head,'neck':neck,'hip':hip,'lsh':lsh,'rsh':rsh,'lel':lel,'rel':rel,'lh':lh,'rh':rh,'lk':lk,'rk':rk,'lf':lf,'rf':rf}

def draw_char(d,cid,state,t,speaking=False):
    cx=int(state['x']*W); cy=850
    pts=pose_points(cx,cy,state['action'],state['p'])
    if state['action']=='shock_recoil': cy-=8
    line=(25,25,28)
    def seg(a,b,w=12): d.line((*pts[a],*pts[b]),fill=line,width=w)
    seg('neck','hip',14); seg('lsh','lel'); seg('lel','lh'); seg('rsh','rel'); seg('rel','rh'); seg('hip','lk'); seg('lk','lf'); seg('hip','rk'); seg('rk','rf')
    hx,hy=pts['head']; r=58
    d.ellipse((hx-r,hy-r,hx+r,hy+r),fill='white',outline=line,width=9)
    if cid=='kstick':
        d.pieslice((hx-60,hy-73,hx+60,hy+8),180,360,fill=COLORS[cid]); d.rectangle((hx+25,hy-58,hx+82,hy-42),fill=COLORS[cid])
    elif cid=='zippy':
        d.ellipse((hx-42,hy-18,hx-4,hy+14),outline=COLORS[cid],width=7); d.ellipse((hx+4,hy-18,hx+42,hy+14),outline=COLORS[cid],width=7); d.line((hx-4,hy-2,hx+4,hy-2),fill=COLORS[cid],width=6)
    else:
        d.arc((hx-r-4,hy-r-14,hx+r+4,hy+r-20),200,340,fill=COLORS[cid],width=10)
    em=state['emotion']
    ey=hy-7
    if em=='shocked':
        d.ellipse((hx-28,ey-10,hx-12,ey+14),fill=line); d.ellipse((hx+12,ey-10,hx+28,ey+14),fill=line)
    else:
        d.ellipse((hx-26,ey-5,hx-14,ey+9),fill=line); d.ellipse((hx+14,ey-5,hx+26,ey+9),fill=line)
    if speaking:
        open_amt=14+int(10*(0.5+0.5*math.sin(t*18)))
        d.ellipse((hx-18,hy+22,hx+18,hy+22+open_amt),fill=(45,45,48))
    elif em in ('happy','laughing'):
        d.arc((hx-24,hy+18,hx+24,hy+48),0,180,fill=line,width=6)
    elif em=='deadpan':
        d.line((hx-20,hy+34,hx+20,hy+34),fill=line,width=5)
    else:
        d.arc((hx-22,hy+28,hx+22,hy+52),180,360,fill=line,width=5)
    d.ellipse((pts['lh'][0]-8,pts['lh'][1]-8,pts['lh'][0]+8,pts['lh'][1]+8),fill=line)
    d.ellipse((pts['rh'][0]-8,pts['rh'][1]-8,pts['rh'][0]+8,pts['rh'][1]+8),fill=line)
    return pts

def draw_burger(d,x,y,fake=False,scale=1.0):
    w=int(95*scale); h=int(62*scale)
    d.rounded_rectangle((x-w,y-h,x+w,y-h//4),28,fill=(223,149,61),outline=(95,55,25),width=5)
    d.rectangle((x-w+8,y-h//5,x+w-8,y+8),fill=(73,142,70))
    d.rectangle((x-w+6,y+6,x+w-6,y+25),fill=(133,72,45))
    d.rounded_rectangle((x-w,y+22,x+w,y+h),24,fill=(223,149,61),outline=(95,55,25),width=5)
    if fake:
        d.text((x-26,y-16),'TOY',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18),fill=(180,30,30))

def camera_transform(img,b,t):
    cam=b.get('camera','wide'); p=clamp((t-b['start'])/(b['end']-b['start']))
    if cam=='wide': return img
    zoom=1.0
    cx=W//2; cy=640
    if cam=='medium': zoom=1.10
    elif cam=='push_zippy': zoom=1.10+0.10*ease(p); cx=int(W*0.57)
    elif cam=='close_prop': zoom=1.28; cx=int(W*0.50); cy=720
    elif cam=='close_zippy': zoom=1.34; cx=int(W*0.53); cy=620
    elif cam=='punch_mimi': zoom=1.16+0.28*ease(p); cx=int(W*0.25); cy=620
    nw,nh=int(W/zoom),int(H/zoom)
    left=int(clamp(cx-nw/2,0,W-nw)); top=int(clamp(cy-nh/2,0,H-nh))
    return img.crop((left,top,left+nw,top+nh)).resize((W,H),Image.Resampling.LANCZOS)

def active_dialogue(t):
    for b in episode['beats']:
        for d in b.get('dialogue',[]):
            if d['start']<=t<d['start']+d['duration']:
                return d
    return None

proc=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(OUT)],stdin=subprocess.PIPE)

frames=int(DUR*FPS)
for fi in range(frames):
    t=fi/FPS; b=active_beat(t)
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    draw_bg(d)
    # table/plate
    d.rounded_rectangle((145,700,575,820),30,fill=(139,86,51),outline=(92,54,32),width=7)
    d.ellipse((280,690,440,738),fill=(239,239,234),outline=(120,120,116),width=5)
    # characters
    states={}
    for cid in episode['characters']:
        st=char_state(cid,t,b)
        if st: states[cid]=draw_char(d,cid,st,t,active_dialogue(t) is not None and active_dialogue(t)['speaker']==cid)
    # prop logic
    prop=b.get('prop')
    if prop:
        act=prop.get('action','table')
        if act in ('table','swap_fake'):
            draw_burger(d,int(prop.get('x',0.5)*W),675,fake=act=='swap_fake')
        elif act=='hand_to_mouth' and prop.get('owner') in states:
            owner=states[prop['owner']]; p=clamp((t-b['start'])/(b['end']-b['start']))
            hx,hy=owner['head']; hand=owner['rh']
            q=ease(min(1,p*1.5)); x=int(lerp(hand[0],hx+18,q)); y=int(lerp(hand[1],hy+28,q)); draw_burger(d,x,y,True,0.62)
    # hook
    if t<2.0:
        txt=episode['hook']; box=d.textbbox((0,0),txt,font=FONT_BIG); tw=box[2]-box[0]
        d.rounded_rectangle((W//2-tw//2-28,48,W//2+tw//2+28,125),22,fill=(20,20,22))
        d.text((W//2-tw//2,60),txt,font=FONT_BIG,fill='white')
    dlg=active_dialogue(t)
    if dlg:
        txt=dlg['text'].upper(); box=d.textbbox((0,0),txt,font=FONT_MED); tw=box[2]-box[0]
        y=1080; d.rounded_rectangle((W//2-tw//2-24,y-18,W//2+tw//2+24,y+58),22,fill=(20,20,22))
        d.text((W//2-tw//2,y),txt,font=FONT_MED,fill=COLORS[dlg['speaker']])
    im=camera_transform(im,b,t)
    proc.stdin.write(im.tobytes())
proc.stdin.close(); rc=proc.wait()
if rc!=0: raise SystemExit(rc)
print(OUT)
