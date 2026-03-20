"""Step 3: Local Search と同じ文脈でフォローアップ質問を生成する。"""

import argparse
import asyncio
from pathlib import Path

from local_search.config import LocalSearchStudyConfig
from local_search.data_loader import load_local_search_resources
from local_search.engine import (
    build_context_builder,
    build_question_generator,
    build_text_models,
    default_local_context_params,
    load_graphrag_settings,
)


async def run(question_history: list[str], question_count: int) -> None:
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

    question_generator = build_question_generator(
        chat_model=models.chat_model,
        context_builder=context_builder,
        tokenizer=models.tokenizer,
        model_params=models.model_params,
        context_builder_params=default_local_context_params(),
    )

    result = await question_generator.agenerate(
        question_history=question_history,
        context_data=None,
        question_count=question_count,
    )

    print("=== Step3: Candidate Questions ===")
    print("question_history:")
    for idx, question in enumerate(question_history, start=1):
        print(f"{idx}. {question}")

    print("\n--- candidates ---")
    print(result.response)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate candidate follow-up questions.")
    parser.add_argument(
        "--history",
        nargs="+",
        default=[
            "Tell me about Agent Mercer",
            "What happens in Dulce military base?",
        ],
        help="過去質問の履歴（スペース区切りで複数指定）",
    )
    parser.add_argument("--count", type=int, default=5, help="生成する質問数")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(run(question_history=args.history, question_count=args.count))


if __name__ == "__main__":
    main()
