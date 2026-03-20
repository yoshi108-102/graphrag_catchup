"""Step 1: Build nano-graphrag index from input text."""

from pathlib import Path

from nano_graphrag_study.config import NanoGraphRAGStudyConfig
from nano_graphrag_study.workflow import build_graph, ensure_api_key, load_input_text


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    config = NanoGraphRAGStudyConfig.from_project_root(project_root)

    ensure_api_key()
    graph = build_graph(config)
    text = load_input_text(config)

    graph.insert(text)

    print("=== Step1: Build Index ===")
    print(f"input: {config.input_text_path}")
    print(f"working_dir: {config.working_dir}")
    print(f"input chars: {len(text)}")
    print("indexing: completed")


if __name__ == "__main__":
    main()
