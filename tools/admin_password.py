#!/usr/bin/env python3
"""Calculate the XZ000-G7 TR Build 250926 default admin password from a LAN MAC."""

import argparse
import re


def default_admin_password(mac: str) -> str:
    mac = mac.strip()
    if not (
        re.fullmatch(r"[0-9a-fA-F]{12}", mac)
        or re.fullmatch(r"[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}", mac)
        or re.fullmatch(r"[0-9a-fA-F]{2}(?:-[0-9a-fA-F]{2}){5}", mac)
    ):
        raise ValueError("Expected a six-byte MAC address, for example 02:00:00:12:34:56.")
    normalized = mac.replace(":", "").replace("-", "").upper()
    return "TsPeLbN" + normalized[-8:]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Calculate the conditional default password for XZ000-G7 TR v1.20 Build 250926. "
            "The result does not recover a changed password or establish defaults for another build."
        )
    )
    parser.add_argument("mac", help="the ONT's LAN MAC address")
    args = parser.parse_args()
    try:
        password = default_admin_password(args.mac)
    except ValueError as error:
        parser.error(str(error))
    print(password)


if __name__ == "__main__":
    main()
