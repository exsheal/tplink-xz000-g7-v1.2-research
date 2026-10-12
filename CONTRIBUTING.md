# Contributing

Results from other hardware revisions and firmware builds are particularly useful. Include the model, reported hardware revision, region and full firmware version so readers can tell whether a finding applies to their device.

Describe what you expected, what happened and how to reproduce it. State whether the result came from the web interface, TP-Link CLI, Linux shell or offline analysis. Keep live observations separate from symbols, templates and inferred behavior.

## Keep unit data private

Use synthetic identifiers such as `02:00:00:12:34:56` in examples. Exclude actual MAC/GPON serial/LOID values, passwords and account hashes, subscription/WAN details, Device IDs, raw flash dumps, current configuration and optical calibration data. Review screenshots and terminal excerpts for surrounding tabs, prompts and metadata as well.

Store local captures and generated helpers under `local-private/`, which is excluded from Git. Prefer a short sanitized excerpt or a reproducible code-path explanation over a complete firmware or source-bundle upload. Common package hashes and official download links are useful.

## Checks

Run the repository checker and existing offline tests before submitting:

```sh
python3 .github/scripts/check_public.py .
python3 -m unittest discover -s tests -v
```

The checker catches common identity patterns, binary files and broken relative links. It cannot replace reviewing the content you submit. Maintainers can additionally supply an external private fingerprint list with `--deny-file`.

See [NOTICE](NOTICE.md) for the repository's current licensing position. Third-party material keeps its original ownership and license terms.
