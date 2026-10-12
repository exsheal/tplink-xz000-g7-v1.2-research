#!/usr/bin/env python3
"""XZ000-G7 TR Build 250926 varsayılan admin parolasını MAC'ten hesapla."""

import argparse
import re


def default_admin_password(mac: str) -> str:
    mac = mac.strip()
    if not (
        re.fullmatch(r"[0-9a-fA-F]{12}", mac)
        or re.fullmatch(r"[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}", mac)
        or re.fullmatch(r"[0-9a-fA-F]{2}(?:-[0-9a-fA-F]{2}){5}", mac)
    ):
        raise ValueError("MAC adresi 6 bayt olmalı: 02:00:00:12:34:56 gibi.")
    normalized = mac.replace(":", "").replace("-", "").upper()
    return "TsPeLbN" + normalized[-8:]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "XZ000-G7 TR v1.20 Build 250926 varsayılan parolası. "
            "Sonradan değiştirilmiş parola veya başka firmware için geçerli olmayabilir."
        )
    )
    parser.add_argument("mac", help="ONT'nin gerçek LAN MAC adresi")
    args = parser.parse_args()
    try:
        password = default_admin_password(args.mac)
    except ValueError as error:
        parser.error(str(error))
    print(password)


if __name__ == "__main__":
    main()
