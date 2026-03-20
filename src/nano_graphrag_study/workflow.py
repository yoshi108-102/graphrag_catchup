import os
from pathlib import Path

from nano_graphrag import GraphRAG, QueryParam

from .config import NanoGraphRAGStudyConfig
from .experiment import install_local_query_db_debug_patch


def ensure_api_key() -> str:
    """Ensure nano-graphrag can read an API key from environment."""

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        return openai_key

    # Reuse existing GraphRAG env var when migrating.
    legacy_key = os.environ.get("GRAPHRAG_API_KEY")
    if legacy_key:
        os.environ["OPENAI_API_KEY"] = legacy_key
        return legacy_key

    raise RuntimeError(
        "OPENAI_API_KEY is not set. Set OPENAI_API_KEY (or GRAPHRAG_API_KEY for fallback)."
    )


def load_input_text(config: NanoGraphRAGStudyConfig) -> str:
    if not config.input_text_path.exists():
        raise FileNotFoundError(f"Input text not found: {config.input_text_path}")

    return config.input_text_path.read_text(encoding="utf-8")


def build_graph(config: NanoGraphRAGStudyConfig) -> GraphRAG:
    config.working_dir.mkdir(parents=True, exist_ok=True)
    # Project-side monkey patch: never edit site-packages for debugging hooks.
    install_local_query_db_debug_patch()
    return GraphRAG(working_dir=str(config.working_dir))


def run_query(
    graph: GraphRAG,
    query: str,
    *,
    mode: str = "local",
    response_type: str = "Multiple Paragraphs",
    only_need_context: bool = False,
) -> str:
    return graph.query(
        query,
        param=QueryParam(
            mode=mode,
            response_type=response_type,
            only_need_context=only_need_context,
        ),
    )


def generate_followup_questions(
    graph: GraphRAG,
    question_history: list[str],
    *,
    count: int,
) -> str:
    """Generate candidate follow-up questions from local context."""

    latest_query = question_history[-1] if question_history else "Summarize the key entities."
    local_context = run_query(
        graph,
        latest_query,
        mode="local",
        only_need_context=True,
    )

    history_block = "\n".join(f"{idx}. {q}" for idx, q in enumerate(question_history, start=1))
    prompt = (
        "You are helping with iterative investigation.\n"
        "Given the question history and retrieved context, propose follow-up questions.\n"
        f"Return exactly {count} concise questions as a numbered list.\n\n"
        "Question history:\n"
        f"{history_block}\n\n"
        "Retrieved local context:\n"
        f"{local_context}"
    )

    return run_query(
        graph,
        prompt,
        mode="local",
        response_type=f"Numbered list with exactly {count} short follow-up questions",
    )
