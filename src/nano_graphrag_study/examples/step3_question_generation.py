"""Step 3: Generate candidate follow-up questions."""

import argparse
from pathlib import Path

from nano_graphrag_study.config import NanoGraphRAGStudyConfig
from nano_graphrag_study.workflow import build_graph, ensure_api_key, generate_followup_questions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate follow-up questions with nano-graphrag")
    parser.add_argument(
        "--history",
        nargs="+",
        default=[
            "Tell me about Agent Mercer",
            "What happens in Dulce military base?",
        ],
        help="question history",
    )
    parser.add_argument("--count", type=int, default=5, help="number of candidate questions")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[3]
    config = NanoGraphRAGStudyConfig.from_project_root(project_root)

    ensure_api_key()
    graph = build_graph(config)

    candidates = generate_followup_questions(
        graph,
        question_history=args.history,
        count=args.count,
    )

    print("=== Step3: Candidate Questions ===")
    print("question_history:")
    for idx, question in enumerate(args.history, start=1):
        print(f"{idx}. {question}")

    print("\n--- candidates ---")
    print(candidates)


if __name__ == "__main__":
    main()
