import importlib.util
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('secret_check',ROOT/'scripts/check_secrets.py')
scanner=importlib.util.module_from_spec(spec); spec.loader.exec_module(scanner)

def test_secret_check_uses_staged_bytes_without_exposing_value(tmp_path):
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    secret='AI'+'za'+'x'*35
    path=tmp_path/'config.py'; path.write_text('KEY='+repr(secret))
    subprocess.run(['git','add','config.py'],cwd=tmp_path,check=True)
    path.write_text('KEY="now-clean-in-working-tree"')
    findings=scanner.scan(tmp_path,staged=True)
    assert findings and all(secret not in f for f in findings)
    assert not scanner.scan(tmp_path)

def test_environment_files_are_blocked_but_example_allowed():
    assert scanner.inspect_file('.env',b'GEMINI_API_KEY=anything')
    assert scanner.inspect_file('.env.production',b'')
    assert scanner.inspect_file('.env.example',b'GEMINI_API_KEY=')==[]

def test_update_backs_up_code_and_keeps_local_state(tmp_path):
    spec=importlib.util.spec_from_file_location('updater',ROOT/'scripts/apply_update.py')
    updater=importlib.util.module_from_spec(spec); spec.loader.exec_module(updater)
    source=tmp_path/'new'; target=tmp_path/'existing'
    for root in (source,target):
        (root/'backend').mkdir(parents=True)
        (root/'backend/app.py').write_text('old' if root==target else 'new')
        (root/'data/runtime').mkdir(parents=True)
        (root/'data/runtime/workspace.sqlite3').write_bytes(b'local-saved-state')
        (root/'.env').write_text('local-provider-setting')
        (root/'KIRO_USAGE.md').write_text('actual local work' if root==target else 'template')
    (target/'custom-note.md').write_text('keep this too')
    changed,_=updater.update(source,target)
    assert changed==['backend/app.py'] and (target/'backend/app.py').read_text()=='old'
    _,backup=updater.update(source,target,True)
    assert (backup/'backend/app.py').read_text()=='old'
    assert (target/'backend/app.py').read_text()=='new'
    assert (target/'.env').read_text()=='local-provider-setting'
    assert (target/'KIRO_USAGE.md').read_text()=='actual local work'
    assert (target/'data/runtime/workspace.sqlite3').read_bytes()==b'local-saved-state'
    assert (target/'custom-note.md').exists()
