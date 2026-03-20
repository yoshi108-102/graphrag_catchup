from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class NanoGraphRAGStudyConfig:
    """Configuration for nano-graphrag study scripts."""

    project_root: Path
    input_text_path: Path
    working_dir: Path

    @classmethod
    def from_project_root(cls, project_root: Path) -> "NanoGraphRAGStudyConfig":
        return cls(
            project_root=project_root,
            input_text_path=project_root / "input" / "book.txt",
            working_dir=project_root / "cache" / "nano_graphrag",
        )
