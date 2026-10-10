"""Offline regressions for delivery gates and headless-only preflight."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import shutil
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py')
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
delivery=module('check_delivery');environment=module('check_environment')
class Delivery(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name).resolve()
        (self.root/'evidence.md').write_text('Release evidence fixture')
        (self.root/'DIRECTION.md').write_text('# 方向\n因为产品是模型选择器，所以镜头推近选择器。\n| # | 镜头 |\n|---|---|\n| 1 | feature |\n', encoding='utf-8')
        self.plan={'demo':False,'style':'repo','duration':5,'fps':30,'width':1920,'height':1080,'audioRequired':False,'audioExceptionReason':'User requested a silent version',
            'typography':{'mode':'bilingual','zhStyle':'sans-serif','zhFont':'Noto Sans CJK','enFont':'Georgia'},
            'shots':[{'id':'feature','start':0,'end':5,'type':'detail','headline':'切换模型，继续对话','headlineEn':'Switch models','claim':True,'source':['file:evidence.md'],
                'plainExplanation':'切换模型后，可以带着之前的对话继续工作。','description':'切换模型后，对话内容会保留。','component':'src/selector.tsx','actions':[]}]}
    def errors(self):return delivery.check(self.plan,project_dir=self.root)['errors']
    def test_valid_production(self):self.assertEqual(self.errors(),[])
    def test_all_claims_false(self):
        self.plan['shots'][0]['claim']=False;self.assertTrue(any('at least one' in x for x in self.errors()))
    def test_demo_still_allowed(self):
        self.plan['demo']=True;self.plan['shots'][0]['claim']=False;self.assertEqual(self.errors(),[])
    def test_feature_components_required(self):
        for kind in ['detail','workspace','macro']:
            for value in [None,'','   ']:
                with self.subTest(kind=kind,value=value):
                    self.plan['shots'][0].update(type=kind,component=value)
                    self.assertTrue(any('component source' in x for x in self.errors()))
    def test_audio_exception_required(self):
        for value in [None,'','   ',True]:
            self.plan['audioExceptionReason']=value
            self.assertTrue(any('audioExceptionReason' in x for x in self.errors()))
    def test_source_files_resolve(self):
        for source in ['file:missing.md','./missing.md','repo:missing.tsx']:
            self.plan['shots'][0]['source']=[source];self.assertTrue(self.errors())
        self.plan['repo']=str(self.root)
        for source in ['repo:evidence.md:2','file:evidence.md#L3','evidence.md']:
            self.plan['shots'][0]['source']=[source];self.assertEqual(self.errors(),[])
    def test_legacy_paths_search_video_then_repo(self):
        repo=self.root/'product';(repo/'src/components').mkdir(parents=True)
        (repo/'src/components/Selector.jsx').write_text('export const Selector = 1;')
        (repo/'CHANGELOG.md').write_text('Product release')
        self.plan['repo']='product'
        self.plan['shots'][0]['source']=['src/components/Selector.jsx:12','CHANGELOG.md#L2']
        self.assertEqual(self.errors(),[])
        self.assertEqual(delivery.source_file('CHANGELOG.md',self.root,'product'),repo/'CHANGELOG.md')
        (self.root/'CHANGELOG.md').write_text('Video evidence')
        self.assertEqual(delivery.source_file('CHANGELOG.md',self.root,'product'),self.root/'CHANGELOG.md')
        self.plan['shots'][0]['source']=['missing.md'];self.assertTrue(self.errors())
    def test_explicit_source_roots_do_not_fall_back(self):
        repo=self.root/'product';repo.mkdir();(repo/'release.md').write_text('Release')
        self.plan['repo']=str(repo)
        for source in ['file:release.md','./release.md','../release.md']:
            self.plan['shots'][0]['source']=[source];self.assertTrue(self.errors())
        self.plan['shots'][0]['source']=['repo:release.md'];self.assertEqual(self.errors(),[])
        self.assertEqual(delivery.source_file(str(repo/'release.md'),self.root,None),repo/'release.md')
    def test_production_requires_direction(self):
        (self.root/'DIRECTION.md').unlink()
        self.assertTrue(any('DIRECTION.md' in x for x in self.errors()))
        self.plan['demo']=True;self.assertFalse(any('DIRECTION.md' in x for x in self.errors()))
    def test_direction_without_reasons_warns(self):
        (self.root/'DIRECTION.md').write_text('| # | 镜头 |\n|---|---|\n| 1 | feature |\n', encoding='utf-8')
        warnings=delivery.check(self.plan,project_dir=self.root)['warnings']
        self.assertTrue(any('derive devices' in w for w in warnings))
    def test_external_evidence_not_treated_as_file(self):
        self.plan['shots'][0]['source']=['https://example.org/release.md','tag:v1.0','commit:abc123'];self.assertEqual(self.errors(),[])
class Preflight(unittest.TestCase):
    def probe(self,project,launch_ok=True):
        def fake_run(args,cwd=None,timeout=30):
            out=''
            if '--version' in args:out='v22.0.0' if 'node' in args[0] else '10.0.0'
            elif '-version' in args:out='ffmpeg 8'
            elif '-filters' in args:out='volume adelay amix loudnorm afade aresample asetnsamples'
            elif '-encoders' in args:out='libx264 aac'
            elif '-e' in args:
                js=args[args.index('-e')+1]
                if 'chromium.launch' in js:
                    if not launch_ok:return {'ok':False,'stdout':'','stderr':'Permission denied','output':'Permission denied'}
                else:
                    self.assertNotIn('executablePath()',js)
                    out=json.dumps({k:{'version':'1.0','path':'/unavailable/'+k} for k in ['playwright','esbuild','react','react-dom','gsap','three']})
            return {'ok':True,'stdout':out,'stderr':'','output':out}
        with patch.object(environment,'run',side_effect=fake_run),patch.object(environment.shutil,'which',side_effect=lambda n:'/bin/'+n),patch('sys.argv',['check_environment','--project',str(project)]),contextlib.redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as caught:environment.main()
        return caught.exception.code,json.loads(output.getvalue())
    def test_headless_only_and_cache_revalidation(self):
        with tempfile.TemporaryDirectory() as d:
            code,result=self.probe(Path(d));self.assertEqual(code,0);self.assertTrue(result['ready']);self.assertTrue(result['browser']['launched'])
            code,result=self.probe(Path(d));self.assertTrue(result['cached'])
            code,result=self.probe(Path(d),False);self.assertEqual(code,1);self.assertFalse(result['cached']);self.assertIn('browser-launch',result['missing'])
class Starter(unittest.TestCase):
    def test_default_repo_and_unedited_demo_promotion(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d)/'repo';repo.mkdir();project=Path(d)/'video'
            subprocess.run([sys.executable,str(ROOT/'scripts/init_project.py'),'--output',str(project),'--style','default','--repo',str(repo)],capture_output=True,check=True)
            plan=json.loads((project/'plan.json').read_text(encoding='utf-8'))
            self.assertEqual(plan['repo'],str(repo.resolve()))
            self.assertIn(str(repo.resolve()),(project/'BRIEF.md').read_text(encoding='utf-8'))
            plan['demo']=False
            self.assertTrue(any('at least one' in e for e in delivery.check(plan,project_dir=project)['errors']))
    def test_init_writes_direction_questions_not_answers(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d)/'repo';repo.mkdir();project=Path(d)/'video'
            subprocess.run([sys.executable,str(ROOT/'scripts/init_project.py'),'--output',str(project),'--style','repo','--repo',str(repo)],capture_output=True,check=True)
            text=(project/'DIRECTION.md').read_text(encoding='utf-8')
            for heading in ['参考拆解','产品气质','三个方向','选择与理由','画面规范','镜头表']:self.assertIn(heading,text)
            self.assertIn('不要照抄',text)
            self.assertTrue((project/'src/engine.js').is_file())
    def test_sample_views_cover_plan_shots(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d)/'repo';repo.mkdir();project=Path(d)/'video'
            subprocess.run([sys.executable,str(ROOT/'scripts/init_project.py'),'--output',str(project),'--style','repo','--repo',str(repo)],capture_output=True,check=True)
            ids=[s['id'] for s in json.loads((project/'plan.json').read_text(encoding='utf-8'))['shots']]
            index=(project/'src/shots/index.js').read_text(encoding='utf-8')
            for i in ids:self.assertIn(i+':',index)
class FirstFrame(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg needed')
    def test_blank_opening_fails_production(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            blank=root/'blank.mp4';busy=root/'busy.mp4'
            for src,out in [('color=c=0xfafaf9:s=640x360:r=30:d=1',blank),('testsrc2=s=640x360:r=30:d=1',busy)]:
                subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',src,'-pix_fmt','yuv420p',str(out)],check=True)
            self.assertTrue(all(r<0.004 for r in delivery.first_frame_metrics(blank)['inkRatio']))
            self.assertTrue(all(r>0.004 for r in delivery.first_frame_metrics(busy)['inkRatio']))
class Mix(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg needed')
    def test_outputs_are_capped_to_film_duration(self):
        import math,struct,wave
        mixer=module('mix_audio')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'assets/sfx').mkdir(parents=True)
            def tone(path,seconds,freq,channels=2):
                rate=48000;frames=[]
                for i in range(int(rate*seconds)):
                    v=int(0.3*32767*math.sin(2*math.pi*freq*i/rate));frames+= [v]*channels
                with wave.open(str(path),'wb') as w:w.setnchannels(channels);w.setsampwidth(2);w.setframerate(rate);w.writeframes(struct.pack('<%dh'%len(frames),*frames))
            tone(root/'assets/music.wav',3.2,220);tone(root/'assets/sfx/a.wav',0.4,880);tone(root/'assets/sfx/b.wav',1.5,660,1)
            actions=[{'id':f'k{i}','at':0.2+i*0.3,'action':'key','soundRequired':True} for i in range(8)]
            cues=[{'at':a['at'],'actionId':a['id'],'file':'assets/sfx/'+('a' if i%2 else 'b')+'.wav','gain':0.8,'role':'sfx','kind':'click'} for i,a in enumerate(actions)]
            plan={'duration':3,'fps':30,'shots':[{'id':'s','start':0,'end':3,'actions':actions}],'audio':{'music':{'file':'assets/music.wav','gain':0.6},'cues':cues,'ducking':{'enabled':True}}}
            (root/'plan.json').write_text(json.dumps(plan), encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):mixer.mix(root/'plan.json')
            for name in ['sfx-stem.wav','music-ducked.wav','master.wav']:
                out=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(root/'assets'/name)],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout
                self.assertAlmostEqual(float(out),3.0,delta=0.05,msg=name)
class Landmarks(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg needed')
    def test_onset_and_peak(self):
        import math,struct,wave
        landmarks=module('sfx_landmarks').landmarks
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'hit.wav';rate=48000;data=[]
            for i in range(rate):
                t=i/rate;amp=0 if t<0.25 else (0.4 if t<0.5 else 0.9*math.exp(-(t-0.5)*8))
                data.append(int(amp*32767*math.sin(2*math.pi*440*t)))
            with wave.open(str(f),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(struct.pack('<%dh'%len(data),*data))
            r=landmarks(f)
            self.assertAlmostEqual(r['onset'],0.25,delta=0.01)
            self.assertAlmostEqual(r['peak'],0.5,delta=0.01)
            self.assertAlmostEqual(r['peakDbfs'],-0.9,delta=0.3)

class EncodingAndMigration(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()

    def test_init_project_utf8_encoding_and_reading(self):
        repo = self.root / 'repo'
        repo.mkdir()
        project = self.root / 'video'
        subprocess.run(
            [sys.executable, str(ROOT / 'scripts/init_project.py'), '--output', str(project), '--style', 'default', '--repo', str(repo)],
            capture_output=True, check=True
        )
        plan_bytes = (project / 'plan.json').read_bytes()
        self.assertIn('软件更新 · 技术样片'.encode('utf-8'), plan_bytes)
        brief_bytes = (project / 'BRIEF.md').read_bytes()
        self.assertIn('视频 brief'.encode('utf-8'), brief_bytes)
        pres_bytes = (project / 'src/presentations.jsx').read_bytes()
        self.assertIn('组件展示 / DEMO'.encode('utf-8'), pres_bytes)
        dir_bytes = (project / 'DIRECTION.md').read_bytes()
        self.assertIn('影片方向'.encode('utf-8'), dir_bytes)

        plan = delivery.load_plan(project / 'plan.json')
        self.assertEqual(plan['product'], '软件更新 · 技术样片')

        res = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/check_delivery.py'), str(project / 'plan.json')],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn('"ok": true', res.stdout)

    def test_chinese_audio_filenames_mix_and_delivery_roundtrip(self):
        import wave
        import hashlib
        def sha256(p): return hashlib.sha256(p.read_bytes()).hexdigest()
        def make_wav(p):
            p.parent.mkdir(parents=True, exist_ok=True)
            with wave.open(str(p), 'wb') as f:
                f.setnchannels(1); f.setsampwidth(2); f.setframerate(48000)
                f.writeframes(b'\x00\x00' * 480)

        music_path = self.root / 'assets/背景音乐.wav'
        cue_path = self.root / 'assets/sfx/提示音.wav'
        master_path = self.root / 'assets/master.wav'
        stem_path = self.root / 'assets/sfx-stem.wav'
        evidence_dir = self.root / 'evidence'
        evidence_dir.mkdir(parents=True, exist_ok=True)

        for p in [music_path, cue_path, master_path, stem_path]:
            make_wav(p)

        plan = {
            'duration': 5, 'fps': 30, 'width': 1920, 'height': 1080, 'demo': True, 'style': 'default',
            'audioRequired': True, 'sfxRequired': True,
            'audio': {
                'ducking': {'enabled': True},
                'music': {'file': 'assets/背景音乐.wav', 'gain': 0.65},
                'cues': [{'at': 1.0, 'actionId': 'feat-enter', 'file': 'assets/sfx/提示音.wav', 'gain': 0.8, 'role': 'sfx', 'kind': 'click'}]
            },
            'shots': [{
                'id': 'feat', 'start': 0, 'end': 5, 'type': 'detail', 'claim': False, 'source': [],
                'headline': '中文特性', 'description': '说明文案', 'plainExplanation': '说明文案',
                'actions': [{'id': 'feat-enter', 'at': 1.0, 'action': 'enter', 'soundRequired': True}]
            }]
        }
        plan_path = self.root / 'plan.json'
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

        report = {
            'planSha256': sha256(plan_path),
            'master': {'file': 'assets/master.wav', 'sha256': sha256(master_path)},
            'sfxStem': {'file': 'assets/sfx-stem.wav', 'sha256': sha256(stem_path)},
            'music': {'file': 'assets/背景音乐.wav', 'sha256': sha256(music_path)},
            'ducking': {'method': 'cue-envelope', 'windows': []},
            'cues': [{'at': 1.0, 'actionId': 'feat-enter', 'file': 'assets/sfx/提示音.wav', 'gain': 0.8, 'role': 'sfx', 'kind': 'click', 'sha256': sha256(cue_path)}],
            'timing': []
        }
        mix_report_path = evidence_dir / 'audio-mix.json'
        mix_report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

        result = delivery.check(plan, project_dir=self.root, mix_report=mix_report_path, plan_path=plan_path)
        self.assertEqual(result['errors'], [])

        res = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/check_delivery.py'), str(plan_path), '--mix-report', str(mix_report_path)],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn('"ok": true', res.stdout)

    def test_legacy_non_utf8_plan_migration(self):
        plan = {
            'duration': 5, 'fps': 30, 'width': 1920, 'height': 1080, 'demo': True,
            'audioRequired': False, 'audioExceptionReason': 'Testing legacy migration',
            'shots': [{
                'id': 'feat', 'start': 0, 'end': 5, 'type': 'detail', 'claim': False, 'source': [],
                'headline': '历史遗留计划', 'description': 'GBK 编码计划说明', 'plainExplanation': 'GBK 编码计划说明',
                'actions': []
            }]
        }
        plan_path = self.root / 'plan.json'
        plan_path.write_bytes(json.dumps(plan, ensure_ascii=False, indent=2).encode('cp936'))

        with self.assertRaises(UnicodeDecodeError):
            plan_path.read_text(encoding='utf-8')

        loaded = delivery.load_plan(plan_path)
        self.assertEqual(loaded['shots'][0]['headline'], '历史遗留计划')

        migrated_text = plan_path.read_text(encoding='utf-8')
        self.assertIn('历史遗留计划', migrated_text)

        mix_audio = module('mix_audio')
        loaded_again = mix_audio.load_plan(plan_path)
        self.assertEqual(loaded_again['shots'][0]['headline'], '历史遗留计划')

    def test_non_utf8_default_encoding_simulation(self):
        orig_read_text = Path.read_text
        def cp936_default_read_text(path_obj, encoding=None, errors=None):
            if encoding is None:
                encoding = 'cp936'
            return orig_read_text(path_obj, encoding=encoding, errors=errors)

        with patch.object(Path, 'read_text', side_effect=cp936_default_read_text, autospec=True):
            # Verify load_plan preserves explicit UTF-8 decoding even when unparameterized read_text defaults to CP936.
            plan_path = self.root / 'plan_utf8.json'
            plan_path.write_text('{"test": "中文内容"}', encoding='utf-8')
            loaded = delivery.load_plan(plan_path)
            self.assertEqual(loaded['test'], '中文内容')

if __name__=='__main__':unittest.main()
