"""Audit probe v2: run against the REAL save ladder (user DATA01-06 + oracle DATA11-16).

Answers:
 1. Compendium count + exact bit sets per save; bits NEVER set in any real save
 2. Party-persona range (201-232) behavior across the ladder
 3. Joker stock slot flags: 0x1001 vs 0x0001 pattern
 4. Record-table hunt: 232-entry x 0x30 table near the masks?
"""
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.editor import SaveEditor

USER_SAVEDATA = r"C:\Users\kufis\AppData\Roaming\SEGA\P5R\Steam\76561197984149929\savedata"
ORACLE_DIR = r"C:\Users\kufis\p5r_buff_save"

MASK = 0x09973
MIRROR = 0x21E83
NBITS = 232
NBYTES = 29

SAVES = []
for slot in range(1, 7):
    p = os.path.join(USER_SAVEDATA, f"DATA{slot:02d}", "DATA.DAT")
    if os.path.isfile(p):
        SAVES.append((f"user DATA{slot:02d}", p))
for slot in range(11, 17):
    p = os.path.join(ORACLE_DIR, f"DATA{slot:02d}", "DATA.DAT")
    if os.path.isfile(p):
        SAVES.append((f"oracle DATA{slot:02d}", p))

print(f"found {len(SAVES)} saves\n")


def mask_set(d):
    out = set()
    for i in range(NBITS):
        if (d[MASK + i // 8] >> (i % 8)) & 1:
            out.add(i + 1)
    return out


def scan_record_tables(d, mask_set_bits):
    hits = []
    max_off = min(len(d) - 0x1BC0, 0x40000)
    for tbase in range(0x8000, max_off, 0x10):
        match = 0
        total = 0
        for k in range(0, 232, 8):
            off = tbase + k * 0x30
            pid = struct.unpack_from("<H", d, off + 2)[0]
            lvl = d[off + 4]
            flags = struct.unpack_from("<H", d, off)[0]
            if pid in mask_set_bits and 1 <= lvl <= 99:
                match += 1
            total += 1
        if match >= total * 0.6:
            hits.append((tbase, match))
    return sorted(hits, key=lambda h: -h[1])[:6]


all_bits = set(range(1, NBITS + 1))
ever_set = set()
results = {}

for label, path in SAVES:
    try:
        e = SaveEditor(open(path, "rb").read())
    except Exception as ex:
        print(f"{label}: LOAD FAIL {ex}")
        continue
    if not e.is_real_save():
        print(f"{label}: not pc31")
        continue
    d = e.parser.data_payload
    reg = mask_set(d)
    ever_set |= reg
    results[label] = (path, d, reg)

    print(f"== {label} ==  count={len(reg)}")
    party_bits = sorted(x for x in reg if x >= 201)
    print(f"   bits 201-232: {party_bits}")
    # Joker stock flags
    st = e.get_persona_stock(0)
    nonempty = [(k, hex(s["flags"]), hex(s["persona_id"]), s["level"])
                for k, s in enumerate(st) if not s["empty"]]
    print(f"   Joker stock (k, flags, id, lvl): {nonempty}")
    # mask==mirror?
    print(f"   mask==mirror: {d[MASK:MASK+NBYTES] == d[MIRROR:MIRROR+NBYTES]}")

print("\n=== BITS NEVER SET IN ANY REAL SAVE ===")
never = sorted(ever_set ^ all_bits)
print(f"count={len(never)}: {[hex(x) for x in never]}")
print("\n=== BITS SET IN EVERY SAVE (anchor set) ===")
common = set.intersection(*[set(r[2]) for r in results.values()]) if results else set()
print(f"count={len(common)}: {sorted(common)[:40]}")

# Record table scan on the richest save (oracle DATA11 if present)
richest = max(results.items(), key=lambda kv: len(kv[1][2]))
label, (path, d, reg) = richest
print(f"\n=== record-table scan on {label} (len={len(reg)}) ===")
print("hits:", scan_record_tables(d, reg))

# dump region after mask on richest save
print("region after primary mask:")
for off in range(MASK + NBYTES, MASK + NBYTES + 0x30, 0x10):
    print("   ", hex(off), d[off:off + 0x10].hex())
