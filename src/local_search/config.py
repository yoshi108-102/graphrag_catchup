from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class LocalSearchStudyConfig:
    """local_search サンプル実装の設定値をまとめる。"""

    project_root: Path
    output_dir: Path
    lancedb_uri: Path
    community_level: int = 2

    community_report_table: str = "community_reports"
    entity_table: str = "entities"
    community_table: str = "communities"
    relationship_table: str = "relationships"
    covariate_table: str = "covariates"
    text_unit_table: str = "text_units"

    entity_description_index_name: str = "entity_description"

    @classmethod
    def from_project_root(cls, project_root: Path, community_level: int = 2) -> "LocalSearchStudyConfig":
        output_dir = project_root / "output"
        return cls(
            project_root=project_root,
            output_dir=output_dir,
            lancedb_uri=output_dir / "lancedb",
            community_level=community_level,
        )

    def parquet_path(self, table_name: str) -> Path:
        return self.output_dir / f"{table_name}.parquet"
