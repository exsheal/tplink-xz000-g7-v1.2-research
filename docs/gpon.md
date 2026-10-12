# GPON, optical status and OLT information

[Back to the guide](../README.md#gpon)

## Registration state and ONU ID

The examined unit reached **O5**, the operational GPON activation state. This establishes activation on the PON; Internet service also requires the right VLAN, GEM and PPPoE configuration.

The OLT assigns the **ONU ID** to identify an ONU on that PON. It is not an OLT model number, a chassis slot, a port number, a GPON serial or a count of subscribers. The attached OLT's make/model was not established from these backups.

An `OLTMode` or vendor-compatibility selection in configuration identifies a supported mode, not necessarily the operator's actual equipment.

## Can the OLT model be queried?

OMCI **OLT-G**, class `131`, instance `0`, may contain vendor, equipment and version attributes. The firmware includes this local query:

```sh
gc_omcicli mib get 131 0
```

It requires a **Linux shell**. It is not a TP-Link `TP-Link(conf)#` command. Its presence was verified statically; a live reply was not captured, and an OLT may leave some fields empty.

UART is not required by OMCI itself. Another authorized Linux-shell or local-MIB interface could perform the query, but neither a normal admin-CLI path nor a web field exposing OLT-G has been confirmed here.

See [ITU-T G.988](https://www.itu.int/rec/T-REC-G.988/en) and the [OLT-G definition, section 9.12.2](https://www.ietf.org/lib/dt/documents/LIAISON/file1019.pdf).

## Optical readings

The web interface exposes Tx/Rx power, temperature, supply voltage and bias current. These fields use real optical getter paths, including `gccli bob opt`; they are not merely unused template labels.

UX3320S was detected live. The runtime optical block and corresponding flash block matched at 4096 bytes. Device-specific measurements and calibration data are kept private. Files named `gc_default_bob_*.bin` can be ASCII register tables for other supported BOB families, rather than proof that each family is installed on this unit.

Partial defaults in the UX3320S path do not establish that the whole calibration is generic. Laser power, bias and LOS-threshold changes were not tested.

Some traffic displays are affected by 32-bit counters or signed conversion limits. A displayed maximum such as `2147483647` is not evidence of a traffic quota. The two displayed FEC fields may share a getter; they should not be treated as two independently verified controls.

## VLAN configuration path

The traced apply path is:

```text
data model
  → OMCI reload message 707
  → gc_omcid
  → gcOmci_tpSetVlanMode
  → libgc_netApi_setVlanMode
  → gcnet ioctl, with NAT/FDB clearing
```

The decoded modes are `0 = OLT`, `1 = Tag`, `2 = Transparent`; the traced input range is VID 1–4094 and priority 0–7. In this build, the relevant functions occur at `0x1df24` in `gc_omcid` and `0x6d00` in `libgc`. Addresses are build-specific.

The code establishes an apply path, not successful operation of every VLAN or OMCI profile. Full trunk/translation combinations and alternate operator profiles were not tested. [VLAN disassembly](../research/disassembly/gcs-vlan.txt) and [GPON status/auth paths](../research/disassembly/gpon-status-auth.txt) provide the supporting excerpts.
