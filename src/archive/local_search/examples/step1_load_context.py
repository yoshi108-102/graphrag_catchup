"""Step 1: Local Search の入力データを読み込み、件数を確認する。"""

from pathlib import Path

from archive.local_search.config import LocalSearchStudyConfig
from archive.local_search.data_loader import load_local_search_resources


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    config = LocalSearchStudyConfig.from_project_root(project_root)

    resources = load_local_search_resources(config)

    # まずは Local Search の材料が揃っているかを確認する。
    print("=== Step1: Context Data Summary ===")
    print(f"entities: {len(resources.entities)}")
    print(f"relationships: {len(resources.relationships)}")
    print(f"community reports: {len(resources.reports)}")
    print(f"text units: {len(resources.text_units)}")
    print(f"covariates enabled: {resources.covariates is not None}")
    print(f"lancedb uri: {config.lancedb_uri}")
    print(f"entity description index: {config.entity_description_index_name}")

    print("\n--- entities preview ---")
    print(resources.entity_df.head(5).to_string())


if __name__ == "__main__":
    main()
