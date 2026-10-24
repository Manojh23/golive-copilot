#!/usr/bin/env python3
"""Small offline credential-pattern check. Findings never print secret values.

Not a comprehensive secret detector. --staged inspects Git index bytes, so an
unstaged edit cannot hide a credential already prepared for commit.
"""
import argparse
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PATTERNS=[
    ('Google API key',re.compile(rb'AI' rb'za[0-9A-Za-z_-]{35}')),
    ('OpenAI-style key',re.compile(rb'sk-' rb'(?:proj-|svcacct-)?[A-Za-z0-9_-]{30,}')),
    ('GitHub token',re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})')),
    ('private key',re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
]
SKIP={'.git','.venv','node_modules','dist','__pycache__','.pytest_cache','.hypothesis'}

def inspect_file(name,data):
    path=Path(name)
    if path.name=='.env' or path.name.startswith('.env.') and path.name!='.env.example':
        return [f'{name}: environment file must not be committed']
    return [f'{name}: possible {label} (value withheld)' for label,pattern in PATTERNS if pattern.search(data)]

def scan(root,staged=False):
    root=Path(root); findings=[]
    if staged:
        names=subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=ACMR','-z'],cwd=root).decode().split('\0')
        for name in filter(None,names):
            data=subprocess.check_output(['git','show',':'+name],cwd=root)
            findings.extend(inspect_file(name,data))
    else:
        for path in root.rglob('*'):
            rel=path.relative_to(root)
            if path.is_symlink() or not path.is_file() or set(rel.parts)&SKIP:
                continue
            if rel.parts[:2] in (('data','runtime'),('data','sources')) or path.name.startswith('.env') and path.name!='.env.example':
                continue
            if path.suffix in ('.zip','.pdf','.png','.jpg','.woff','.woff2','.sqlite3'):
                continue
            findings.extend(inspect_file(str(rel),path.read_bytes()))
    return findings

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged',action='store_true',help='Inspect staged Git contents; fails if not in Git.')
    args=parser.parse_args()
    try:
        findings=scan(ROOT,args.staged)
    except subprocess.CalledProcessError:
        print('Git scan could not run. Initialize/open the repository, or omit --staged for a project-file scan.')
        return 2
    if findings:
        print('\n'.join(findings)); return 1
    print('No configured credential patterns detected. This is not a complete security audit.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
