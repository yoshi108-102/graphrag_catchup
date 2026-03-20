import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from graphrag.config.load_config import load_config
from graphrag.config.models.graph_rag_config import GraphRagConfig
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.question_gen.local_gen import LocalQuestionGen
from graphrag.query.structured_search.local_search.mixed_context import LocalSearchMixedContext
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag_llm.completion import create_completion
from graphrag_llm.embedding import create_embedding

from .data_loader import LocalSearchResources


def load_graphrag_settings(project_root: Path) -> GraphRagConfig:
    """settings.yaml を読み込み、GraphRAG 設定オブジェクトに変換する。"""

    return load_config(project_root)


@dataclass(slots=True)
class TextModels:
    chat_model: Any
    text_embedder: Any
    tokenizer: Any
    model_params: dict[str, Any]


def build_text_models(
    config: GraphRagConfig,
    *,
    api_key_env: str = "GRAPHRAG_API_KEY",
) -> TextModels:
    """settings.yaml に従って chat model / embedding model / tokenizer を生成する。"""

    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise RuntimeError(f"環境変数 {api_key_env} が設定されていません。")

    completion_settings = config.get_completion_model_config(config.local_search.completion_model_id)
    embedding_settings = config.get_embedding_model_config(config.local_search.embedding_model_id)

    chat_model = create_completion(completion_settings)
    text_embedder = create_embedding(embedding_settings)
    tokenizer = chat_model.tokenizer

    return TextModels(
        chat_model=chat_model,
        text_embedder=text_embedder,
        tokenizer=tokenizer,
        model_params=completion_settings.call_args,
    )


def build_context_builder(resources: LocalSearchResources, text_embedder: Any, tokenizer: Any) -> LocalSearchMixedContext:
    """Local Search のコンテキスト生成器を組み立てる。"""

    return LocalSearchMixedContext(
        community_reports=resources.reports,
        text_units=resources.text_units,
        entities=resources.entities,
        relationships=resources.relationships,
        covariates=resources.covariates,
        entity_text_embeddings=resources.description_embedding_store,
        embedding_vectorstore_key=EntityVectorStoreKey.ID,
        text_embedder=text_embedder,
        tokenizer=tokenizer,
    )


def default_local_context_params() -> dict[str, Any]:
    """公式ノートブックの値をベースにした context builder パラメータ。"""

    return {
        "text_unit_prop": 0.5,
        "community_prop": 0.1,
        "conversation_history_max_turns": 5,
        "conversation_history_user_turns_only": True,
        "top_k_mapped_entities": 10,
        "top_k_relationships": 10,
        "include_entity_rank": True,
        "include_relationship_weight": True,
        "include_community_rank": False,
        "return_candidate_context": False,
        "embedding_vectorstore_key": EntityVectorStoreKey.ID,
        "max_tokens": 12_000,
    }


def default_model_params() -> dict[str, Any]:
    return {
        "max_tokens": 2_000,
        "temperature": 0.0,
    }


def build_local_search_engine(
    *,
    chat_model: Any,
    context_builder: LocalSearchMixedContext,
    tokenizer: Any,
    model_params: dict[str, Any],
    context_builder_params: dict[str, Any],
    response_type: str = "multiple paragraphs",
) -> LocalSearch:
    """Local Search 本体を構築する。"""

    return LocalSearch(
        model=chat_model,
        context_builder=context_builder,
        tokenizer=tokenizer,
        model_params=model_params,
        context_builder_params=context_builder_params,
        response_type=response_type,
    )


def build_question_generator(
    *,
    chat_model: Any,
    context_builder: LocalSearchMixedContext,
    tokenizer: Any,
    model_params: dict[str, Any],
    context_builder_params: dict[str, Any],
) -> LocalQuestionGen:
    """Local Search と同じ文脈で候補質問を生成する。"""

    return LocalQuestionGen(
        model=chat_model,
        context_builder=context_builder,
        tokenizer=tokenizer,
        model_params=model_params,
        context_builder_params=context_builder_params,
    )
