# Experimental RAM helpers

[Research index](../README.md) · [Account roles](../../docs/passwords.md)

These sources build modified application copies for specific **Build 250926** ELF files. They preserve the original input and check hashes, entry points, segments and patch regions. Proprietary input binaries, generated binaries and account dumps are not included.

## Purpose and observed results

| Builder | Added path | Result recorded in earlier sessions |
|---|---|---|
| [build_cfg_reader.py](build_cfg_reader.py) | `dm_shmInit(0)` → `dm_dumpCfg()` | Produced a configuration dump; private output excluded |
| [build_usercfg_reader.py](build_usercfg_reader.py) | Reads the existing `DEV2_USER_CFG` object | Read account state: root disabled, admin enabled |
| [build_web_replay.py](build_web_replay.py) | Replays existing HTTP/challenge/user messages | Restored port 80 after an httpd restart |
| [build_webroot.py](build_webroot.py) | RAM httpd role-0 account and UI-role mapping | Login succeeded; no new menus, management error `71231` |

The webroot experiment did not demonstrate a complete or permanent unlock. Builder manifests use `live_execution_verified=False` because building a file on a PC does not execute it on the ONT. That field is separate from the historical results above.

## Offline build

Keep extracted original binaries under `local-private/input/`. Outputs go to `local-private/helpers/`. Python `assert` checks are part of the input validation; do not run these builders with `python -O`.

The builders require `pyelftools`. The replay builder also needs an ARM-capable `clang`, selected with `ONT_CLANG` if necessary.

```sh
python3 -m pip install -r research/helpers/requirements.txt
python3 research/helpers/build_cfg_reader.py --source local-private/input/cli
python3 research/helpers/build_usercfg_reader.py --source local-private/input/cli
ONT_CLANG=clang python3 research/helpers/build_web_replay.py --source local-private/input/cli
python3 research/helpers/build_webroot.py --source local-private/input/httpd
```

Use a virtual environment for dependencies where appropriate. The builders do not install packages, connect to an ONT, stop services or write firmware.

The webroot builder generates a random local password for its private output directory and stores the credential file with mode `0600`. Both the generated binary and assembly contain that password and must remain private. No password from the earlier experiment is embedded in these sources.

Execution on the ONT is a separate experiment. The [access notes](../../docs/access.md#restarting-the-web-service) describe the web initialization and role restrictions that motivated these helpers.
