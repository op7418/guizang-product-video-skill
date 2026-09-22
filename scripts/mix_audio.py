#!/usr/bin/env python3
"""Mix plan audio.music and action-linked audio.cues; retain inspectable SFX stem and hashes."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import sys


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(args):subprocess.run(['ffmpeg','-v','error','-y',*args],check=True)
def finite(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)

DUCK_PRESETS = {
    'click': (3,.10,.20), 'click-alt': (3,.10,.20), 'pop': (3.5,.12,.24),
    'toggle': (3,.12,.24), 'typing': (2.5,.35,.25), 'whoosh': (4,.16,.30),
    'sweep': (4,.20,.35), 'ding-dong': (6,.45,.40), 'success': (5,.35,.35),
    'error': (5,.35,.35), 'resolve': (5,.55,.45),
}

def duck_windows(audio, cues, duration):
    config=audio.get('ducking',{})
    if not isinstance(config,dict):raise ValueError('audio.ducking must be an object')
    if config.get('enabled') is False:
        if not config.get('reason'):raise ValueError('Explain why the mix needs no ducking')
        return []
    windows=[]
    for cue in cues:
        kind=cue.get('kind',Path(cue['file']).stem)
        db,hold,release=DUCK_PRESETS.get(kind,(4,.18,.30))
        override=cue.get('duck',{})
        if not isinstance(override,dict):raise ValueError('cue.duck must be an object')
        settings={'db':db,'attack':.04,'hold':hold,'release':release}
        settings.update({k:config[k] for k in settings if k in config})
        settings.update(override)
        for key in ['db','attack','hold','release']:
            if not finite(settings.get(key)):raise ValueError('Duck parameters must be finite')
        if not 0<=settings['db']<=12 or not .005<=settings['attack']<=.5 or not 0<=settings['hold']<=3 or not .02<=settings['release']<=2:
            raise ValueError('Duck envelope outside useful bounds')
        if settings['db']==0:
            if not settings.get('reason'):raise ValueError('A zero duck depth needs a reason')
            continue
        # Lower BGM before the audible landmark, not before a file containing long leading silence.
        center=cue['at']+cue.get('syncOffset',0)
        windows.append({'actionId':cue['actionId'],'kind':kind,'start':max(0,center-settings['attack']),
            'attackEnd':center,'holdEnd':min(duration,center+settings['hold']),
            'end':min(duration,center+settings['hold']+settings['release']),'db':settings['db']})
    return windows

def duck_expression(windows):
    expressions=[]
    for w in windows:
        a,b,c,d=[w[k] for k in ['start','attackEnd','holdEnd','end']]
        gain=10**(-w['db']/20)
        attack=f'1-(1-{gain})*(t-{a})/{b-a}' if b>a else str(gain)
        release=f'{gain}+(1-{gain})*(t-{c})/{d-c}' if d>c else '1'
        expressions.append(f'if(lt(t,{a}),1,if(lt(t,{b}),{attack},if(lt(t,{c}),{gain},if(lt(t,{d}),{release},1))))')
    # The deepest current envelope wins. Overlapping clicks never multiply attenuation into silence.
    result='1'
    for expr in expressions:result=f'min({result},{expr})'
    return result


def load_plan(plan_path):
    p = Path(plan_path)
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except UnicodeDecodeError:
        for enc in ['locale', 'gbk', 'cp936']:
            try:
                content = p.read_text() if enc == 'locale' else p.read_text(encoding=enc)
                data = json.loads(content)
                try:
                    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                except OSError as err:
                    print(f"Warning: Failed to rewrite '{p.name}' to UTF-8: {err}", file=sys.stderr)
                return data
            except (UnicodeDecodeError, json.JSONDecodeError, OSError):
                continue
        raise ValueError(f"Plan file '{p.name}' is not valid UTF-8. Please convert to UTF-8.")


def mix(plan_path):
    plan_path=plan_path.resolve();base=plan_path.parent;plan=load_plan(plan_path)
    duration=plan['duration'];audio=plan.get('audio',{});music=audio.get('music',{});cues=audio.get('cues',[])
    if not finite(duration) or duration<=0:raise ValueError('Invalid duration')
    if not isinstance(cues,list) or not cues:raise ValueError('No SFX cues. A BGM-only master is not a completed sound design.')
    sources=[music,*cues]
    for item in sources:
        if not isinstance(item,dict) or not isinstance(item.get('file'),str):raise ValueError('Every music/cue item needs a file')
        file=(base/item['file']).resolve()
        if not file.is_file():raise ValueError('Missing audio: '+str(file))
        gain=item.get('gain',1)
        if not finite(gain) or not 0<gain<=4:raise ValueError('Gain must be finite and in (0,4]')
    for cue in cues:
        if cue.get('role')!='sfx' or not cue.get('actionId'):raise ValueError('Each cue needs role=sfx and actionId')
        if not finite(cue.get('at')) or not 0<=cue['at']<duration:raise ValueError('Cue time outside video')
    required={}
    actions={}
    for shot in plan['shots']:
        for action in shot.get('actions',[]):
            if action.get('id'):
                actions[action['id']]=shot['start']+action['at']
                if action.get('soundRequired'):required[action['id']]=True
    for cue in cues:
        if cue['actionId'] not in actions:raise ValueError('Cue refers to an unknown action')
        offset=cue.get('syncOffset',0)
        if not finite(offset) or offset<0:raise ValueError('syncOffset must be a nonnegative audible-landmark offset')
        if abs(cue['at']+offset-actions[cue['actionId']])>2/plan['fps']:raise ValueError('Cue audible landmark differs from its action by more than two frames')
    if set(required)-{c['actionId'] for c in cues}:raise ValueError('Required key actions are missing SFX')
    music_path=(base/music['file']).resolve()
    measured=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(music_path)],text=True,encoding='utf-8',errors='replace'))
    music_duration=float(measured['format']['duration']);warnings=[]
    if music_duration-duration>1:
        warnings.append(f'Music is {music_duration-duration:.2f}s longer than the film; automatic trim/fade is not a composed ending. Review and arrange the ending.')
        print('Warning: '+warnings[-1],file=sys.stderr)
    if music_duration+.05<duration:raise ValueError('Music shorter than film; arrange/loop and end it deliberately before mixing')
    out=base/'assets';out.mkdir(exist_ok=True)
    evidence=base/'evidence';evidence.mkdir(exist_ok=True)
    stem=out/'sfx-stem.wav';master=out/'master.wav';bgm_stem=out/'music-ducked.wav'
    if any((base/s['file']).resolve() in [stem.resolve(),master.resolve(),bgm_stem.resolve()] for s in sources):
        raise ValueError('Inputs must not be the generated master or stem')
    inputs=[];filters=[]
    for i,cue in enumerate(cues):
        inputs += ['-i',str((base/cue['file']).resolve())]
        filters.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={cue.get("gain",1)},adelay={round(cue["at"]*1000)}:all=1[c{i}]')
    filters.append(''.join(f'[c{i}]' for i in range(len(cues)))+f'amix=inputs={len(cues)}:normalize=0,apad=whole_dur={duration},atrim=duration={duration}[sfx]')
    # Float stem preserves summed transients until mastering; no early hard clipping.
    run([*inputs,'-filter_complex',';'.join(filters),'-map','[sfx]','-t',str(duration),'-c:a','pcm_f32le','-ar','48000',str(stem)])
    windows=duck_windows(audio,cues,duration)
    envelope=duck_expression(windows)
    bg_filters=f"aresample=48000,asetnsamples=n=240:p=0,volume='{music.get('gain',1)}*({envelope})':eval=frame,afade=t=in:d=0.025,afade=t=out:st={max(0,duration-.5)}:d=0.5,atrim=duration={duration}"
    # 240 samples at 48 kHz = 5 ms steps: smoother gain automation around short click transients.
    run(['-i',str(music_path),'-af',bg_filters,'-t',str(duration),'-ar','48000','-ac','2','-c:a','pcm_f32le',str(bgm_stem)])
    with tempfile.TemporaryDirectory(prefix='film-mix-') as tmp:
        raw=Path(tmp)/'raw.wav'
        graph=f'[0:a][1:a]amix=inputs=2:normalize=0,atrim=duration={duration}[mix]'
        run(['-i',str(bgm_stem),'-i',str(stem),'-filter_complex',graph,'-map','[mix]','-t',str(duration),'-ar','48000','-ac','2','-c:a','pcm_f32le',str(raw)])
        measurement=subprocess.run(['ffmpeg','-v','info','-i',str(raw),'-af','loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True).stderr
        stats=json.loads(measurement[measurement.rfind('{'):measurement.rfind('}')+1])
        if not all(math.isfinite(float(stats[k])) for k in ['input_i','input_tp','input_lra','input_thresh','target_offset']):raise ValueError('Silent/invalid mix')
        norm='loudnorm=I=-16:TP=-1.5:LRA=8:linear=true:'+':'.join(f'{k}={stats[v]}' for k,v in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')])
        final_measurement=subprocess.run(['ffmpeg','-y','-v','info','-i',str(raw),'-af',norm+':print_format=json','-ar','48000','-ac','2','-c:a','pcm_s24le',str(master)],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True).stderr
        final_stats=json.loads(final_measurement[final_measurement.rfind('{'):final_measurement.rfind('}')+1])
    timing=[];beat=audio.get('beatGrid',{})
    for cue in cues:
        anchor=cue['at']+cue.get('syncOffset',0)
        row={'actionId':cue['actionId'],'fileStart':cue['at'],'audibleLandmark':anchor,'actionTime':actions[cue['actionId']],
             'errorFrames':round((anchor-actions[cue['actionId']])*plan['fps'],3)}
        if cue.get('onBeat'):
            bpm=beat.get('bpm');origin=beat.get('offset',0);division=cue.get('beatDivision',1)
            if not finite(bpm) or not 30<=bpm<=300 or not finite(origin) or division not in [1,2,4]:raise ValueError('onBeat cues require a measured beatGrid and valid beatDivision')
            step=60/bpm/division;nearest=origin+round((anchor-origin)/step)*step
            row.update(nearestBeat=nearest,beatErrorFrames=round((anchor-nearest)*plan['fps'],3))
        timing.append(row)
    report={'planSha256':sha(plan_path),'music':{**music,'sha256':sha(music_path)},'cues':[{**c,'sha256':sha((base/c['file']).resolve())} for c in cues],
            'master':{'file':'assets/master.wav','sha256':sha(master)},'sfxStem':{'file':'assets/sfx-stem.wav','sha256':sha(stem)},
            'musicStem':{'file':'assets/music-ducked.wav','sha256':sha(bgm_stem)},'ducking':{'method':'cue-envelope','windows':windows,'overlap':'deepest-envelope-wins'},'timing':timing,
            'warnings':warnings,'normalization':{'requested':'linear','normalization_type':final_stats.get('normalization_type'),'measurement':stats,'output':final_stats},
            'listeningStatus':'Not auditioned by script; listen to isolated SFX, final mix and encoded MP4.'}
    (evidence/'audio-mix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Mixed BGM + '+str(len(cues))+' action cues with music ducking. Inspect assets/sfx-stem.wav and assets/master.wav before delivery.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan',type=Path);a=p.parse_args()
    try:mix(a.plan)
    except (ValueError,KeyError,OSError,subprocess.CalledProcessError) as e:p.exit(1,str(e)+'\n')
if __name__=='__main__':main()
