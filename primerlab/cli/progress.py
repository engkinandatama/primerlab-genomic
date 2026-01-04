"""
Progress Indicator (v0.3.2)

Progress bars and spinners for CLI operations.
"""

import sys
import time
import threading
from typing import Optional, Callable
from contextlib import contextmanager


class Spinner:
    """
    Simple terminal spinner for indeterminate operations.
    """

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str = "Loading", delay: float = 0.1):
        """
        Initialize spinner.
        
        Args:
            message: Message to display
            delay: Frame delay in seconds
        """
        self.message = message
        self.delay = delay
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _spin(self):
        """Spinner animation loop."""
        idx = 0
        while not self._stop_event.is_set():
            frame = self.FRAMES[idx % len(self.FRAMES)]
            sys.stdout.write(f"\r   {frame} {self.message}...")
            sys.stdout.flush()
            idx += 1
            time.sleep(self.delay)

    def start(self):
        """Start the spinner."""
        if self._thread is None:
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()

    def stop(self, success: bool = True):
        """Stop the spinner and show result."""
        if self._thread is not None:
            self._stop_event.set()
            self._thread.join(timeout=1)
            self._thread = None

            # Clear line and show result
            icon = "✅" if success else "❌"
            sys.stdout.write(f"\r   {icon} {self.message}    \n")
            sys.stdout.flush()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop(success=exc_type is None)
        return False


class ProgressBar:
    """
    Simple terminal progress bar.
    """

    def __init__(
        self,
        total: int,
        message: str = "Progress",
        width: int = 30,
        show_eta: bool = True
    ):
        """
        Initialize progress bar.
        
        Args:
            total: Total number of items
            message: Message to display
            width: Bar width in characters
            show_eta: Whether to show ETA
        """
        self.total = total
        self.message = message
        self.width = width
        self.show_eta = show_eta
        self.current = 0
        self.start_time = time.time()

    def update(self, n: int = 1):
        """Update progress by n items."""
        self.current += n
        self._render()

    def set(self, value: int):
        """Set progress to specific value."""
        self.current = value
        self._render()

    def _render(self):
        """Render the progress bar."""
        if self.total == 0:
            pct = 100
        else:
            pct = min(100, int(100 * self.current / self.total))

        filled = int(self.width * pct / 100)
        bar = "█" * filled + "░" * (self.width - filled)

        # ETA calculation
        eta_str = ""
        if self.show_eta and self.current > 0:
            elapsed = time.time() - self.start_time
            rate = self.current / elapsed
            remaining = (self.total - self.current) / rate if rate > 0 else 0
            eta_str = f" ETA: {remaining:.0f}s"

        sys.stdout.write(f"\r   {self.message}: [{bar}] {pct}%{eta_str}  ")
        sys.stdout.flush()

        if self.current >= self.total:
            sys.stdout.write("\n")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.current < self.total:
            sys.stdout.write("\n")
        return False


@contextmanager
def spinner(message: str = "Loading"):
    """
    Context manager for spinner.
    
    Usage:
        with spinner("Loading database"):
            load_database()
    """
    s = Spinner(message)
    s.start()
    try:
        yield s
    finally:
        s.stop(success=True)


@contextmanager
def progress(total: int, message: str = "Progress"):
    """
    Context manager for progress bar.
    
    Usage:
        with progress(100, "Processing") as bar:
            for i in range(100):
                bar.update()
    """
    bar = ProgressBar(total, message)
    try:
        yield bar
    finally:
        pass


def show_spinner(message: str, func: Callable, *args, **kwargs):
    """
    Run function with spinner.
    
    Args:
        message: Spinner message
        func: Function to run
        *args, **kwargs: Function arguments
        
    Returns:
        Function result
    """
    with spinner(message):
        return func(*args, **kwargs)
