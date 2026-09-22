#!/usr/bin/env python3
"""Check plan invariants and actual media metadata. Does not judge visual/audio taste."""
import argparse
import hashlib
import re
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import sys


def nonempty(value):
    return isinstance(value,str) and bool(value.strip())


def source_file(source, project_dir, repo):
    """Resolve explicit file:/repo: sources and recognizable legacy file paths.
    URLs, commits and version labels remain evidence references, not file paths.
    """
    if re.match(r'^[a-zA-Z]+://',source):return None
    root=Path(project_dir or '.').resolve()
    repo_root=Path(repo).expanduser() if nonempty(repo) else None
    if repo_root is not None and not repo_root.is_absolute():repo_root=root/repo_root
    legacy_bare=False
    if source.startswith('repo:'):
        if not nonempty(repo):raise ValueError('repo: source requires plan.repo')
        root=repo_root
        raw=source[5:]
    elif source.startswith('file:'):raw=source[5:]
    else:
        raw=source
        legacy_bare=not raw.startswith(('./','../','/','~/'))
        if not (raw.startswith(('./','../','/','~/')) or re.search(r'\.(?:md|mdx|txt|json|tsx?|jsx?|vue|svelte|css|html|py|rs|go)(?:[:#].*)?$',raw)):
            return None
    raw=re.sub(r'(?::\d+(?::\d+)?|#L\d+(?:-L\d+)?)$','',raw)
    if not raw.strip():raise ValueError('empty file source')
    path=Path(raw).expanduser()
    if path.is_absolute():return path
    candidate=root/path
    if legacy_bare and not candidate.is_file() and repo_root is not None:
        alternative=repo_root/path
        if alternative.is_file():return alternative
    return candidate


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def creative_checks(plan, errors, warnings, project_dir, mix_report, final_video, plan_path):
    production = plan.get('demo') is False
    issue = errors if production else warnings
    typography=plan.get('typography', {})
    if not isinstance(typography,dict):
        issue.append('typography must describe language/font roles');typography={}
    exception=bool(typography.get('exceptionReason'))
    if not exception:
        if typography.get('mode')!='bilingual':issue.append('Use meaningful bilingual headings or record the user-requested exception')
        if typography.get('zhStyle')!='sans-serif':issue.append('Chinese headings default to sans-serif; do not mix Chinese serif/sans lines')
        if not typography.get('zhFont') or not typography.get('enFont') or typography.get('zhFont')==typography.get('enFont'):
            issue.append('Specify separate Chinese and English headline fonts')
    if production:
        if not any(isinstance(s,dict) and s.get('claim') is True for s in plan['shots']):
            errors.append('Production promo needs at least one evidenced feature claim')
        if plan.get('audioRequired') is False and not nonempty(plan.get('audioExceptionReason')):
            errors.append('Disabling audio needs audioExceptionReason documenting the user request')
    actions={};required=set()
    for shot in plan['shots']:
        if not isinstance(shot,dict):continue
        label=str(shot.get('id','shot'))
        if production and shot.get('type') in ['detail','workspace','macro'] and not nonempty(shot.get('component')):
            errors.append(label+' needs a component source for its feature visual')
        en=shot.get('headlineEn','')
        if not exception and shot.get('type') in ['title','detail','workspace','macro','end']:
            if not isinstance(en,str) or not re.search('[A-Za-z]',en) or en.strip().upper() in ['UPDATE','PRODUCT UPDATE','NEW','FEATURE']:
                issue.append(label+' needs a meaningful English headline, not a decorative generic label')
        if shot.get('claim'):
            if not isinstance(shot.get('plainExplanation'),str) or not shot['plainExplanation'].strip():
                issue.append(label+' needs a plain explanation of object, action and observable result')
            if not isinstance(shot.get('description'),str) or not shot['description'].strip():issue.append(label+' lacks an on-screen explanation')
        text=str(shot.get('description',''))
        if any(term in text for term in ['自然流转','一气呵成','触手可及','重新定义','赋能','无缝衔接']):
            warnings.append(label+' may contain vague promotional language; perform the plain-language read-through')
        for action in shot.get('actions',[]) if isinstance(shot.get('actions'),list) else []:
            if not isinstance(action,dict):issue.append(label+' has malformed action');continue
            aid=action.get('id')
            if not isinstance(aid,str) or not aid or aid in actions:issue.append(label+' needs unique action IDs');continue
            at=action.get('at')
            if not number(at) or not number(shot.get('start')) or not number(shot.get('end')) or not 0<=at<shot['end']-shot['start']:
                issue.append(label+' has action outside shot');continue
            actions[aid]=shot['start']+at
            if action.get('soundRequired'):required.add(aid)
    sfx_required=plan.get('audioRequired') and plan.get('sfxRequired',True)
    if plan.get('audioRequired') and plan.get('sfxRequired') is False and not plan.get('audioExceptionReason'):
        issue.append('Disabling SFX needs the user-requested reason, not an agent shortcut')
    audio=plan.get('audio',{})
    if not isinstance(audio,dict):issue.append('audio must be an object');audio={}
    cues=audio.get('cues',[])
    if not isinstance(cues,list):issue.append('audio.cues must be an array');cues=[]
    linked=set()
    if sfx_required:
        if not required:issue.append('Mark key state changes with soundRequired; do not leave all key actions silent')
        if not cues:issue.append('Missing SFX cues; a music track alone is insufficient')
        music=audio.get('music',{})
        if not isinstance(music,dict) or not music.get('file'):issue.append('Record BGM separately from SFX')
        for cue in cues:
            if not isinstance(cue,dict):issue.append('Malformed SFX cue');continue
            aid=cue.get('actionId')
            if not isinstance(aid,str) or aid not in actions:issue.append('SFX cue needs a known actionId');continue
            if cue.get('role')!='sfx' or not isinstance(cue.get('file'),str) or not cue['file'].strip():issue.append('SFX cue needs role=sfx and an actual file')
            offset=cue.get('syncOffset',0)
            if not number(offset) or offset<0 or not number(cue.get('at')) or abs(cue['at']+offset-actions[aid])>2/plan['fps']:issue.append('SFX audible landmark must align with its action within two frames')
            if not number(cue.get('gain',1)) or not 0<cue.get('gain',1)<=4:issue.append('SFX gain must be in (0,4]')
            linked.add(aid)
        kinds={c.get('kind',Path(c.get('file','')).stem) for c in cues if isinstance(c,dict)}
        if plan['duration']>=30 and len(kinds)<3:warnings.append('Long promo has fewer than three SFX roles; review sound variety rather than repeating one chime')
        if required-linked:issue.append('Key actions without SFX: '+', '.join(sorted(required-linked)))
        if production and final_video and mix_report is None:errors.append('Final video needs --mix-report evidence of BGM + SFX assembly; audio stream existence is insufficient')
    if mix_report is not None:
        try:
            report=json.loads(Path(mix_report).read_text(encoding='utf-8'))
            base=Path(project_dir)
            def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
            if report.get('planSha256')!=digest(Path(plan_path) if plan_path else base/'plan.json'):errors.append('Mix report is stale for the current plan')
            if report.get('cues') is None or [{k:v for k,v in c.items() if k!='sha256'} for c in report['cues']]!=cues:
                errors.append('Mix report cues differ from plan')
            if sfx_required and not report.get('ducking') and not audio.get('ducking',{}).get('reason'):errors.append('Missing music ducking evidence')
            for item in report.get('timing',[]):
                if abs(item.get('beatErrorFrames',0))>2:warnings.append(item['actionId']+' is off its requested beat; adjust picture and audio together')
            for entry in [report['master'],report['sfxStem'],report['music'],*([report['musicStem']] if 'musicStem' in report else []),*report['cues']]:
                if digest(base/entry['file'])!=entry['sha256']:errors.append('Mix asset hash mismatch: '+entry['file'])
            warnings.append('Mix inputs/stem/master verified; listen to SFX audibility and verify this master was used in the final export')
        except (OSError,ValueError,KeyError,TypeError) as exc:errors.append('Invalid mix evidence: '+str(exc))


def check(plan, video=None, project_dir=None, mix_report=None, plan_path=None):
    errors, warnings = [], []
    result = {'errors':errors, 'warnings':warnings, 'limits':['No semantic verification of feature claims', 'No visual clipping or taste assessment', 'No listening or sound cue alignment assessment']}
    if not isinstance(plan, dict):
        errors.append('plan must be an object')
        return result
    for field in ['duration','fps','width','height']:
        if not number(plan.get(field)) or plan[field] <= 0:
            errors.append(field+' must be a positive finite number')
    if errors:
        return result
    for field in ['width','height']:
        if int(plan[field]) != plan[field] or int(plan[field]) % 2:
            errors.append(field+' must be an even integer for yuv420p')
    if plan.get('style') not in ['repo','default','hybrid']:
        errors.append('style must be repo/default/hybrid')
    if not isinstance(plan.get('audioRequired'), bool):
        errors.append('audioRequired must explicitly be true or false')
    if plan.get('demo', True):
        warnings.append('Technical demo; not a completed promotional film')
    shots = plan.get('shots')
    if not isinstance(shots, list) or not shots:
        errors.append('shots must be a nonempty array')
        return result
    tolerance = .5/plan['fps']
    cursor = 0
    ids=set()
    types=set()
    for idx,s in enumerate(shots):
        label='shot '+str(idx+1)
        if not isinstance(s,dict):
            errors.append(label+' must be an object');continue
        if not isinstance(s.get('id'),str) or not s['id'] or s['id'] in ids:
            errors.append(label+' requires a unique nonempty id')
        else:
            ids.add(s['id']);label=s['id']
        if not all(number(s.get(k)) for k in ['start','end']) or s.get('end',0)<=s.get('start',0):
            errors.append(label+' has invalid timing');continue
        if abs(s['start']-cursor)>tolerance:
            errors.append(label+' creates a timeline gap/overlap; shots must cover the timeline in order')
        cursor=s['end']
        if s.get('type') in ['title','detail','end','workspace','macro','montage']:
            types.add(s['type'])
        else:
            warnings.append(label+' has custom/missing type; review shot variety')
        if not isinstance(s.get('headline'),str) or not s['headline'].strip():
            errors.append(label+' is missing its headline')
        if not isinstance(s.get('claim'),bool):
            errors.append(label+' must explicitly identify whether it makes a feature claim')
        sources=s.get('source')
        if s.get('claim') and (not isinstance(sources,list) or not sources or not all(isinstance(x,str) and x.strip() for x in sources)):
            errors.append(label+' claims a feature without a source array')
        if plan.get('demo') is False and isinstance(sources,list):
            for source in sources:
                if not nonempty(source):continue
                try:
                    resolved=source_file(source,project_dir,plan.get('repo'))
                    if resolved is not None and not resolved.is_file():errors.append(label+' source file missing: '+source)
                except ValueError as exc:errors.append(label+' invalid source: '+str(exc))
        desc=s.get('description','')
        appeared=s.get('descriptionAt',0)
        if not number(appeared) or appeared<0 or appeared>=s['end']-s['start']:
            errors.append(label+' has invalid descriptionAt')
        elif isinstance(desc,str):
            readable=s['end']-s['start']-appeared
            if len(''.join(desc.split()))/readable>9:
                warnings.append(label+' description may be too fast; inspect actual reading time')
        else:
            errors.append(label+' description must be text')
        if not isinstance(s.get('actions'),list) or not s['actions']:
            warnings.append(label+' has no recorded action beats')
    if abs(cursor-plan['duration'])>tolerance:
        errors.append('shots do not end at declared duration')
    if len(shots)>3 and len(types)<2:
        warnings.append('All shots use one layout type; review visual rhythm')
    creative_checks(plan, errors, warnings, project_dir, mix_report, bool(video), plan_path)
    if video:
        try:
            proc=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
            meta=json.loads(proc.stdout)
            streams=meta.get('streams',[])
            videos=[s for s in streams if s.get('codec_type')=='video']
            audios=[s for s in streams if s.get('codec_type')=='audio']
            result['media']={'format':meta.get('format',{}),'video':videos,'audio':audios}
            if not videos:
                errors.append('No video stream')
            else:
                stream=videos[0]
                for dim in ['width','height']:
                    if stream.get(dim)!=plan[dim]:errors.append('Video '+dim+' differs from plan')
                rate=float(Fraction(stream.get('avg_frame_rate','0/1')))
                if abs(rate-plan['fps'])>.02:errors.append('Video frame rate differs from plan')
                duration=float(stream.get('duration',meta['format'].get('duration',0)))
                if abs(duration-plan['duration'])>max(.1,2/plan['fps']):errors.append('Video duration differs from plan')
            if plan.get('audioRequired') and not audios:
                errors.append('Music/SFX required but audio stream missing')
            elif audios:
                ad=float(audios[0].get('duration',meta['format'].get('duration',0)))
                if ad+0.2<plan['duration']:warnings.append('Audio stream ends before the video; inspect ending')
                warnings.append('Audio stream exists; loudness, audibility and synchronization still need review')
        except (OSError,subprocess.CalledProcessError,ValueError,KeyError,ZeroDivisionError) as exc:
            errors.append('Could not inspect media: '+str(exc))
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


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan',type=Path)
    p.add_argument('--video',type=Path)
    p.add_argument('--mix-report',type=Path)
    args=p.parse_args()
    try:
        plan=load_plan(args.plan)
        result=check(plan,args.video,args.plan.resolve().parent,args.mix_report,args.plan)
    except (OSError,ValueError) as exc:
        result={'errors':[str(exc)],'warnings':[]}
    result['ok']=not result['errors']
    print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(0 if result['ok'] else 1)

if __name__=='__main__':
    main()
