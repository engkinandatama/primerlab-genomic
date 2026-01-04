"""
Sequence Alignment Engine.

Simple local alignment for primer binding site detection.
"""

import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


def reverse_complement(seq: str) -> str:
    """Get reverse complement of DNA sequence."""
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G',
                  'a': 't', 't': 'a', 'g': 'c', 'c': 'g',
                  'N': 'N', 'n': 'n'}
    return ''.join(complement.get(base, 'N') for base in reversed(seq))


def calculate_match_percent(primer: str, target: str) -> Tuple[float, int, List[int]]:
    """
    Calculate match percentage between primer and target.
    
    Returns:
        (match_percent, mismatch_count, mismatch_positions)
    """
    if len(primer) != len(target):
        min_len = min(len(primer), len(target))
        primer = primer[:min_len]
        target = target[:min_len]

    matches = 0
    mismatches = 0
    mismatch_positions = []

    for i, (p, t) in enumerate(zip(primer.upper(), target.upper())):
        if p == t:
            matches += 1
        else:
            mismatches += 1
            mismatch_positions.append(i)

    match_percent = (matches / len(primer)) * 100 if primer else 0
    return match_percent, mismatches, mismatch_positions


def find_binding_sites(
    primer: str,
    template: str,
    min_match_percent: float = 70.0,
    max_mismatches: int = 5
) -> List[Tuple[int, str, float, int, List[int]]]:
    """
    Find all potential binding sites for a primer on a template.
    
    Args:
        primer: Primer sequence
        template: Template DNA sequence
        min_match_percent: Minimum match % to report
        max_mismatches: Maximum mismatches allowed
        
    Returns:
        List of (position, strand, match_percent, mismatches, mismatch_positions)
    """
    primer = primer.upper()
    template = template.upper()
    primer_len = len(primer)
    primer_rc = reverse_complement(primer)

    sites = []

    # Scan forward strand
    for i in range(len(template) - primer_len + 1):
        window = template[i:i + primer_len]
        match_pct, mismatches, mm_pos = calculate_match_percent(primer, window)

        if match_pct >= min_match_percent and mismatches <= max_mismatches:
            sites.append((i, '+', match_pct, mismatches, mm_pos))

    # Scan reverse strand
    for i in range(len(template) - primer_len + 1):
        window = template[i:i + primer_len]
        match_pct, mismatches, mm_pos = calculate_match_percent(primer_rc, window)

        if match_pct >= min_match_percent and mismatches <= max_mismatches:
            sites.append((i, '-', match_pct, mismatches, mm_pos))

    # Sort by match percent descending
    sites.sort(key=lambda x: x[2], reverse=True)

    return sites


def local_align(
    seq1: str,
    seq2: str,
    match_score: int = 2,
    mismatch_penalty: int = -1,
    gap_penalty: int = -2
) -> Tuple[float, str, str]:
    """
    Simple Smith-Waterman local alignment.
    
    Returns:
        (alignment_score, aligned_seq1, aligned_seq2)
    """
    seq1 = seq1.upper()
    seq2 = seq2.upper()
    m, n = len(seq1), len(seq2)

    # Initialize scoring matrix
    score_matrix = [[0] * (n + 1) for _ in range(m + 1)]
    traceback = [[None] * (n + 1) for _ in range(m + 1)]

    max_score = 0
    max_pos = (0, 0)

    # Fill matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i-1] == seq2[j-1]:
                diag = score_matrix[i-1][j-1] + match_score
            else:
                diag = score_matrix[i-1][j-1] + mismatch_penalty

            up = score_matrix[i-1][j] + gap_penalty
            left = score_matrix[i][j-1] + gap_penalty

            score = max(0, diag, up, left)
            score_matrix[i][j] = score

            if score > max_score:
                max_score = score
                max_pos = (i, j)

            if score == diag:
                traceback[i][j] = 'D'
            elif score == up:
                traceback[i][j] = 'U'
            elif score == left:
                traceback[i][j] = 'L'

    # Traceback
    aligned1, aligned2 = [], []
    i, j = max_pos

    while i > 0 and j > 0 and score_matrix[i][j] > 0:
        if traceback[i][j] == 'D':
            aligned1.append(seq1[i-1])
            aligned2.append(seq2[j-1])
            i -= 1
            j -= 1
        elif traceback[i][j] == 'U':
            aligned1.append(seq1[i-1])
            aligned2.append('-')
            i -= 1
        else:
            aligned1.append('-')
            aligned2.append(seq2[j-1])
            j -= 1

    return max_score, ''.join(reversed(aligned1)), ''.join(reversed(aligned2))
