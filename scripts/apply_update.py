#!/usr/bin/env python3
"""Overlay this package onto an existing project; keep local state and backups.

Stop the app first. Run from the NEW extracted package, not the old project.
Default is a dry run. Pass --apply to copy changes. No files are deleted.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','.venv','node_modules','__pycache__','.pytest_cache','.hypothesis'}

def protected(rel):
    return (bool(set(rel.parts)&SKIP) or rel.parts[:2] in (('data','runtime'),('data','sources'))
            or rel.name.startswith('.env') and rel.name!='.env.example'
            or str(rel)=='KIRO_USAGE.md')

def update(source,target,apply=False):
    source=Path(source).resolve(); target=Path(target).resolve()
    if source==target or source in target.parents or target in source.parents:
        raise ValueError('Extract the update into a separate folder beside your existing project.')
    if not (target/'backend/app.py').is_file():
        raise ValueError('Target must be your existing golive-copilot project folder.')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    backup=target.parent/(target.name+'-backup-'+stamp)
    changed=[]
    # Validate the complete plan before touching any file.
    for src in sorted(source.rglob('*')):
        rel=src.relative_to(source)
        if protected(rel) or src.is_symlink() or not src.is_file():
            continue
        dest=target/rel
        if any(p.is_symlink() for p in (dest,*dest.parents)):
            raise ValueError(f'Refusing a destination through a symbolic link: {rel}')
        if dest.exists() and not dest.is_file():
            raise ValueError(f'Destination is not a regular file: {rel}')
        if dest.exists() and hashlib.sha256(dest.read_bytes()).digest()==hashlib.sha256(src.read_bytes()).digest():
            continue
        changed.append((src,dest,rel))
    if apply:
        for src,dest,rel in changed:
            if dest.exists():
                saved=backup/rel; saved.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(dest,saved)
            dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dest)
    return [str(rel) for _,_,rel in changed],backup

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',required=True,help='Existing project directory')
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    try:
        changed,backup=update(ROOT,args.target,args.apply)
    except ValueError as e:
        parser.error(str(e))
    print(('Updated' if args.apply else 'Would update')+f' {len(changed)} files.')
    for path in changed: print('  '+path)
    if args.apply:
        print(f'Overwritten files backed up under: {backup}')
        print('Preserved .env, Git history, virtual environment, runtime database and KIRO_USAGE.md. No files deleted.')
        print('Next: run bash scripts/setup.sh from your existing project, then npm run dev.')
    else:
        print('Dry run only. Add --apply after checking the target path.')

if __name__=='__main__': main()
