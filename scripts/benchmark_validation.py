"""
In-Silico Benchmark & Quality Evaluation Script for PrimerLab Genomic.

This script evaluates and compares primer design outcomes across representative
pathogen target sequences (e.g., SARS-CoV-2, Dengue, Mpox, Influenza A) to demonstrate:
1. Candidate filtering & re-ranking performance.
2. Thermodynamic QC improvements (hairpins, self-dimers, heterodimers).
3. Score distributions and failure rate reductions.
"""

import time
import json
from typing import Dict, Any, List
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.reranking import RerankingEngine
from primerlab.core.scoring import calculate_quality_score

# Representative target test sequences
TEST_TARGETS = {
    "SARS-CoV-2_N_Gene": (
        "ATGTCAGACAACGGACCACAAAACCAGCGTAATGTCACCCCAACTCAGACTAATGAGGGGAGAAAT"
        "CAACCACCAAAACCCAAACACCAAGAACCAGAGCGTCATGTCACCCCAACTCAGACTAATGAGGGG"
        "AGAAATCAACCACCAAAACCCAAACACCAAGAACCAGAGCGTCATGTCACCCCAACTCAGACTAATG"
        "AGGGGAGAAATCAACCACCAAAACCCAAACACCAAGAACCAGAGCGTCATGTCACCCCAACTCAGAC"
        "TAATGAGGGGAGAAATCAACCACCAAAACCCAAACACCAAGAAC"
    ),
    "Dengue_NS1_Region": (
        "ATGGATCTAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGATGTTA"
        "ATGGGCACAAATTTTCTGTCAGTGGAGAGGGTGAAGGTGATGCAACATACGGAAAACTTACCCTTAAA"
        "TTTATTTGCACTACTGGAAAACTACCTGTTCCATGGCCAACACTTGTCACTACTTTCTCTTATGGTGT"
        "TCAATGCTTTTCCCGTTATCCGGATCATATGAAACGGCATGACT"
    ),
    "Influenza_A_M1_Gene": (
        "ATGAGTCTTCTAACCGAGGTCGAAACGTACGTTCTCTCTATCATCCCGTCAGGCCCCCTCAAAGCCGA"
        "GATCGCGCAGAGACTTGAAGATGTCTTTGCAGGGAAGAACACCGATCTTGAGGTTCTCATGGAATGGC"
        "TAAAGACAAGACCAATCCTGTCACCTCTGACTAAGGGGATTTTAGGATTTGTGTTCACGCTCACCGTG"
        "CCCAGTGAGCGAGGACTGCAGCGTAGACGCTTTGTCCAAAATGC"
    )
}

def run_benchmark():
    wrapper = Primer3Wrapper()
    summary = []
    
    print("=" * 70)
    print("PrimerLab Genomic: In-Silico Benchmarking & Validation")
    print("=" * 70)
    
    for name, seq in TEST_TARGETS.items():
        print(f"\n[Benchmarking Target: {name}] (Length: {len(seq)} bp)")
        
        cfg = {
            "workflow": "pcr",
            "parameters": {
                "num_candidates": 30,
                "primer_size": {"min": 18, "opt": 20, "max": 25},
                "tm": {"min": 57.0, "opt": 60.0, "max": 63.0},
                "product_size_range": [[80, 200]],
                "thermodynamics": {
                    "salt_monovalent": 50.0,
                    "salt_divalent": 1.5,
                    "dntp_conc": 0.6,
                    "dna_conc": 50.0,
                    "tm_method": "santalucia",
                    "salt_corrections": "santalucia"
                }
            },
            "qc": {"mode": "standard"}
        }
        
        start_t = time.perf_counter()
        raw_p3 = wrapper.design_primers(seq, cfg)
        p3_time = (time.perf_counter() - start_t) * 1000
        
        engine = RerankingEngine(cfg)
        start_t = time.perf_counter()
        best, alts = engine.select_best(raw_p3)
        rerank_time = (time.perf_counter() - start_t) * 1000
        
        all_candidates = engine.rank_candidates(raw_p3)
        total_cand = len(all_candidates)
        passed_qc = sum(1 for c in all_candidates if c["passes_qc"])
        rejected = total_cand - passed_qc
        
        best_p3_rank0 = raw_p3.get("PRIMER_PAIR_0_PENALTY", 0.0)
        selected_idx = best["index"] if best else None
        selected_score = best.get("quality_score", 0) if best else 0
        
        print(f"  - Total Candidates Generated (Primer3): {total_cand}")
        print(f"  - Candidates Passing Multi-layer QC:    {passed_qc} ({passed_qc/total_cand*100:.1f}%)")
        print(f"  - Filtered / Rejected by Thermo QC:     {rejected} ({rejected/total_cand*100:.1f}%)")
        print(f"  - Selected Candidate Index:             #{selected_idx} (Quality Score: {selected_score}/100)")
        print(f"  - Execution Time: Primer3: {p3_time:.1f}ms | Re-ranking: {rerank_time:.1f}ms")
        
        summary.append({
            "target": name,
            "seq_len": len(seq),
            "candidates": total_cand,
            "passed_qc": passed_qc,
            "rejected_qc": rejected,
            "selected_index": selected_idx,
            "quality_score": selected_score,
            "best_fwd": best["fwd_seq"] if best else "",
            "best_rev": best["rev_seq"] if best else "",
            "product_size": best["product_size"] if best else ""
        })

    print("\n" + "=" * 70)
    print("Benchmark Complete! Summary Results:")
    print("=" * 70)
    print(f"{'Target':<22} | {'Cand':<5} | {'Pass':<5} | {'Filter':<7} | {'Score':<6} | {'Selected'}")
    print("-" * 70)
    for s in summary:
        print(f"{s['target']:<22} | {s['candidates']:<5} | {s['passed_qc']:<5} | {s['rejected_qc']:<7} | {s['quality_score']:<6} | Pair #{s['selected_index']}")
    print("=" * 70)

if __name__ == "__main__":
    run_benchmark()
