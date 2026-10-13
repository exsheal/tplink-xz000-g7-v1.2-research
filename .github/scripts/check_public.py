#!/usr/bin/env python3
"""Check publication paths, text formats, synthetic identities and local links.

An optional external JSON array provides exact private fingerprints. The
checker reports rule names/locations, never the matched secret text. It is a
guard against common mistakes, not a proof that arbitrary new content is safe.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ALLOWED_SUFFIXES = {'.md', '.json', '.tsv', '.txt', '.py', '.sh', '.S', '.dts',
                    '.config', '.yml', '.yaml'}
ALLOWED_DOTFILES = {'.gitignore', '.gitattributes'}
SKIP_DIRS = {'.git', '__pycache__', 'local-private'}
BLOCKED_DIRS = {'backups', 'logs', 'analysis', 'runtime', 'serve'}
# Approved README photograph, pinned to the reviewed bytes.
APPROVED_IMAGES = {
    'assets/xz000-g7.png': '62d4704a6b4c51a01728f657bfda26927403a2b726403ea077aaf784b1ce83e3',
}
EXAMPLE_MACS = {'02:00:00:12:34:56', '02-00-00-12-34-56',
                '00:00:00:00:00:00', '00-00-00-00-00-00',
                'FF:FF:FF:FF:FF:FF', 'FF-FF-FF-FF-FF-FF'}  # Ethernet broadcast
MAC = re.compile(r'(?<![0-9a-fA-F])(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}(?![0-9a-fA-F])'
                 r'|(?<![0-9a-fA-F])(?:[0-9a-fA-F]{2}-){5}[0-9a-fA-F]{2}(?![0-9a-fA-F])')
PRIVATE_KEY = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
TOKEN = re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b')
LOCAL_HOME = re.compile(r'/home/[A-Za-z0-9_.-]+(?:/|\b)')
LINK = re.compile(r'(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)|!\[[^\]\n]*\]\(([^)\n]+)\)')
HTML_IMAGE = re.compile(r'''<img\b[^>]*\bsrc=["']([^"']+)["']''', re.IGNORECASE)


def scan(root, private_fingerprints=()):
    root = Path(root).resolve()
    failures = []
    files = []
    fingerprints = [str(x).casefold() for x in private_fingerprints if x]

    def fail(path, rule, line=None):
        failures.append({'path': path, 'rule': rule, **({'line': line} if line else {})})

    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        name = relative.as_posix()
        if path.is_symlink():
            fail(name, 'symlink-not-allowed')
            continue
        if not path.is_file():
            continue
        files.append(path)
        if any(part in BLOCKED_DIRS for part in relative.parts):
            fail(name, 'private-directory')
        raw = path.read_bytes()
        if name in APPROVED_IMAGES:
            if hashlib.sha256(raw).hexdigest() != APPROVED_IMAGES[name]:
                fail(name, 'unapproved-image-content')
            continue
        if path.suffix not in ALLOWED_SUFFIXES and path.name not in ALLOWED_DOTFILES:
            fail(name, 'unapproved-file-type')
        if raw.startswith((b'\x7fELF', b'PK\x03\x04', b'\x1f\x8b', b'hsqs')) or b'\x00' in raw:
            fail(name, 'binary-content')
            continue
        try:
            content = raw.decode('utf-8')
        except UnicodeDecodeError:
            fail(name, 'non-utf8-content')
            continue
        searchable = name.casefold() + '\n' + content.casefold()
        if any(value in searchable for value in fingerprints):
            fail(name, 'private-fingerprint')
        for number, line in enumerate(content.splitlines(), 1):
            if any(x.group(0).upper() not in EXAMPLE_MACS for x in MAC.finditer(line)):
                fail(name, 'non-synthetic-mac', number)
            if PRIVATE_KEY.search(line): fail(name, 'private-key', number)
            if TOKEN.search(line): fail(name, 'credential-token', number)
            if LOCAL_HOME.search(line): fail(name, 'personal-home-path', number)
        if path.suffix == '.json':
            try:
                json.loads(content)
            except ValueError:
                fail(name, 'invalid-json')
        if path.suffix == '.md':
            urls = [match.group(1) or match.group(2) for match in LINK.finditer(content)]
            urls.extend(HTML_IMAGE.findall(content))
            for url in urls:
                url = url.strip().strip('<>')
                parsed = urlsplit(url)
                if parsed.scheme or url.startswith('#'):
                    continue
                target = (path.parent / unquote(parsed.path)).resolve()
                try:
                    target.relative_to(root)
                except ValueError:
                    fail(name, 'link-outside-package')
                    continue
                if parsed.path and not target.exists():
                    fail(name, 'missing-local-link')
    manifest = root / 'MANIFEST.sha256.txt'
    if manifest.is_file():
        listed = set()
        for number, line in enumerate(manifest.read_text().splitlines(), 1):
            try:
                digest, relative = line.split('  ', 1)
                target = (root / relative).resolve()
                target.relative_to(root)
                if not re.fullmatch(r'[0-9a-f]{64}', digest): raise ValueError()
                if relative in listed or target not in files: raise ValueError()
                listed.add(relative)
                if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                    fail('MANIFEST.sha256.txt', 'manifest-hash-mismatch', number)
            except (ValueError, OSError):
                fail('MANIFEST.sha256.txt', 'invalid-manifest-entry', number)
        expected = {p.relative_to(root).as_posix() for p in files if p != manifest}
        if listed != expected:
            fail('MANIFEST.sha256.txt', 'manifest-file-set-mismatch')
    return {'ok': not failures, 'files_checked': len(files),
            'exact_private_rules': len(fingerprints), 'failures': failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, nargs='?', default=Path('.'))
    parser.add_argument('--deny-file', type=Path,
                        help='external private JSON array; values are never printed')
    args = parser.parse_args()
    values = []
    if args.deny_file:
        deny = args.deny_file.resolve(strict=True)
        root = args.root.resolve(strict=True)
        if deny.is_relative_to(root):
            parser.error('private deny file must be outside the public repository')
        values = json.loads(deny.read_text())
        if not isinstance(values, list) or not all(isinstance(x, str) for x in values):
            parser.error('deny file must be a JSON array of strings')
    result = scan(args.root, values)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
