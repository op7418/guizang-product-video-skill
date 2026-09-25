"""Example score (light keys + soft rhythm) from an earlier CodePilot promo: 48s, 120 BPM, D major.
Copy into a video project and adapt its arrangement to that film.
No samples, third-party recordings, reference-film audio, or model API.
Usage: python3 score-example-keys.py --output /path/to/new-music-dir
"""
import argparse, array, math, wave, random, subprocess, shutil, sys
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
if not shutil.which('ffmpeg'):parser.error('FFmpeg is required; follow references/onboarding.md.')
if args.output.exists() and (not args.output.is_dir() or any(args.output.iterdir())):
    parser.error('Use an empty output directory; existing audio will not be overwritten.')
args.output.mkdir(parents=True,exist_ok=True)
RATE=48000; DURATION=48; N=RATE*DURATION
left=array.array('f',[0])*N; right=array.array('f',[0])*N
rng=random.Random(1709)
def hz(note):return 440*2**((note-69)/12)
def instrument(start,dur,note,amp,kind='keys',pan=0):
    off=round(start*RATE); freq=hz(note); lg=math.sqrt((1-pan)/2); rg=math.sqrt((1+pan)/2)
    for j in range(min(round(dur*RATE),N-off)):
        t=j/RATE; p=2*math.pi*freq*t
        if kind=='pad':
            env=min(1,t/.22)*min(1,(dur-t)/.4)
            v=(math.sin(p)+.13*math.sin(p*2+.1))*env*amp
        elif kind=='bass':
            env=min(1,t/.009)*math.exp(-3.7*t)*min(1,(dur-t)/.06)
            v=(math.sin(p)+.25*math.sin(p*2)+.08*math.sin(p*3))*env*amp
        else:
            env=min(1,t/.004)*math.exp(-4.5*t)*min(1,(dur-t)/.08)
            v=(math.sin(p)+.3*math.sin(2*p)*math.exp(-6*t)+.14*math.sin(3*p)*math.exp(-9*t))*env*amp
        left[off+j]+=v*lg;right[off+j]+=v*rg
# Dmaj9, Bm9, Gmaj9, Aadd9. Two bars per harmony, varied four-bar phrases.
chords=[[50,57,61,64,69],[47,54,57,61,66],[43,50,54,57,62],[45,52,57,59,64]]
for bar in range(24):
    start=bar*2; chord=chords[(bar//2)%4]
    for i,note in enumerate(chord[1:]):instrument(start,2.15,note,.023,'pad',(i-1.5)*.32)
    for step in range(8):
        if step in ([0,2,3,5,6] if bar%2==0 else [0,1,3,4,6,7]):
            n=chord[1+([0,2,1,3,2,0,3,1][step])]+12
            instrument(start+step*.25,1.15,n,.09 if step%2==0 else .063,'keys',-.28 if step%2==0 else .3)
    if start<46:
        for t,n in [(0,chord[0]),(.75,chord[0]),(1.5,chord[0]+12)]:instrument(start+t,.48,n,.16,'bass')
# A restrained, audible rhythm section: kick, brushed backbeat and stereo shaker.
for beat in range(94):
    start=beat*.5; off=round(start*RATE)
    if beat<4 or beat>=92:continue
    for j in range(round(.21*RATE)):
        t=j/RATE; phase=2*math.pi*(48*t+54*.025*(1-math.exp(-t/.025)))
        v=.23*math.sin(phase)*math.exp(-21*t)*min(1,t/.001)
        left[off+j]+=v*.707;right[off+j]+=v*.707
    if beat%2:
        for j in range(round(.12*RATE)):
            t=j/RATE; v=(rng.uniform(-1,1)*.064+math.sin(2*math.pi*185*t)*.025)*math.exp(-35*t)
            left[off+j]+=v*.75;right[off+j]+=v*.65
    for half in range(2):
        pos=off+round(half*.25*RATE);prev=0
        for j in range(round(.045*RATE)):
            t=j/RATE;x=rng.uniform(-1,1);v=(x-prev)*.014*math.exp(-75*t);prev=x
            left[pos+j]+=v*(.9 if half else .5);right[pos+j]+=v*(.5 if half else .9)
# Signature melodic resolution under the final brand lockup.
for t,n in [(45,74),(45.5,76),(46,78),(46.5,81)]:instrument(t,1.5,n,.1,'keys',.1)
def save(path,L,R):
    pcm=array.array('h')
    for i,(l,r) in enumerate(zip(L,R)):
        t=i/RATE;env=min(1,t/.025)*min(1,max(0,(48-t)/.65))
        pcm.extend([int(max(-.98,min(.98,l*env))*32767),int(max(-.98,min(.98,r*env))*32767)])
    if sys.byteorder!='little':pcm.byteswap()
    with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(pcm.tobytes())
save(args.output/'music-raw.wav',left,right)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(args.output/'music-raw.wav'),'-af','loudnorm=I=-17.5:TP=-2:LRA=8','-ar',str(RATE),str(args.output/'music.wav')],check=True)
print('Created music.wav and music-raw.wav: 48s, stereo, 120 BPM. Adapt this example for the current film; mix SFX separately.')
