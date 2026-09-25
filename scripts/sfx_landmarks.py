#!/usr/bin/env python3
"""Measure where each sound effect is actually heard, and how loud it is.

For every file prints: duration, onset (first transient above 30% of peak), peak time, peak level.
Use onset as syncOffset for clicks/keys/pops, peak for whooshes/impacts/swells:
    cue.at = action_time - syncOffset
Peak level helps set gains: bundled/procedural SFX are often ~-20 dBFS, recorded ones near 0 dBFS.
Only needs FFmpeg (decodes mp3/wav/etc.).
Usage: python3 sfx_landmarks.py assets/sfx/*.wav [--json]
"""
import argparse, json, math, struct, subprocess, sys
from pathlib import Path

RATE = 48000


def samples(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(RATE), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    return struct.unpack('<%dh' % (len(raw) // 2), raw)


def landmarks(path, threshold=0.3):
    x = samples(path)
    if not x:
        raise ValueError(f'{path}: no audio')
    env = [abs(v) / 32768 for v in x]
    peak_i = max(range(len(env)), key=env.__getitem__)
    peak = env[peak_i]
    onset_i = next((i for i, v in enumerate(env) if v >= threshold * peak), 0)
    return {'file': str(path), 'duration': round(len(env) / RATE, 3), 'onset': round(onset_i / RATE, 3),
            'peak': round(peak_i / RATE, 3), 'peakDbfs': round(20 * math.log10(peak), 1) if peak > 0 else None}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('files', nargs='+', type=Path)
    p.add_argument('--json', action='store_true')
    a = p.parse_args()
    rows = []
    for f in a.files:
        try:
            rows.append(landmarks(f))
        except (subprocess.CalledProcessError, ValueError) as e:
            print(f'skip {f}: {e}', file=sys.stderr)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    for r in rows:
        print(f"{Path(r['file']).name:28s} dur {r['duration']:6.2f}s  onset {r['onset']:6.3f}s  peak {r['peak']:6.3f}s  {r['peakDbfs']} dBFS")


if __name__ == '__main__':
    main()
