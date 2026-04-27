# 🔬 Audit: Primer3 Coverage di PrimerLab Genomic

> **Tujuan**: Identifikasi fungsi/parameter Primer3 yang belum di-wrap, dan rekomendasi prioritas implementasi.

---

## 1. APA YANG DIMILIKI PRIMER3-PY?

Primer3-py menyediakan **2 kelompok API utama**:

### A. `ThermoAnalysis` Class — Thermodynamic Calculations
Fungsi individual untuk perhitungan termodinamika:

| Fungsi Primer3-py | Parameter yang Dikembalikan | Status di PrimerLab |
|-------------------|-----------------------------|---------------------|
| `calc_tm(seq)` | Tm (°C) | ⚠️ **PARTIAL** — ada via ViennaRNA, tapi **belum pakai primer3's native `calc_tm`** |
| `calc_hairpin(seq)` | Tm, ΔG, ΔH, ΔS, struktur | ⚠️ **PARTIAL** — pakai ViennaRNA fallback, **bukan primer3 `calc_hairpin`** |
| `calc_homodimer(seq)` | Tm, ΔG, ΔH, ΔS, struktur | ⚠️ **PARTIAL** — ada via ViennaRNA `cofold`, **bukan primer3 `calc_homodimer`** |
| `calc_heterodimer(seq1, seq2)` | Tm, ΔG, ΔH, ΔS, struktur | ⚠️ **PARTIAL** — ada via ViennaRNA `cofold`, **bukan primer3 `calc_heterodimer`** |
| `calc_end_stability(seq)` | ΔG ujung 3' | ❌ **MISSING** — tidak ada wrapper sama sekali |

**Parameter `ThermoAnalysis` yang bisa dikonfigurasi:**

| Parameter | Keterangan | Status |
|-----------|-----------|--------|
| `mv_conc` | Monovalent cation conc (mM), default 50 | ⚠️ PARTIAL — ada `PRIMER_SALT_MONOVALENT` tapi tidak diekspose ke user config |
| `dv_conc` | Divalent cation conc (mM), default 1.5 | ❌ MISSING — tidak ada sama sekali |
| `dntp_conc` | dNTP conc (mM), default 0.6 | ❌ MISSING |
| `dna_conc` | DNA/oligo conc (nM), default 50 | ⚠️ PARTIAL — ada `PRIMER_DNA_CONC` tapi tidak diekspose |
| `temp_c` | Temperature (°C) untuk kalkulasi | ❌ MISSING |
| `tm_method` | `santalucia` atau `breslauer` | ❌ MISSING |
| `salt_corrections_method` | `santalucia`, `schildkraut`, `owczarzy` | ❌ MISSING |
| `max_loop` | Max loop size untuk hairpin/dimer, default 30 | ❌ MISSING |

---

### B. `design_primers()` — Global Args yang Belum Di-wrap

Primer3 punya **200+ parameter global**. Yang sudah di-wrap di `primer3_wrapper.py`:

#### ✅ SUDAH DI-WRAP (14 parameter):
```
SEQUENCE_TEMPLATE, PRIMER_TASK, PRIMER_PICK_LEFT_PRIMER,
PRIMER_PICK_RIGHT_PRIMER, PRIMER_NUM_RETURN,
PRIMER_OPT_SIZE, PRIMER_MIN_SIZE, PRIMER_MAX_SIZE,
PRIMER_OPT_TM, PRIMER_MIN_TM, PRIMER_MAX_TM,
PRIMER_MIN_GC, PRIMER_MAX_GC, PRIMER_PRODUCT_SIZE_RANGE,
PRIMER_PICK_INTERNAL_OLIGO (probe), + probe size/Tm/GC,
SEQUENCE_TARGET, SEQUENCE_EXCLUDED_REGION
```

#### ❌ BELUM DI-WRAP — Kategori Kritis:

**🔴 HIGH PRIORITY (langsung relevan untuk primer/probe design):**

| Parameter Primer3 | Fungsi | Dampak Jika Missing |
|-------------------|--------|---------------------|
| `PRIMER_SALT_MONOVALENT` | Salt monovalent (mM) untuk Tm calculation | Tm tidak akurat untuk kondisi lab spesifik |
| `PRIMER_SALT_DIVALENT` | Salt divalent/Mg²⁺ (mM) | Sangat penting untuk qPCR (pakai MgCl₂) |
| `PRIMER_DNTP_CONC` | Konsentrasi dNTP (mM) | Mempengaruhi Mg²⁺ bebas → Tm error |
| `PRIMER_DNA_CONC` | Konsentrasi oligo (nM) | Mempengaruhi Tm calculation |
| `PRIMER_MAX_POLY_X` | Max poly-X run (AAAA, TTTT, dll) | Saat ini pakai default Primer3, tidak user-configurable |
| `PRIMER_MAX_NS_ACCEPTED` | Max ambiguous base (N) | Penting untuk degenerate primer design |
| `PRIMER_MAX_SELF_ANY_TH` | Max self-complementarity (threshold method) | Lebih akurat dari ANY |
| `PRIMER_MAX_SELF_END_TH` | Max 3' self-complementarity (threshold) | Lebih akurat untuk 3'-dimer |
| `PRIMER_PAIR_MAX_COMPL_ANY_TH` | Max pair complementarity (threshold) | Heterodimer check lebih akurat |
| `PRIMER_PAIR_MAX_COMPL_END_TH` | Max pair 3' complementarity (threshold) | Penting untuk primer pair |
| `PRIMER_MAX_HAIRPIN_TH` | Max hairpin Tm (threshold method) | Kontrol hairpin lebih presisi |

**🟡 MEDIUM PRIORITY (fitur penting untuk workflow spesifik):**

| Parameter Primer3 | Fungsi | Use Case |
|-------------------|--------|----------|
| `PRIMER_INTERNAL_SALT_MONOVALENT` | Salt untuk probe Tm | qPCR probe Tm accuracy |
| `PRIMER_INTERNAL_SALT_DIVALENT` | Mg²⁺ untuk probe | qPCR |
| `PRIMER_INTERNAL_DNTP_CONC` | dNTP untuk probe | qPCR |
| `PRIMER_INTERNAL_DNA_CONC` | Konsentrasi probe | qPCR |
| `PRIMER_TM_FORMULA` | `1` (SantaLucia), `0` (Breslauer) | Konsistensi dengan lab protocol |
| `PRIMER_SALT_CORRECTIONS` | `1` (SantaLucia), `2` (Owczarzy) | Akurasi Tm di buffer berbeda |
| `PRIMER_SEQUENCING_LEAD` | Lead bp untuk sequencing primer | Sanger sequencing preset |
| `PRIMER_SEQUENCING_SPACING` | Spacing antar sequencing primer | Sanger sequencing |
| `PRIMER_SEQUENCING_ACCURACY` | Accuracy target untuk sequencing | Sanger sequencing |
| `SEQUENCE_INCLUDED_REGION` | Batasi region design dalam sekuens | Sudah ada via `target_region` tapi berbeda semantic |
| `SEQUENCE_FORCE_LEFT_START` | Paksa forward primer start di posisi tertentu | Cloning/restriction site design |
| `SEQUENCE_FORCE_LEFT_END` | Paksa forward primer end di posisi tertentu | Same |
| `SEQUENCE_FORCE_RIGHT_START` | Paksa reverse primer start | Same |
| `SEQUENCE_FORCE_RIGHT_END` | Paksa reverse primer end | Same |
| `PRIMER_MUST_MATCH_FIVE_PRIME` | Nucleotide constraint 5' end | Degenerate design |
| `PRIMER_MUST_MATCH_THREE_PRIME` | Nucleotide constraint 3' end | Allele-specific primer |
| `PRIMER_MIN_END_QUALITY` | Minimum quality di ujung primer | Next-gen sequencing |
| `PRIMER_MIN_QUALITY` | Minimum base quality | Same |
| `SEQUENCE_QUALITY` | Per-base quality scores | Same |

**🟢 LOW PRIORITY (niche / sangat advanced):**

| Parameter Primer3 | Fungsi |
|-------------------|--------|
| `misprime_lib` | Library repeat/unwanted sequences untuk mispriming check |
| `mishyb_lib` | Library untuk probe mishybridization check |
| `PRIMER_TASK` saat ini hanya `generic` | Belum ekspose: `pick_left_only`, `pick_right_only`, `pick_hyb_probe_only`, `check_primers`, `pick_sequencing_primers`, `pick_cloning_primers`, `pick_discriminative_primers` |
| `PRIMER_PAIR_MAX_DIFF_TM` | Max Tm difference antara forward & reverse | Sudah ada QC check tapi bukan dari Primer3 native |
| `PRIMER_OPT_GC_PERCENT` | Optimal GC% target | Sudah ada min/max tapi tidak ada optimal |
| `PRIMER_WT_*` | Bobot scoring untuk berbagai parameter | Fine-tuning primer ranking |
| `PRIMER_NUM_RETURN` | Sudah ada tapi hardcoded 30/50 | Perlu diekspose ke user |

---

## 2. MISSING DARI `ThermoAnalysis` — Yang Kritis

PrimerLab saat ini **tidak menggunakan `primer3.ThermoAnalysis` sama sekali** untuk thermodynamic calculations. Semua Tm/ΔG dihitung via:
- ViennaRNA (hairpin, homodimer, heterodimer)
- Custom fallback estimation (jika ViennaRNA tidak ada)

Ini berarti **perhitungan Tm tidak konsisten** dengan yang digunakan Primer3 internally saat mendesain primer. Seharusnya pakai `ThermoAnalysis.calc_tm()` yang identik dengan Primer3's internal calculation.

---

## 3. REKOMENDASI PRIORITAS IMPLEMENTASI

### 🔴 FASE 1 — Critical Fixes (High Impact, Relatively Easy)

#### 1a. Salt/Buffer Condition Support
**Kenapa penting**: Tm sangat bergantung pada salt concentration. Lab berbeda pakai kondisi berbeda (PCR buffer ≠ qPCR buffer dengan MgCl₂).

```yaml
# Yang seharusnya bisa dikonfigurasi user di YAML:
parameters:
  thermodynamics:
    salt_monovalent: 50.0    # mM, default 50
    salt_divalent: 1.5       # mM Mg²⁺, default 1.5
    dntp_conc: 0.6           # mM dNTP, default 0.6
    dna_conc: 50.0           # nM, default 50
    tm_method: santalucia    # santalucia | breslauer
    salt_corrections: santalucia  # santalucia | schildkraut | owczarzy
```

**Implementasi**: Tambahkan ke `primer3_wrapper.py` sebagai `global_args` + ekspose ke config schema.

#### 1b. Native `calc_tm` via `ThermoAnalysis`
**Kenapa penting**: Saat ini PrimerLab menghitung Tm sendiri, tapi Primer3 punya implementasi SantaLucia yang sangat akurat. Lebih baik pakai yang sama supaya konsisten.

```python
# Tambah ke primer3_wrapper.py atau buat ThermocalcWrapper baru
from primer3.thermoanalysis import ThermoAnalysis

class ThermocalcWrapper:
    def __init__(self, mv_conc=50.0, dv_conc=1.5, dntp_conc=0.6, dna_conc=50.0):
        self.ta = ThermoAnalysis(mv_conc=mv_conc, dv_conc=dv_conc,
                                  dntp_conc=dntp_conc, dna_conc=dna_conc)

    def calc_tm(self, seq: str) -> float:
        return self.ta.calc_tm(seq)

    def calc_hairpin(self, seq: str) -> dict:
        result = self.ta.calc_hairpin(seq)
        return {"tm": result.tm, "dg": result.dg, "dh": result.dh, "ds": result.ds}

    def calc_homodimer(self, seq: str) -> dict:
        result = self.ta.calc_homodimer(seq)
        return {"tm": result.tm, "dg": result.dg}

    def calc_heterodimer(self, seq1: str, seq2: str) -> dict:
        result = self.ta.calc_heterodimer(seq1, seq2)
        return {"tm": result.tm, "dg": result.dg}

    def calc_end_stability(self, seq: str) -> dict:
        result = self.ta.calc_end_stability(seq)
        return {"tm": result.tm, "dg": result.dg}
```

#### 1c. `PRIMER_PAIR_MAX_DIFF_TM` via Primer3
Saat ini QC Tm balance dilakukan manual di PrimerLab. Lebih baik passekan langsung ke Primer3 supaya filtering terjadi sebelum kandidat dikembalikan.

#### 1d. `PRIMER_MAX_POLY_X` & `PRIMER_MAX_NS_ACCEPTED`
Ekspose ke user config — saat ini pakai default Primer3 (100 untuk POLY_X = practically disabled).

---

### 🟡 FASE 2 — Feature Completeness

#### 2a. `PRIMER_TASK` Variants
Tambahkan support untuk Primer3 TASK lain:

| Task | Kegunaan di PrimerLab |
|------|-----------------------|
| `check_primers` | Validate existing primers (bukan design baru) — tambah ke `validate_primers` |
| `pick_left_only` | Design hanya forward primer (half-primer design) |
| `pick_right_only` | Design hanya reverse primer |
| `pick_hyb_probe_only` | Design hanya probe (pakai existing primers) |
| `pick_discriminative_primers` | Allele-specific design — sudah ada `genotyping/` tapi belum pakai Primer3 task ini |

```python
# Tambah ke CLI dan API:
primerlab check-primers --forward "ATGC..." --reverse "GCTA..." --template seq.fasta
primerlab design-probe --primers primers.json --template seq.fasta
```

#### 2b. Mispriming Library Support
Primer3 mendukung pengecekan terhadap **repeat/unwanted sequences** saat design:

```python
result = primer3.design_primers(
    seq_args=seq_args,
    global_args=global_args,
    misprime_lib={
        "ALU": "GGCCGGGCGCGGTGGCTCAC...",     # Alu repeat
        "LINE1": "CACCATGGAGCTCCTGATAT...",   # LINE-1 repeat
    },
    mishyb_lib={
        "PSEUDOGENE": "ATGCATGCATGCATGC..."   # Pseudogene untuk probe
    }
)
```

**Use case**: Sangat berguna untuk human genome primer design (banyak repeat elements).

#### 2c. Forced Primer Positions
```yaml
# Contoh YAML untuk cloning design:
parameters:
  force_left_start: 50    # Forward primer HARUS mulai di posisi 50
  force_right_end: 500    # Reverse primer HARUS selesai di posisi 500
```

#### 2d. `SEQUENCE_INCLUDED_REGION` vs current `target_region`
Saat ini PrimerLab pakai `SEQUENCE_TARGET` (primer harus **mengapit** region).
Primer3 juga punya `SEQUENCE_INCLUDED_REGION` (primer harus **berada di dalam** region).
Ini semantik berbeda — perlu keduanya.

---

### 🟢 FASE 3 — Nice to Have

#### 3a. Sequencing Primer Design
```bash
primerlab run sequencing --config sequencing.yaml
```
Dengan parameter: `PRIMER_SEQUENCING_LEAD`, `PRIMER_SEQUENCING_SPACING`, `PRIMER_SEQUENCING_ACCURACY`

#### 3b. Cloning Primer Design
```bash
primerlab run cloning --config cloning.yaml --add-restriction-sites EcoRI,BamHI
```
Dengan: `SEQUENCE_FORCE_LEFT_START`, restriction site overhang addition

#### 3c. Primer Weight Fine-tuning
```yaml
parameters:
  weights:
    tm_gt_opt: 1.0       # Weight penalty jika Tm > optimal
    tm_lt_opt: 1.0       # Weight penalty jika Tm < optimal
    size_gt_opt: 0.5     # Weight penalty jika size > optimal
    end_stability: 0.25  # Weight untuk 3' stability
    gc_clamp: 0.0        # Weight untuk GC clamp
```

---

## 4. SUMMARY MATRIX

| Kategori | Sudah Ada | Missing Kritis | Missing Nice-to-have |
|----------|-----------|----------------|----------------------|
| **Core Design** | PCR, qPCR, Nested | Cloning, Sequencing tasks | Discriminative design |
| **Thermodynamics** | Tm (custom), ΔG (ViennaRNA) | `calc_tm` native, `calc_end_stability`, salt/buffer config | Weight fine-tuning |
| **QC Parameters** | Hairpin, dimer, GC, Poly-X (default) | Salt config, `POLY_X` ekspose, `MAX_NS` | Sequence quality |
| **Specificity** | BLAST, in-silico, species check | Mispriming library | Mishybridization library |
| **Sequence Constraints** | Target region, excluded regions | Forced positions, `INCLUDED_REGION` | Nucleotide constraints |
| **Buffer Conditions** | ❌ Hardcoded defaults | **Salt, Mg²⁺, dNTP, DNA conc** | Per-primer conditions |
| **Probe Design** | TaqMan, SYBR | `pick_hyb_probe_only` task | Probe mishybridization |

---

## 5. QUICK WIN — Yang Paling Worth Dikerjakan Duluan

Berdasarkan **impact vs effort**:

1. **Salt/Buffer config** (effort: rendah, impact: tinggi) — tambahkan 4-6 parameter ke YAML schema dan `primer3_wrapper.py`
2. **`ThermocalcWrapper` menggunakan native primer3 `ThermoAnalysis`** (effort: sedang, impact: tinggi) — gantikan custom Tm dengan primer3's own SantaLucia
3. **`check_primers` TASK** (effort: rendah, impact: sedang) — existing primers validation via Primer3
4. **Mispriming library support** (effort: sedang, impact: sedang) — filter human repeats
5. **`calc_end_stability`** (effort: rendah, impact: sedang) — 3' stability ΔG yang lebih akurat
6. **Ekspose `PRIMER_MAX_POLY_X` ke user config** (effort: sangat rendah, impact: sedang)
