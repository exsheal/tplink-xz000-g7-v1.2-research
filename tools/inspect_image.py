#!/usr/bin/env python3
"""Read-only, basic format inspection of local XZ000-G7 files.

Does not print unit identity/calibration contents, flash hardware, execute
vendor code, or claim firmware compatibility/signature verification. A raw
image SHA-256 is a private fingerprint; do not publish the report unchanged.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

FLASH_BYTES = 0x800000
PARTITIONS = (
    ('uboot', 0, 0x20000), ('kernel1', 0x20000, 0x180000),
    ('rootfs1', 0x180000, 0x3e0000), ('kernel2', 0x3e0000, 0x540000),
    ('rootfs2', 0x540000, 0x7a0000), ('misc', 0x7a0000, 0x7f0000),
    ('hwconfig', 0x7f0000, 0x800000),
)


def inspect(data, kind='auto'):
    if kind == 'auto':
        kind = 'flash' if len(data) == FLASH_BYTES else 'upgrade'
    out = {'kind': kind, 'bytes': len(data),
           'sha256': hashlib.sha256(data).hexdigest(),
           'identity_contents_printed': False,
           'compatibility_verified': False,
           'signature_verified': False}
    if kind == 'flash':
        if len(data) != FLASH_BYTES:
            raise ValueError('Expected exactly 8 MiB for this v1.20 flash map')
        out['layout_assumption'] = 'TR v1.20; size alone does not prove model'
        out['partitions'] = [{'name': name, 'offset': hex(start), 'bytes': end-start}
                             for name, start, end in PARTITIONS]
        out['squashfs_at_expected_roots'] = {
            name: data[start:start+4] == b'hsqs'
            for name, start, _ in PARTITIONS if name.startswith('rootfs')}
        out['kernel_tag_bytes_assumed'] = 512
    else:
        if len(data) < 512:
            raise ValueError('File is shorter than the expected 512-byte IMAGE_TAG')
        out['header_bytes_assumed'] = 512
        # Probe a structural marker only. Do not decode account/identity words.
        out['squashfs_candidates'] = []
        offset = 512
        while True:
            found = data.find(b'hsqs', offset)
            if found < 0: break
            out['squashfs_candidates'].append(hex(found))
            if len(out['squashfs_candidates']) == 64:
                break
            offset = found + 4
        out['limits'] = 'Markers may be incidental; no vendor tag checks performed'
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--kind', choices=['auto', 'flash', 'upgrade'], default='auto')
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.image.read_bytes(), args.kind), indent=2))
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
