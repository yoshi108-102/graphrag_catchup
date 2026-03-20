"""Step 2: Local Search を実行し、回答と使用コンテキストを確認する。"""

import argparse
import asyncio
from pathlib import Path

from local_search.config import LocalSearchStudyConfig
from local_search.data_loader import load_local_search_resources
from local_search.engine import (
    build_context_builder,
    build_local_search_engine,
    build_text_models,
    default_local_context_params,
    load_graphrag_settings,
)


async def run(query: str, response_type: str) -> None:
    project_root = Path(__file__).resolve().parents[3]
    config = LocalSearchStudyConfig.from_project_root(project_root)
    graphrag_config = load_graphrag_settings(project_root)

    resources = load_local_search_resources(config)
    models = build_text_models(graphrag_config)

    context_builder = build_context_builder(
        resources=resources,
        text_embedder=models.text_embedder,
        tokenizer=models.tokenizer,
    )

    search_engine = build_local_search_engine(
        chat_model=models.chat_model,
        context_builder=context_builder,
        tokenizer=models.tokenizer,
        model_params=models.model_params,
        context_builder_params=default_local_context_params(),
        response_type=response_type,
    )

    result = await search_engine.search(query)

    print("=== Step2: Local Search Result ===")
    print(f"query: {query}")
    print("\n--- response ---")
    print(result.response)

    # ノートブックの「context inspection」に対応。
    print("\n--- context: entities ---")
    print(result.context_data["entities"].head(5).to_string())

    print("\n--- context: relationships ---")
    print(result.context_data["relationships"].head(5).to_string())

    if "reports" in result.context_data:
        print("\n--- context: reports ---")
        print(result.context_data["reports"].head(5).to_string())

    if "claims" in result.context_data:
        print("\n--- context: claims ---")
        print(result.context_data["claims"].head(5).to_string())

    print("\n--- context: sources ---")
    print(result.context_data["sources"].head(5).to_string())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run GraphRAG Local Search example.")
    parser.add_argument("--query", default="Tell me about Agent Mercer", help="検索クエリ")
    parser.add_argument(
        "--response-type",
        default="multiple paragraphs",
        help="応答形式の指示。例: single paragraph / prioritized list",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(run(query=args.query, response_type=args.response_type))


if __name__ == "__main__":
    main()
