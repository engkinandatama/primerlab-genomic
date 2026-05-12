#!/usr/bin/env python3
"""
Diagnostic script to debug why find_exo_probe returns None.
Run this on HPC to see exactly what Tm values the probe scanner calculates.

Usage:
    python scripts/debug_probe.py
"""
import primer3
from primerlab.core.tools.thermocalc_wrapper import ThermocalcWrapper

# --- The BEST candidate amplicon from the last run ---
# FWD: CAAATATCATTGGGATCTTGCACTTGATAT (Tm: 63.7C, pos ~580)
# REV: CTGTTCCTGTCGATATTCTTCCCTCATAGA (Tm: 66.7C)
# Amplicon: 152 bp

SEQUENCE = (
    "AGCAAAAGCAGGTAGATATTGAAAGATGAGTCTTCTAACCGAGGTCGAAACGTACGTTCTCTCTATCATCCCGTCAGGCCCCCTCAAAGCCGAGATCGCGCAGAGACTTGAAGATGTCTTTGCAGGGAAGAACACAGATCTTGAGGCTCTCATGGAATGGCTAAAGACAAGACCAATCCTGTCACCTCTGACTAAGGGGATTTTAGGGTTTGTGTTCACGCTCACCGTGCCCAGTGAGCGAGGACTGCAGCGTAGACGCTTTGTCCAAAATGCCCTAAATGGGAATGGAGACCCAAACAACATGGACAGAGCAGTTAAACTGTACAGGAAACTGAAGAGAGAAATAACGTTCCATGGGGCCAAAGAAGTAGCACTCAGTTATTCAACTGGTGCACTTGCCAGTTGCATGGGCCTCATATACAACAGGATGGGGACAGTGACCACAGAAGTGGCTTTTGGCCTAGTGTGTGCCACTTGTGAGCAGATTGCTGATTCACAGCATCGGTCTCACAGGCAGATGGCGACTACCACCAATCCACTAATCAGGCATGAGAACAGAATGGTGCTGGCCAGCACTACAGCTAAGGCTATGGAGCAGATGGCTGGATCAAGTGAGCAGGCAGCGGAGGCCATGGAGGTTGCTAGTCAGGCTAGGCAGATGGTGCAGGCAATGAGAACCATTGGGACTCATCCTAGCTCCAGTGCTGGTCTAAGAGATGATCTTCTTGAAAATTTGCAGGCCTACCAGAAACGAATGGGAGTGCAGATGCAGCGATTCAAGTGATCCTCTCGTTATTGCCGCAAATATCATTGGGATCTTGCACTTGATATTGTGGATTCTTGATCGTCTTTTTTTCAAATGCATTTATCGTCGCTTTAAATACGGTTTGAAAAGAGGGCCTTCTACGGAAGGAGTGCCTGAGTCTATGAGGGAAGAATATCGACAGGAACAGCAGAGTGCTGTGGATGTTGACGATGGTCATTTTGTCAACATAGAGCTGGAGTAAAAAACTACCTTGTTTCTACT"
)

# Simulate: pick a representative amplicon region (around position 580-732 = 152bp)
# Use actual FWD/REV from the best candidate
FWD_SEQ = "CAAATATCATTGGGATCTTGCACTTGATAT"
REV_SEQ = "CTGTTCCTGTCGATATTCTTCCCTCATAGA"

# Find FWD position in sequence
fwd_pos = SEQUENCE.find(FWD_SEQ)
# REV is reverse complement on opposite strand, find the reverse complement in sequence
from primerlab.core.sequence import SequenceLoader
rev_rc = "".join({"A":"T","T":"A","C":"G","G":"C"}.get(b,b) for b in reversed(REV_SEQ))
rev_pos = SEQUENCE.find(rev_rc)

print(f"FWD position: {fwd_pos}, length: {len(FWD_SEQ)}")
print(f"REV rc position: {rev_pos}, REV length: {len(REV_SEQ)}")

if fwd_pos < 0 or rev_pos < 0:
    # Just use a manual slice from the middle of the sequence
    fwd_pos = 400
    rev_pos = fwd_pos + 152
    print(f"WARNING: Could not find exact primers. Using positions {fwd_pos}-{rev_pos}")

amp_full = SEQUENCE[fwd_pos : rev_pos + len(REV_SEQ)]
fwd_len = len(FWD_SEQ)
rev_len = len(REV_SEQ)
print(f"\nAmplicon length: {len(amp_full)} bp")
print(f"Amplicon: {amp_full[:40]}...{amp_full[-40:]}")

# --- Probe parameters ---
P_LEN_MIN = 46
P_LEN_MAX = 52
P_TM_MIN = 54.0
P_TM_MAX = 85.0
MIN_GAP = 5

print(f"\n{'='*70}")
print(f"PROBE SEARCH PARAMETERS:")
print(f"  Size range: {P_LEN_MIN}-{P_LEN_MAX} nt")
print(f"  Tm range:   {P_TM_MIN}-{P_TM_MAX} °C")
print(f"  Min gap:    {MIN_GAP} bp")
print(f"  FWD len:    {fwd_len}, REV len: {rev_len}")
print(f"{'='*70}")

# --- Test 1: Default calc_tm (NO Mg2+) ---
print(f"\n{'='*70}")
print("TEST 1: primer3.calc_tm() DEFAULT (0mM Mg2+, 50nM DNA)")
print(f"{'='*70}")

probe_start_min = fwd_len + MIN_GAP
tms_default = []
for p_len in [46, 48, 50, 52]:
    probe_start_max = len(amp_full) - rev_len - MIN_GAP - p_len
    if probe_start_max < probe_start_min:
        print(f"  Length {p_len}: NO ROOM (start_max={probe_start_max} < start_min={probe_start_min})")
        continue
    count = 0
    for i in range(probe_start_min, probe_start_max + 1):
        p_seq = amp_full[i:i+p_len]
        tm = primer3.calc_tm(p_seq)
        tms_default.append(tm)
        if count < 3:  # Show first 3
            status = "✅ PASS" if P_TM_MIN <= tm <= P_TM_MAX else "❌ FAIL"
            print(f"  len={p_len} pos={i}: Tm={tm:.1f}°C GC={sum(1 for b in p_seq if b in 'GC')/p_len*100:.0f}% {status}")
        count += 1
    passed = sum(1 for t in tms_default if P_TM_MIN <= t <= P_TM_MAX)
    print(f"  Length {p_len}: {count} positions scanned")

if tms_default:
    print(f"\n  Summary (DEFAULT): Tm range = {min(tms_default):.1f} - {max(tms_default):.1f} °C")
    passed = sum(1 for t in tms_default if P_TM_MIN <= t <= P_TM_MAX)
    print(f"  Passed filter ({P_TM_MIN}-{P_TM_MAX}°C): {passed}/{len(tms_default)}")

# --- Test 2: RAA conditions (14mM Mg2+, 480nM DNA) ---
print(f"\n{'='*70}")
print("TEST 2: ThermocalcWrapper with RAA conditions (14mM Mg2+, 480nM DNA)")
print(f"{'='*70}")

thermo = ThermocalcWrapper(
    mv_conc=50.0,
    dv_conc=14.0,
    dntp_conc=0.8,
    dna_conc=480.0,
    tm_method='santalucia',
    salt_corrections='owczarzy',
)

tms_raa = []
for p_len in [46, 48, 50, 52]:
    probe_start_max = len(amp_full) - rev_len - MIN_GAP - p_len
    if probe_start_max < probe_start_min:
        print(f"  Length {p_len}: NO ROOM")
        continue
    count = 0
    for i in range(probe_start_min, probe_start_max + 1):
        p_seq = amp_full[i:i+p_len]
        tm = thermo.calc_tm(p_seq)
        tms_raa.append(tm)
        if count < 3:
            status = "✅ PASS" if P_TM_MIN <= tm <= P_TM_MAX else "❌ FAIL"
            print(f"  len={p_len} pos={i}: Tm={tm:.1f}°C GC={sum(1 for b in p_seq if b in 'GC')/p_len*100:.0f}% {status}")
        count += 1
    print(f"  Length {p_len}: {count} positions scanned")

if tms_raa:
    print(f"\n  Summary (RAA): Tm range = {min(tms_raa):.1f} - {max(tms_raa):.1f} °C")
    passed = sum(1 for t in tms_raa if P_TM_MIN <= t <= P_TM_MAX)
    print(f"  Passed filter ({P_TM_MIN}-{P_TM_MAX}°C): {passed}/{len(tms_raa)}")
    if passed == 0:
        too_low = sum(1 for t in tms_raa if t < P_TM_MIN)
        too_high = sum(1 for t in tms_raa if t > P_TM_MAX)
        print(f"  ❌ DIAGNOSIS: {too_low} too cold (<{P_TM_MIN}°C), {too_high} too hot (>{P_TM_MAX}°C)")
        if too_high > too_low:
            print(f"  💡 RECOMMENDATION: Raise probe tm.max to {max(tms_raa):.0f}°C or higher")
        elif too_low > too_high:
            print(f"  💡 RECOMMENDATION: Lower probe tm.min to {min(tms_raa):.0f}°C or lower")

# --- Test 3: What Tm range would capture probes? ---
print(f"\n{'='*70}")
print("TEST 3: SUGGESTED Tm RANGE for this sequence")
print(f"{'='*70}")
if tms_raa:
    p10 = sorted(tms_raa)[len(tms_raa)//10]
    p90 = sorted(tms_raa)[len(tms_raa)*9//10]
    print(f"  10th percentile Tm: {p10:.1f}°C")
    print(f"  90th percentile Tm: {p90:.1f}°C")
    print(f"  Suggested range:    {p10-2:.0f} - {p90+2:.0f} °C")
    
    # Also check what the Primer3 INTERNAL oligo Tm would be
    print(f"\n  For reference, Primer3 reported primer Tms: 63.7°C (FWD), 66.7°C (REV)")
    print(f"  Probe Tm should typically be 3-10°C above primer Tm in RAA.")

print(f"\n{'='*70}")
print("DONE. Use this output to adjust probe.tm.min/max in your config.")
print(f"{'='*70}")
