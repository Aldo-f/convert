from dataclasses import dataclass
from pathlib import Path

@dataclass
class ConversionRequest:
    source_path: Path
    target_path: Path
    src_fmt: str
    dst_fmt: str

@dataclass
class ConversionResult:
    output_path: Path
    message: str