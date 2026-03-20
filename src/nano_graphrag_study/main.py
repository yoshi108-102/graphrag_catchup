import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from nano_graphrag import GraphRAG, QueryParam


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="nano-graphrag minimal runner")
    parser.add_argument(
        "--input-path",
        default="input/book.txt",
        help="Path to source text file (project-root relative)",
    )
    parser.add_argument(
        "--working-dir",
        default="cache/nano_graphrag_main",
        help="Path to nano-graphrag working directory (project-root relative)",
    )
    parser.add_argument(
        "--query",
        default="What are the top themes in this story?",
        help="Question to run",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=12000,
        help="Max characters to index on first run. Reduce this if you still hit 429.",
    )
    parser.add_argument(
        "--full-input",
        action="store_true",
        help="Index full input text instead of truncating to --max-chars.",
    )
    parser.add_argument(
        "--reindex",
        action="store_true",
        help="Force re-index even when cache marker exists.",
    )
    parser.add_argument(
        "--debug-local-db",
        action="store_true",
        help="Enable local_query DB debug prints from project-side wrapper patch.",
    )
    return parser.parse_args()


def ensure_api_key() -> None:
    # Explicit path avoids load_dotenv() assertion in some execution modes.
    load_dotenv(".env")
    if os.getenv("OPENAI_API_KEY"):
        return
    legacy = os.getenv("GRAPHRAG_API_KEY")
    if legacy:
        os.environ["OPENAI_API_KEY"] = legacy
        return
    raise RuntimeError("OPENAI_API_KEY is missing (.env or environment)")


def main() -> None:
    args = parse_args()
    ensure_api_key()

    if args.debug_local_db:
        os.environ["NANO_GRAPHRAG_DEBUG_LOCAL_QUERY_DB"] = "1"
        print("local_query DB debug is enabled")

    project_root = Path(__file__).resolve().parents[2]
    input_path = project_root / args.input_path
    working_dir = project_root / args.working_dir
    marker = working_dir / ".indexed"
    working_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    graph_func = GraphRAG(
        working_dir=str(working_dir),
        # Keep to public API knobs; avoid private nano_graphrag._llm imports.
        best_model_max_async=1,
        cheap_model_max_async=1,
        embedding_func_max_async=1,
        embedding_batch_num=2,
        chunk_token_size=1800,
        chunk_overlap_token_size=80,
    )

    should_index = args.reindex or not marker.exists()
    if should_index:
        text = input_path.read_text(encoding="utf-8")
        text_to_insert = text if args.full_input else text[: args.max_chars]
        print(f"indexing started: chars={len(text_to_insert)} (full={args.full_input})")
        try:
            graph_func.insert(text_to_insert)
            marker.write_text("ok\n", encoding="utf-8")
            print("indexing completed")
        except Exception as exc:
            body = getattr(exc, "body", None)
            print("indexing failed")
            print(f"error_type={type(exc).__name__}")
            print(f"error_body={body}")
            raise
    else:
        print("skip indexing: existing cache detected (use --reindex to rebuild)")

    print("\n--- global ---")
    print(graph_func.query(args.query))

    print("\n--- local ---")
    print(graph_func.query(args.query, param=QueryParam(mode="local")))


if __name__ == "__main__":
    main()