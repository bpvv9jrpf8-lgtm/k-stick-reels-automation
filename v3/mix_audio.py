import json, pathlib, subprocess

ROOT=pathlib.Path(__file__).parent
OUTDIR=ROOT/'out'; OUTDIR.mkdir(exist_ok=True)
video=ROOT/'silent_v3.mp4'
lines=json.loads((ROOT/'dialogue_audio.json').read_text())
episode=json.loads((ROOT/'episode.json').read_text())

inputs=['-i',str(video)]
filters=[]; labels=[]; idx=1
for line in lines:
    f=ROOT/'audio'/line['audio_file']
    inputs += ['-i',str(f)]
    delay=int(float(line['start'])*1000)
    filters.append(f'[{idx}:a]adelay={delay}|{delay},volume=1.0[a{idx}]')
    labels.append(f'[a{idx}]'); idx+=1

sfx_timing={'sneak':5.8,'pop':9.6,'bite':13.3,'record':15.1,'bonk':16.8,'fall':22.3,'laugh':22.55}
for name,start in sfx_timing.items():
    f=ROOT/'sfx'/f'{name}.wav'
    if not f.exists(): continue
    inputs += ['-i',str(f)]
    delay=int(start*1000)
    vol=0.55 if name not in ('record','bonk') else 0.75
    filters.append(f'[{idx}:a]adelay={delay}|{delay},volume={vol}[a{idx}]')
    labels.append(f'[a{idx}]'); idx+=1

if labels:
    filters.append(''.join(labels)+f'amix=inputs={len(labels)}:duration=longest:dropout_transition=0,alimiter=limit=0.95[mix]')
    cmd=['ffmpeg','-y',*inputs,'-filter_complex',';'.join(filters),'-map','0:v:0','-map','[mix]','-c:v','copy','-c:a','aac','-b:a','192k','-shortest',str(OUTDIR/'k-stick-v3.mp4')]
else:
    cmd=['ffmpeg','-y','-i',str(video),'-c:v','copy',str(OUTDIR/'k-stick-v3.mp4')]
subprocess.run(cmd,check=True)
print(OUTDIR/'k-stick-v3.mp4')
