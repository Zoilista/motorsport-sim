"""Telemetry Recorder module for high-frequency telemetry logging.

Exports deterministic 20 Hz simulation telemetry data to CSV format
for offline engineering analysis, sensitivity studies, and integration
with data science libraries (Pandas, Matplotlib, FastF1).
"""

from __future__ import annotations

import csv
import os
from typing import TYPE_CHECKING, Any, ClassVar, Self, TextIO

if TYPE_CHECKING:
    from simulation.telemetry import Telemetry


class TelemetryRecorder:
    """Records real-time telemetry frames to CSV format."""

    HEADERS: ClassVar[tuple[str, ...]] = (
        "timestamp_s",
        "lap",
        "sector",
        "speed_kmh",
        "throttle_pct",
        "brake_pct",
        "gear",
        "rpm",
        "fl_temp_c",
        "fr_temp_c",
        "rl_temp_c",
        "rr_temp_c",
        "ers_soc_pct",
        "aero_mode",
        "compound",
    )

    def __init__(self, output_path: str = "telemetry_exports/race_telemetry.csv") -> None:
        self.output_path = output_path
        self._file: TextIO | None = None
        self._writer: Any = None
        self._frame_count = 0
        self._init_file()

    def _init_file(self) -> None:
        """Ensures target directory exists and initializes the CSV file with headers."""
        dirname = os.path.dirname(self.output_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        self._file = open(self.output_path, mode="w", newline="", encoding="utf-8")  # noqa: SIM115
        writer = csv.writer(self._file)
        writer.writerow(self.HEADERS)
        self._writer = writer
        self._file.flush()

    def record_frame(
        self,
        telemetry: Telemetry,
        timestamp_s: float = 0.0,
        lap: int = 1,
    ) -> None:
        """Appends a single telemetry snapshot to the CSV log."""
        if self._writer is None or self._file is None:
            raise RuntimeError("TelemetryRecorder is closed.")

        row = [
            f"{timestamp_s:.3f}",
            lap,
            telemetry.sector,
            f"{telemetry.speed:.2f}",
            f"{telemetry.throttle * 100.0:.1f}",
            f"{telemetry.brake * 100.0:.1f}",
            telemetry.gear,
            f"{telemetry.rpm:.0f}",
            f"{telemetry.fl_temp:.1f}",
            f"{telemetry.fr_temp:.1f}",
            f"{telemetry.rl_temp:.1f}",
            f"{telemetry.rr_temp:.1f}",
            f"{telemetry.ers_soc_pct:.1f}",
            telemetry.aero_mode,
            telemetry.compound,
        ]
        self._writer.writerow(row)
        self._frame_count += 1

    def flush(self) -> None:
        """Flushes buffered telemetry data to disk."""
        if self._file and not self._file.closed:
            self._file.flush()

    def close(self) -> None:
        """Closes the underlying CSV file."""
        if self._file and not self._file.closed:
            self._file.flush()
            self._file.close()
            self._file = None
            self._writer = None

    @property
    def frame_count(self) -> int:
        """Returns the number of recorded telemetry rows."""
        return self._frame_count

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()
