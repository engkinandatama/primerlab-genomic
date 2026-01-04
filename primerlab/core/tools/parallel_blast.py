"""
Parallel BLAST (v0.3.2)

Multi-threaded BLAST for batch primer processing.
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import logging

from primerlab.core.models.blast import BlastResult

logger = logging.getLogger(__name__)


@dataclass
class ParallelBlastTask:
    """A single BLAST task for parallel execution."""
    task_id: str
    query_seq: str
    database: str
    params: Optional[Dict[str, Any]] = None


@dataclass
class ParallelBlastResult:
    """Result from parallel BLAST execution."""
    task_id: str
    result: Optional[BlastResult]
    error: Optional[str] = None
    elapsed_time: float = 0.0


class ParallelBlastRunner:
    """
    Run multiple BLAST queries in parallel.
    
    Uses ThreadPoolExecutor for concurrent execution.
    """

    DEFAULT_THREADS = 4

    def __init__(
        self,
        blast_func: Callable,
        max_threads: int = DEFAULT_THREADS,
        timeout: Optional[float] = None
    ):
        """
        Initialize parallel runner.
        
        Args:
            blast_func: Function to run BLAST (query, database, params) -> BlastResult
            max_threads: Maximum number of parallel threads
            timeout: Timeout per task in seconds
        """
        self.blast_func = blast_func
        self.max_threads = max_threads
        self.timeout = timeout

    def run(
        self,
        tasks: List[ParallelBlastTask],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[ParallelBlastResult]:
        """
        Run multiple BLAST tasks in parallel.
        
        Args:
            tasks: List of BLAST tasks
            progress_callback: Callback for progress updates (current, total)
            
        Returns:
            List of results in same order as tasks
        """
        if not tasks:
            return []

        results: Dict[str, ParallelBlastResult] = {}
        completed = 0
        total = len(tasks)

        logger.info(f"Running {total} BLAST tasks with {self.max_threads} threads")

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._run_task, task): task
                for task in tasks
            }

            # Collect results
            for future in as_completed(future_to_task):
                task = future_to_task[future]

                try:
                    result = future.result(timeout=self.timeout)
                    results[task.task_id] = result
                except Exception as e:
                    results[task.task_id] = ParallelBlastResult(
                        task_id=task.task_id,
                        result=None,
                        error=str(e)
                    )

                completed += 1
                if progress_callback:
                    progress_callback(completed, total)

        # Return in original order
        return [results.get(task.task_id) for task in tasks]

    def _run_task(self, task: ParallelBlastTask) -> ParallelBlastResult:
        """Run a single BLAST task."""
        import time
        start_time = time.time()

        try:
            result = self.blast_func(
                task.query_seq,
                task.database,
                task.params or {}
            )

            elapsed = time.time() - start_time

            return ParallelBlastResult(
                task_id=task.task_id,
                result=result,
                elapsed_time=elapsed
            )

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Task {task.task_id} failed: {e}")

            return ParallelBlastResult(
                task_id=task.task_id,
                result=None,
                error=str(e),
                elapsed_time=elapsed
            )


def run_parallel_blast(
    queries: List[str],
    database: str,
    blast_func: Callable,
    max_threads: int = 4,
    progress_callback: Optional[Callable] = None
) -> List[Optional[BlastResult]]:
    """
    Convenience function for parallel BLAST.
    
    Args:
        queries: List of query sequences
        database: Database path
        blast_func: BLAST function
        max_threads: Number of threads
        progress_callback: Progress callback
        
    Returns:
        List of BlastResult (or None on error)
    """
    tasks = [
        ParallelBlastTask(
            task_id=f"query_{i}",
            query_seq=q,
            database=database
        )
        for i, q in enumerate(queries)
    ]

    runner = ParallelBlastRunner(
        blast_func=blast_func,
        max_threads=max_threads
    )

    results = runner.run(tasks, progress_callback)

    return [r.result if r else None for r in results]
