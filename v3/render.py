import json, math, pathlib, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
episode = json.loads((ROOT/'episode.json').read_text())
W,H,FPS = 720,1280,30
DUR = float(episode['duration'])
OUT = ROOT/'silent_v3.mp4'

try:
    FONT_BIG = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 52)
    FONT_MED = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
    FONT_SMALL = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
except:
    FONT_BIG = FONT_MED = FONT_SMALL = ImageFont.load_default()

COLORS={'kstick':(232,58,58),'zippy':(45,118,230),'mimi':(242,196,56)}
INK=(25,25,28)

def clamp(x,a=0,b=1): return max(a,min(b,x))
def ease(t): t=clamp(t); return t*t*(3-2*t)
def ease_out_back(t):
    t=clamp(t); c1=1.70158; c3=c1+1
    return 1+c3*(t-1)**3+c1*(t-1)**2
def lerp(a,b,t): return a+(b-a)*t

def active_beat(t):
    for b in episode['beats']:
        if b['start'] <= t < b['end']: return b
    return episode['beats'][-1]

def active_dialogue(t):
    for b in episode['beats']:
        for line in b.get('dialogue',[]):
            if line['start'] <= t < line['start'] + line['duration']:
                return line
    return None

def char_state(cid,t,b):
    act=next((a for a in b.get('actions',[]) if a['character']==cid),None)
    if not act: return None
    p=clamp((t-b['start'])/max(0.001,b['end']-b['start']))
    x=act.get('x',0.5); tx=act.get('to_x',x)
    action=act.get('action','idle')
    moving={'walk_right','walk_left','sneak_left','sneak_right','enter_left','enter_right','exit_left','exit_right'}
    xx=lerp(x,tx,ease(p)) if action in moving else x
    return {'x':xx,'action':action,'emotion':act.get('emotion','happy'),'p':p}

def draw_bg(d):
    d.rectangle((0,0,W,H), fill=(248,241,225))
    d.rectangle((0,805,W,H), fill=(219,197,165))
    d.rectangle((36,96,258,405), fill=(188,222,239), outline=(82,101,113), width=7)
    d.line((147,96,147,405),fill=(82,101,113),width=4)
    d.line((36,250,258,250),fill=(82,101,113),width=4)
    d.rounded_rectangle((536,126,694,535),18,fill=(235,239,241),outline=(104,112,120),width=6)
    d.line((548,310,682,310),fill=(160,166,171),width=4)
    d.rectangle((0,650,W,725),fill=(181,121,79))
    d.rectangle((0,725,W,752),fill=(124,77,49))

def draw_table_back(d):
    d.rounded_rectangle((112,685,608,815),28,fill=(160,101,62),outline=(91,54,33),width=7)
    d.rectangle((130,748,590,810),fill=(148,91,55))
    d.ellipse((283,667,437,708),fill=(239,239,234),outline=(119,119,114),width=4)

def draw_table_front(d):
    d.rounded_rectangle((112,785,608,932),20,fill=(133,78,46),outline=(91,54,33),width=7)
    d.rectangle((135,808,585,920),fill=(144,87,51))

def pose_points(cx,cy,action,p):
    moving=('walk' in action or 'sneak' in action or 'enter' in action or 'exit' in action)
    cycle=math.sin(p*math.pi*8)
    bob=(abs(math.sin(p*math.pi*8))*5 if moving else math.sin(p*math.pi*2)*2)
    cy+=bob
    head=(cx,cy-150); neck=(cx,cy-103); hip=(cx,cy+34)
    swing=cycle*26 if moving else 0
    lsh=(cx-34,cy-88); rsh=(cx+34,cy-88)
    lel=(cx-61+swing,cy-27); rel=(cx+61-swing,cy-27)
    lh=(cx-71+swing,cy+31); rh=(cx+71-swing,cy+31)
    lk=(cx-28-swing*0.42,cy+116); rk=(cx+28+swing*0.42,cy+116)
    lf=(cx-42-swing*0.55,cy+202); rf=(cx+42+swing*0.55,cy+202)

    if action=='point':
        rel=(cx+75,cy-64); rh=(cx+134,cy-68)
    elif action in ('reach','swap_prop'):
        rel=(cx+62,cy-42); rh=(cx+116,cy-18)
    elif action=='grab_eat':
        q=ease_out_back(min(1,p*1.8))
        rel=(cx+54,cy-62); rh=(cx+int(48-22*q),cy-int(40+72*q))
    elif action=='facepalm':
        rel=(cx+46,cy-78); rh=(cx+8,cy-145)
    elif action=='shock_recoil':
        spread=110+int(24*math.sin(p*math.pi))
        lel=(cx-76,cy-66); rel=(cx+76,cy-66); lh=(cx-spread,cy-116); rh=(cx+spread,cy-116)
    elif action=='laugh':
        bounce=abs(math.sin(p*math.pi*7))*12
        head=(head[0],head[1]+bounce); neck=(neck[0],neck[1]+bounce)
        lel=(cx-70,cy-94); rel=(cx+70,cy-94); lh=(cx-112,cy-138); rh=(cx+112,cy-138)
    elif action=='fall':
        ang=math.radians(78*ease_out_back(p))
        pivot=(cx,cy+60)
        base={'head':head,'neck':neck,'hip':hip,'lsh':lsh,'rsh':rsh,'lel':lel,'rel':rel,'lh':lh,'rh':rh,'lk':lk,'rk':rk,'lf':lf,'rf':rf}
        def rot(pt):
            x,y=pt; dx,dy=x-pivot[0],y-pivot[1]
            return (pivot[0]+dx*math.cos(ang)-dy*math.sin(ang),pivot[1]+dx*math.sin(ang)+dy*math.cos(ang))
        return {k:rot(v) for k,v in base.items()}
    return {'head':head,'neck':neck,'hip':hip,'lsh':lsh,'rsh':rsh,'lel':lel,'rel':rel,'lh':lh,'rh':rh,'lk':lk,'rk':rk,'lf':lf,'rf':rf}

def draw_char(d,cid,state,t,speaking=False):
    cx=int(state['x']*W); cy=730
    pts=pose_points(cx,cy,state['action'],state['p'])
    line=INK
    def seg(a,b,w=11): d.line((*pts[a],*pts[b]),fill=line,width=w)
    seg('neck','hip',13); seg('lsh','lel'); seg('lel','lh'); seg('rsh','rel'); seg('rel','rh'); seg('hip','lk'); seg('lk','lf'); seg('hip','rk'); seg('rk','rf')
    hx,hy=pts['head']; r=55
    d.ellipse((hx-r,hy-r,hx+r,hy+r),fill='white',outline=line,width=8)

    if cid=='kstick':
        d.pieslice((hx-57,hy-70,hx+57,hy+4),180,360,fill=COLORS[cid])
        d.rectangle((hx+22,hy-57,hx+75,hy-43),fill=COLORS[cid])
    elif cid=='zippy':
        d.ellipse((hx-40,hy-17,hx-5,hy+13),outline=COLORS[cid],width=6)
        d.ellipse((hx+5,hy-17,hx+40,hy+13),outline=COLORS[cid],width=6)
        d.line((hx-5,hy-2,hx+5,hy-2),fill=COLORS[cid],width=5)
    else:
        d.arc((hx-r-2,hy-r-13,hx+r+2,hy+r-22),198,342,fill=COLORS[cid],width=9)

    em=state['emotion']; action=state['action']; ey=hy-7
    look=0
    if action in ('look_prop','reach','grab_eat'): look=-4
    if action in ('point','shock_recoil'): look=3
    if em=='shocked':
        d.ellipse((hx-28+look,ey-10,hx-12+look,ey+14),fill=line)
        d.ellipse((hx+12+look,ey-10,hx+28+look,ey+14),fill=line)
        d.ellipse((hx-19,hy+24,hx+19,hy+52),outline=line,width=5)
    else:
        d.ellipse((hx-25+look,ey-4,hx-14+look,ey+8),fill=line)
        d.ellipse((hx+14+look,ey-4,hx+25+look,ey+8),fill=line)
        if em=='angry':
            d.line((hx-31,hy-28,hx-11,hy-20),fill=line,width=5); d.line((hx+11,hy-20,hx+31,hy-28),fill=line,width=5)
        elif em=='smug':
            d.line((hx-31,hy-23,hx-12,hy-26),fill=line,width=4); d.line((hx+12,hy-26,hx+31,hy-23),fill=line,width=4)

        if speaking:
            open_amt=12+int(10*(0.5+0.5*math.sin(t*20)))
            d.ellipse((hx-17,hy+21,hx+17,hy+21+open_amt),fill=(45,45,48))
        elif em in ('happy','laughing'):
            d.arc((hx-23,hy+16,hx+23,hy+47),0,180,fill=line,width=5)
        elif em=='deadpan':
            d.line((hx-19,hy+33,hx+19,hy+33),fill=line,width=5)
        elif em=='smug':
            d.arc((hx-18,hy+20,hx+24,hy+46),8,155,fill=line,width=5)
        else:
            d.arc((hx-21,hy+27,hx+21,hy+50),180,360,fill=line,width=5)

    for key in ('lh','rh'):
        x,y=pts[key]; d.ellipse((x-7,y-7,x+7,y+7),fill=line)
    return pts

def draw_burger(d,x,y,fake=False,scale=0.52):
    w=max(18,int(95*scale)); h=max(14,int(62*scale))
    outline=max(2,int(5*scale))
    d.rounded_rectangle((x-w,y-h,x+w,y-int(h*0.22)),max(8,int(28*scale)),fill=(223,149,61),outline=(95,55,25),width=outline)
    d.rectangle((x-w+4,y-int(h*0.18),x+w-4,y+4),fill=(73,142,70))
    d.rectangle((x-w+4,y+3,x+w-4,y+int(h*0.38)),fill=(133,72,45))
    d.rounded_rectangle((x-w,y+int(h*0.32),x+w,y+h),max(7,int(22*scale)),fill=(223,149,61),outline=(95,55,25),width=outline)
    if fake:
        label='TOY'; box=d.textbbox((0,0),label,font=FONT_SMALL); tw=box[2]-box[0]
        d.text((x-tw//2,y-int(h*0.15)),label,font=FONT_SMALL,fill=(180,30,30))

def camera_transform(img,b,t):
    cam=b.get('camera','wide'); p=clamp((t-b['start'])/max(.001,b['end']-b['start']))
    if cam=='wide': return img
    zoom=1.0; cx=W//2; cy=600
    if cam=='medium': zoom=1.08
    elif cam=='push_zippy': zoom=1.08+0.10*ease(p); cx=int(W*0.57); cy=590
    elif cam=='close_prop': zoom=1.18; cx=int(W*0.50); cy=650
    elif cam=='close_zippy': zoom=1.24; cx=int(W*0.53); cy=570
    elif cam=='punch_mimi': zoom=1.12+0.20*ease_out_back(p); cx=int(W*0.25); cy=570
    nw,nh=int(W/zoom),int(H/zoom)
    left=int(clamp(cx-nw/2,0,W-nw)); top=int(clamp(cy-nh/2,0,H-nh))
    return img.crop((left,top,left+nw,top+nh)).resize((W,H),Image.Resampling.LANCZOS)

def draw_ui(im,t):
    d=ImageDraw.Draw(im)
    if t<2.0:
        txt=episode['hook']; box=d.textbbox((0,0),txt,font=FONT_BIG); tw=box[2]-box[0]
        d.rounded_rectangle((W//2-tw//2-24,46,W//2+tw//2+24,119),20,fill=(20,20,22))
        d.text((W//2-tw//2,56),txt,font=FONT_BIG,fill='white')
    dlg=active_dialogue(t)
    if dlg:
        txt=dlg['text'].upper(); maxw=W-70
        font=FONT_MED
        while True:
            box=d.textbbox((0,0),txt,font=font); tw=box[2]-box[0]
            if tw<=maxw or getattr(font,'size',30)<=28: break
            font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',font.size-2)
        y=1090
        d.rounded_rectangle((W//2-tw//2-20,y-14,W//2+tw//2+20,y+52),19,fill=(20,20,22))
        d.text((W//2-tw//2,y),txt,font=font,fill=COLORS[dlg['speaker']])

proc=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(OUT)],stdin=subprocess.PIPE)

frames=int(DUR*FPS)
for fi in range(frames):
    t=fi/FPS; b=active_beat(t); dlg=active_dialogue(t)
    scene=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(scene)
    draw_bg(d); draw_table_back(d)

    states={}
    for cid in episode['characters']:
        st=char_state(cid,t,b)
        if st:
            speaking=dlg is not None and dlg['speaker']==cid
            states[cid]=draw_char(d,cid,st,t,speaking)

    draw_table_front(d)

    prop=b.get('prop')
    if prop:
        act=prop.get('action','table')
        if act in ('table','swap_fake'):
            draw_burger(d,int(prop.get('x',0.5)*W),654,fake=act=='swap_fake',scale=0.48)
        elif act=='hand_to_mouth' and prop.get('owner') in states:
            owner=states[prop['owner']]
            p=clamp((t-b['start'])/max(.001,b['end']-b['start']))
            hx,hy=owner['head']; hand=owner['rh']
            q=ease(min(1,p*1.45))
            x=int(lerp(hand[0],hx+18,q)); y=int(lerp(hand[1],hy+30,q))
            bite_scale=0.34*(1-0.16*clamp((p-.65)/.35))
            draw_burger(d,x,y,True,bite_scale)

    scene=camera_transform(scene,b,t)
    draw_ui(scene,t)
    proc.stdin.write(scene.tobytes())

proc.stdin.close(); rc=proc.wait()
if rc!=0: raise SystemExit(rc)
print(OUT)
