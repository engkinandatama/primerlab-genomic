"""
Primer Selection Rationale Generator (v0.1.4)

Generates human-readable explanations for why a primer pair was selected,
including rejected candidates summary and comparison with alternatives.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from collections import Counter


@dataclass
class RejectionReason:
    """Single rejection reason with count."""
    reason: str
    count: int
    example_value: Optional[str] = None


@dataclass
class SelectionRationale:
    """Complete rationale for primer selection."""
    rank: int
    total_candidates: int
    candidates_passed_qc: int
    selection_reasons: List[str]
    rejection_summary: List[RejectionReason]
    comparison_notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "total_candidates": self.total_candidates,
            "candidates_passed_qc": self.candidates_passed_qc,
            "selection_reasons": self.selection_reasons,
            "rejection_summary": [
                {"reason": r.reason, "count": r.count, "example": r.example_value}
                for r in self.rejection_summary
            ],
            "comparison_notes": self.comparison_notes
        }

    def to_markdown(self) -> str:
        """Generate markdown formatted rationale."""
        lines = [
            "### Why This Primer?",
            "",
            f"**Selected as Rank #{self.rank}** from {self.total_candidates} candidates",
            f"({self.candidates_passed_qc} passed all QC checks)",
            "",
        ]

        # Selection reasons
        if self.selection_reasons:
            lines.append("**Selection reasons:**")
            for reason in self.selection_reasons:
                lines.append(f"- {reason}")
            lines.append("")

        # Rejection summary
        if self.rejection_summary:
            lines.append("**Rejected candidates:**")
            for r in self.rejection_summary[:5]:  # Top 5
                lines.append(f"- {r.count} failed: {r.reason}")
            lines.append("")

        # Comparison notes
        if self.comparison_notes:
            lines.append("**Compared to alternatives:**")
            for note in self.comparison_notes:
                lines.append(f"- {note}")

        return "\n".join(lines)


class RationaleTracker:
    """Tracks rejection reasons during candidate evaluation."""

    def __init__(self):
        self.rejections: List[Dict[str, Any]] = []
        self.passed: List[Dict[str, Any]] = []
        self.total_evaluated = 0

    def record_rejection(
        self, 
        candidate_id: int, 
        reason: str, 
        detail: Optional[str] = None
    ):
        """Record a rejected candidate."""
        self.rejections.append({
            "candidate_id": candidate_id,
            "reason": reason,
            "detail": detail
        })
        self.total_evaluated += 1

    def record_pass(
        self, 
        candidate_id: int, 
        score: float,
        primer3_penalty: float
    ):
        """Record a passing candidate."""
        self.passed.append({
            "candidate_id": candidate_id,
            "score": score,
            "primer3_penalty": primer3_penalty
        })
        self.total_evaluated += 1

    def get_rejection_summary(self) -> List[RejectionReason]:
        """Get summary of rejection reasons."""
        reason_counts = Counter(r["reason"] for r in self.rejections)

        summary = []
        for reason, count in reason_counts.most_common():
            # Find example
            example = next(
                (r["detail"] for r in self.rejections if r["reason"] == reason),
                None
            )
            summary.append(RejectionReason(
                reason=reason,
                count=count,
                example_value=example
            ))

        return summary

    def generate_rationale(
        self,
        selected_score: float,
        selected_penalty: float,
        selected_rank: int = 1
    ) -> SelectionRationale:
        """Generate complete rationale for selection."""

        # Selection reasons
        selection_reasons = []

        if selected_rank == 1:
            selection_reasons.append("Lowest combined score among all passing candidates")

        if len(self.passed) > 0:
            avg_penalty = sum(p["primer3_penalty"] for p in self.passed) / len(self.passed)
            if selected_penalty <= avg_penalty:
                selection_reasons.append(
                    f"Lower Primer3 penalty ({selected_penalty:.2f}) than average ({avg_penalty:.2f})"
                )

        selection_reasons.append("All thermodynamic QC checks passed")

        # Comparison notes
        comparison_notes = []
        if len(self.passed) > 1:
            scores = sorted([p["score"] for p in self.passed], reverse=True)
            if len(scores) > 1:
                comparison_notes.append(
                    f"Score {selected_score:.0f} vs next best {scores[1]:.0f}"
                )

        if len(self.rejections) > 0:
            comparison_notes.append(
                f"{len(self.rejections)} candidates rejected due to QC failures"
            )

        return SelectionRationale(
            rank=selected_rank,
            total_candidates=self.total_evaluated,
            candidates_passed_qc=len(self.passed),
            selection_reasons=selection_reasons,
            rejection_summary=self.get_rejection_summary(),
            comparison_notes=comparison_notes
        )

    def reset(self):
        """Reset tracker for new evaluation."""
        self.rejections = []
        self.passed = []
        self.total_evaluated = 0
