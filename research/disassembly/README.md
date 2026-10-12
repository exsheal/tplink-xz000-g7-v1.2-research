# Disassembly excerpts

[Research index](../README.md)

Selected ARM instructions and call paths support the findings below. Addresses belong to the examined 2025 build. Omitted fields are marked `WITHHELD`; complete proprietary binaries and runtime dumps are excluded.

| Excerpt | Subject |
|---|---|
| [password-identity.txt](password-identity.txt) | Default password construction and identity-record readers |
| [gcs-vlan.txt](gcs-vlan.txt) | GCS/OMCI VLAN application |
| [gpon-status-auth.txt](gpon-status-auth.txt) | GPON state, optical and authentication getters/setters |
| [firmware-upgrade.txt](firmware-upgrade.txt) | IMAGE_TAG and update validation |
| [crypto-verification.txt](crypto-verification.txt) | MD5/RSA paths and their limits |
| [gcs-heap-layout.txt](gcs-heap-layout.txt) | Serialized GCS object layout |
| [bank1-auth-initialization.txt](bank1-auth-initialization.txt) | Earlier 2025 GPON-auth initialization |

A traced path establishes implementation details in that binary. It does not establish that a change has been applied successfully under an operator's profile.
