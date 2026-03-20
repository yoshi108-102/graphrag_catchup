"""Step 2: Run local search with nano-graphrag and inspect context."""

import argparse
from pathlib import Path

from nano_graphrag_study.config import NanoGraphRAGStudyConfig
from nano_graphrag_study.workflow import build_graph, ensure_api_key, run_query


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run nano-graphrag local search")
    parser.add_argument("--query", default="Tell me about Agent Mercer", help="search query")
    parser.add_argument(
        "--response-type",
        default="Multiple Paragraphs",
        help="response style instruction",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[3]
    config = NanoGraphRAGStudyConfig.from_project_root(project_root)

    ensure_api_key()
    graph = build_graph(config)

    answer = run_query(
        graph,
        args.query,
        mode="local",
        response_type=args.response_type,
    )
    local_context = run_query(
        graph,
        args.query,
        mode="local",
        only_need_context=True,
    )

    print("=== Step2: Local Search ===")
    print(f"query: {args.query}")
    print("\n--- answer ---")
    print(answer)
    print("\n--- retrieved context (raw) ---")
    print(local_context)


if __name__ == "__main__":
    main()
