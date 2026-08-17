"""Probe v4: fix stride math, persona 0x001, teammate +0x3D byte, record tables."""
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.editor import SaveEditor

USER_SAVEDATA = r"C:\Users\kufis\AppData\Roaming\SEGA\P5R\Steam\76561197984149929\savedata"
ORACLE_DIR = r"C:\Users\kufis\p5r_buff_save"

MASK = 0x09973
NBITS = 232

SAVES = []
for slot in range(1, 7):
    p = os.path.join(USER_SAVEDATA, f"DATA{slot:02d}", "DATA.DAT")
    if os.path.isfile(p):
        SAVES.append((f"user DATA{slot:02d}", p))
for slot in range(11, 17):
    p = os.path.join(ORACLE_DIR, f"DATA{slot:02d}", "DATA.DAT")
    if os.path.isfile(p):
        SAVES.append((f"oracle DATA{slot:02d}", p))

TABLE_W = 0x30  # 48-byte persona record
TABLE_N = 232
TABLE_BYTES = TABLE_N * TABLE_W  # 0x2B80


def mask_bits(d):
    out = set()
    for i in range(NBITS):
        if (d[MASK + i // 8] >> (i % 8)) & 1:
            out.add(i + 1)
    return out


def scan_record_tables(d, reg):
    hits = []
    max_off = max(0x8000, len(d) - TABLE_BYTES - 4)
    for tbase in range(0x8000, max_off, 0x10):
        match = 0
        for k in range(0, TABLE_N, 8):
            off = tbase + k * TABLE_W
            pid = struct.unpack_from("<H", d, off + 2)[0]
            lvl = d[off + 4]
            if pid in reg and 1 <= lvl <= 99:
                match += 1
        if match >= 18:
            hits.append((tbase, match))
    return sorted(hits, key=lambda h: -h[1])[:8]


ever = set()
clean = []
for label, path in SAVES:
    e = SaveEditor(open(path, "rb").read())
    if not e.is_real_save():
        continue
    d = e.parser.data_payload
    reg = mask_bits(d)
    ever |= reg
    clean.append((label, d, reg))

    # teammate +0x3D byte check: member struct base + 0x3D (unk after level)
    unk_vals = {}
    for m in (1, 2, 3, 4):
        base = 0x2C + m * 0x2B0
        unk_vals[m] = d[base + 0x3D]
    # Joker +0x3D is part of his player struct; check +0x0D instead (LV @ +0x0C)
    print(f"{label}: count={len(reg)} | member +0x3D bytes: {unk_vals}")

never = sorted(set(range(1, 233)) - ever)
print("\nNEVER-SET bits across ALL saves (incl. polluted DATA06):",
      [hex(x) for x in never])
clean_ever = set()
for _, d, reg in clean:
    if os.path.basename(os.path.dirname(SAVES[clean.index((_, d, reg))][1])) == "DATA06":
        continue
    clean_ever |= reg
# simpler: recompute excluding DATA06
clean_ever = set()
for label, d, reg in clean:
    if "DATA06" in label:
        continue
    clean_ever |= reg
never_clean = sorted(set(range(1, 233)) - clean_ever)
print("NEVER-SET bits across CLEAN saves:", [hex(x) for x in never_clean])

# persona 0x001 + the never-set names
tbl = SaveEditor()._load_table("Personas.txt")
for pid in never_clean:
    print(f"  bit {pid} = persona 0x{pid:03X} = {tbl.get(pid)}")

# record-table scan on richest clean save
richest = max([r for r in clean if "DATA06" not in r[0]], key=lambda r: len(r[2]))
label, d, reg = richest
print(f"\nrecord-table scan on {label} (count={len(reg)}):")
for base, m in scan_record_tables(d, reg):
    print(f"  candidate @0x{base:X} (match {m}/29)")
# dump the region right after primary mask
print("bytes at 0x09990..0x099C0 (right after mask):")
for off in range(0x09990, 0x099C0, 0x10):
    print("  ", hex(off), d[off:off + 0x10].hex())
