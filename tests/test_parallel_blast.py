"""
Tests for Parallel BLAST (v0.3.2)
"""

import pytest
import time
from typing import Dict, Any

from primerlab.core.tools.parallel_blast import (
    ParallelBlastTask,
    ParallelBlastResult,
    ParallelBlastRunner,
    run_parallel_blast
)
from primerlab.core.models.blast import BlastResult, BlastHit


# Mock BLAST function for testing
def mock_blast_func(query_seq: str, database: str, params: Dict[str, Any]) -> BlastResult:
    """Simulated BLAST function."""
    time.sleep(0.05)  # Simulate work (shorter for tests)
    
    return BlastResult(
        query_id=f"query_{query_seq[:4]}",
        query_seq=query_seq,
        hits=[
            BlastHit(
                subject_id="hit_1",
                subject_title=f"Hit for {query_seq[:4]}",
                identity=95.0,
                alignment_length=len(query_seq),
                mismatches=1,
                gaps=0,
                query_start=1,
                query_end=len(query_seq),
                subject_start=100,
                subject_end=100 + len(query_seq),
                evalue=0.001,
                bit_score=50.0
            )
        ]
    )


def mock_failing_blast(query_seq: str, database: str, params: Dict[str, Any]):
    """BLAST function that raises an error."""
    raise ValueError(f"Simulated error for {query_seq}")


class TestParallelBlastTask:
    """Tests for ParallelBlastTask dataclass."""
    
    def test_task_creation(self):
        """Task should be created correctly."""
        task = ParallelBlastTask(
            task_id="test_1",
            query_seq="ATGCATGC",
            database="/db.fasta"
        )
        
        assert task.task_id == "test_1"
        assert task.query_seq == "ATGCATGC"
        assert task.database == "/db.fasta"


class TestParallelBlastRunner:
    """Tests for ParallelBlastRunner."""
    
    def test_run_single_task(self):
        """Should run a single task."""
        runner = ParallelBlastRunner(mock_blast_func, max_threads=1)
        
        tasks = [
            ParallelBlastTask("task_1", "ATGCATGC", "/db.fasta")
        ]
        
        results = runner.run(tasks)
        
        assert len(results) == 1
        assert results[0].task_id == "task_1"
        assert results[0].result is not None
        assert results[0].error is None
    
    def test_run_multiple_tasks(self):
        """Should run multiple tasks in parallel."""
        runner = ParallelBlastRunner(mock_blast_func, max_threads=4)
        
        tasks = [
            ParallelBlastTask(f"task_{i}", f"ATGCATGC{i}", "/db.fasta")
            for i in range(5)
        ]
        
        results = runner.run(tasks)
        
        assert len(results) == 5
        # Check all results have results (not None)
        for r in results:
            assert r is not None
            assert r.result is not None or r.error is not None
    
    def test_run_preserves_order(self):
        """Results should be in same order as tasks."""
        runner = ParallelBlastRunner(mock_blast_func, max_threads=4)
        
        tasks = [
            ParallelBlastTask(f"task_{i}", f"SEQ_{i}", "/db.fasta")
            for i in range(3)
        ]
        
        results = runner.run(tasks)
        
        for i, result in enumerate(results):
            assert result.task_id == f"task_{i}"
    
    def test_run_with_progress_callback(self):
        """Progress callback should be called."""
        runner = ParallelBlastRunner(mock_blast_func, max_threads=2)
        
        progress_calls = []
        
        def progress_cb(current, total):
            progress_calls.append((current, total))
        
        tasks = [
            ParallelBlastTask(f"task_{i}", f"SEQ_{i}", "/db.fasta")
            for i in range(3)
        ]
        
        runner.run(tasks, progress_callback=progress_cb)
        
        assert len(progress_calls) == 3
        assert progress_calls[-1] == (3, 3)
    
    def test_run_handles_errors(self):
        """Should handle task errors gracefully."""
        runner = ParallelBlastRunner(mock_failing_blast, max_threads=2)
        
        tasks = [
            ParallelBlastTask("task_1", "ATGC", "/db.fasta")
        ]
        
        results = runner.run(tasks)
        
        assert len(results) == 1
        assert results[0].result is None
        assert results[0].error is not None
        assert "Simulated error" in results[0].error
    
    def test_run_empty_tasks(self):
        """Should handle empty task list."""
        runner = ParallelBlastRunner(mock_blast_func)
        
        results = runner.run([])
        
        assert results == []


class TestRunParallelBlast:
    """Tests for convenience function."""
    
    def test_run_parallel_blast(self):
        """Convenience function should work."""
        queries = ["ATGCATGC", "GCTAATGC", "TTAAGCAT"]
        
        # Wrapper that handles params correctly
        def wrapper_blast(query, db, params):
            return mock_blast_func(query, db, params)
        
        results = run_parallel_blast(
            queries=queries,
            database="/db.fasta",
            blast_func=wrapper_blast,
            max_threads=2
        )
        
        assert len(results) == 3
        assert all(r is not None for r in results)
