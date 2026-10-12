"""Offline tests of parsing, privacy rejection and TFTP error/retry behavior."""
import importlib.util
import hashlib
import json
from pathlib import Path
import socket
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, directory=ROOT / 'tools'):
    spec = importlib.util.spec_from_file_location(name, directory / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


PASSWORD = module('admin_password')
PUBLIC = module('check_public', ROOT / '.github' / 'scripts')
BACKUP = module('backup_receiver')
IMAGE = module('inspect_image')


class OfflineTools(unittest.TestCase):
    def test_password_normalization_and_rejection(self):
        for mac in ['02:00:00:12:34:56', '02-00-00-12-34-56', '020000123456']:
            self.assertEqual(PASSWORD.default_admin_password(mac), 'TsPeLbN00123456')
        for value in ['02000012345', '0200001234567', 'not-a-mac', '02:00:00:12:34:ZZ']:
            with self.assertRaises(ValueError):
                PASSWORD.default_admin_password(value)

    def test_privacy_exact_canary_and_binaries(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / 'README.md').write_text('Safe example.\n')
            self.assertTrue(PUBLIC.scan(path)['ok'])
            (path / 'extra.txt').write_text('SECRET_CANARY_EXAMPLE_9876')
            result = PUBLIC.scan(path, ['SECRET_CANARY_EXAMPLE_9876'])
            self.assertFalse(result['ok'])
            self.assertNotIn('SECRET_CANARY', json.dumps(result))
            (path / 'extra.txt').unlink()
            (path / 'raw.bin').write_bytes(b'\x7fELF\x00')
            self.assertFalse(PUBLIC.scan(path)['ok'])

    def test_local_link_detection(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / 'README.md').write_text('[Missing](missing.md)\n')
            self.assertFalse(PUBLIC.scan(path)['ok'])
            (path / 'missing.md').write_text('Found.\n')
            self.assertTrue(PUBLIC.scan(path)['ok'])

    def test_manifest_detects_edits(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / 'README.md'
            target.write_text('Original\n')
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            (root / 'MANIFEST.sha256.txt').write_text(digest + '  README.md\n')
            self.assertTrue(PUBLIC.scan(root)['ok'])
            target.write_text('Edited\n')
            self.assertFalse(PUBLIC.scan(root)['ok'])

    def test_tftp_peer_path_and_duplicate_data(self):
        with tempfile.TemporaryDirectory() as folder:
            receiver = BACKUP.Receiver(folder, '192.0.2.1', announce=lambda *a, **kw: None)
            peer = ('192.0.2.1', 23456)
            wrq = lambda name: b'\x00\x02' + name.encode() + b'\x00octet\x00'
            self.assertIsNone(receiver.handle(wrq('meta/a.txt'), ('192.0.2.2', 1)))
            self.assertEqual(receiver.handle(wrq('../escape'), peer)[:2], b'\x00\x05')
            self.assertEqual(receiver.handle(wrq('meta/a.txt'), peer), b'\x00\x04\x00\x00')
            packet = struct.pack('!HH', 3, 1) + b'a' * 512
            ack = receiver.handle(packet, peer)
            self.assertEqual(ack, b'\x00\x04\x00\x01')
            self.assertEqual(receiver.handle(packet, peer), ack)
            final = struct.pack('!HH', 3, 2) + b'end'
            ack = receiver.handle(final, peer)
            self.assertEqual(receiver.handle(final, peer), ack)
            self.assertEqual((Path(folder) / 'meta/a.txt').read_bytes(), b'a' * 512 + b'end')
            self.assertEqual(receiver.handle(wrq('meta/a.txt'), peer)[:2], b'\x00\x05')

    def test_flash_map_and_truncated_image(self):
        data = bytearray(IMAGE.FLASH_BYTES)
        data[0x180000:0x180004] = b'hsqs'
        data[0x540000:0x540004] = b'hsqs'
        result = IMAGE.inspect(bytes(data), 'flash')
        self.assertTrue(all(result['squashfs_at_expected_roots'].values()))
        self.assertEqual(sum(x['bytes'] for x in result['partitions']), IMAGE.FLASH_BYTES)
        self.assertFalse(result['compatibility_verified'])
        with self.assertRaises(ValueError): IMAGE.inspect(b'bad', 'flash')
        with self.assertRaises(ValueError): IMAGE.inspect(b'bad', 'upgrade')

    def test_tftp_exact_block_requires_empty_final_packet(self):
        with tempfile.TemporaryDirectory() as folder:
            receiver = BACKUP.Receiver(folder, '192.0.2.1', announce=lambda *a, **kw: None)
            peer = ('192.0.2.1', 23456)
            receiver.handle(b'\x00\x02meta/exact.txt\x00octet\x00', peer)
            receiver.handle(struct.pack('!HH', 3, 1) + b'x' * 512, peer)
            target = Path(folder) / 'meta/exact.txt'
            self.assertFalse(target.exists())
            receiver.handle(struct.pack('!HH', 3, 2), peer)
            self.assertEqual(target.read_bytes(), b'x' * 512)

    def test_backup_two_reads_and_partition_reconstruction(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            # Synthetic bytes, unrelated to any device capture.
            data = bytes(range(256)) * (BACKUP.FLASH_SIZE // 256)
            for name in ['flash-a.bin', 'flash-b.bin']:
                (root / name).write_bytes(data)
            (root / 'meta').mkdir()
            (root / 'meta/complete.txt').write_text('CAPTURE_COMPLETE=1\nRUNTIME_ERRORS=0\n')
            report = BACKUP.verify_backup(root, extract=True)
            self.assertTrue(report['full_flash_verified'])
            self.assertTrue(report['capture_complete'])
            self.assertEqual(report['runtime_errors'], 0)
            parts = b''.join((root / 'partitions' / (name + '.bin')).read_bytes()
                             for name, _, _ in BACKUP.PARTITIONS)
            self.assertEqual(parts, data)
            with (root / 'flash-b.bin').open('r+b') as stream:
                stream.write(b'changed')
            self.assertFalse(BACKUP.verify_backup(root)['full_flash_verified'])


if __name__ == '__main__':
    unittest.main()
