from dataclasses import dataclass
from typing import Any

import pandas as pd
from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag_vectors.lancedb import LanceDBVectorStore

from .config import LocalSearchStudyConfig


@dataclass(slots=True)
class LocalSearchResources:
    """Local Search の context builder に渡す材料を保持する。"""

    entities: list[Any]
    relationships: list[Any]
    reports: list[Any]
    text_units: list[Any]
    covariates: dict[str, list[Any]] | None
    description_embedding_store: LanceDBVectorStore

    # デバッグ・学習用に元データフレームも保持する。
    entity_df: pd.DataFrame
    relationship_df: pd.DataFrame
    report_df: pd.DataFrame
    text_unit_df: pd.DataFrame


def _load_covariates_if_exists(config: LocalSearchStudyConfig) -> dict[str, list[Any]] | None:
    covariate_path = config.parquet_path(config.covariate_table)
    if not covariate_path.exists():
        return None

    covariate_df = pd.read_parquet(covariate_path)
    claims = read_indexer_covariates(covariate_df)
    return {"claims": claims}


def _build_description_embedding_store(config: LocalSearchStudyConfig) -> LanceDBVectorStore:
    # ノートブックと同じく、LanceDB を entity description 用の index として使う。
    store = LanceDBVectorStore(
        db_uri=str(config.lancedb_uri),
        index_name=config.entity_description_index_name,
    )
    store.connect()
    return store


def load_local_search_resources(config: LocalSearchStudyConfig) -> LocalSearchResources:
    """Parquet と LanceDB を読み込み、Local Search 用の構造化データを作る。"""

    entity_df = pd.read_parquet(config.parquet_path(config.entity_table))
    community_df = pd.read_parquet(config.parquet_path(config.community_table))
    relationship_df = pd.read_parquet(config.parquet_path(config.relationship_table))
    report_df = pd.read_parquet(config.parquet_path(config.community_report_table))
    text_unit_df = pd.read_parquet(config.parquet_path(config.text_unit_table))

    entities = read_indexer_entities(entity_df, community_df, config.community_level)
    relationships = read_indexer_relationships(relationship_df)
    reports = read_indexer_reports(report_df, community_df, config.community_level)
    text_units = read_indexer_text_units(text_unit_df)
    covariates = _load_covariates_if_exists(config)

    description_embedding_store = _build_description_embedding_store(config)

    return LocalSearchResources(
        entities=entities,
        relationships=relationships,
        reports=reports,
        text_units=text_units,
        covariates=covariates,
        description_embedding_store=description_embedding_store,
        entity_df=entity_df,
        relationship_df=relationship_df,
        report_df=report_df,
        text_unit_df=text_unit_df,
    )
