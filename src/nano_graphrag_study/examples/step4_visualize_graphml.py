"""Step 4: Visualize GraphML as an interactive HTML graph."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Visualize nano-graphrag GraphML")
    parser.add_argument(
        "--graphml",
        type=Path,
        default=Path("cache/nano_graphrag/graph_chunk_entity_relation.graphml"),
        help="Path to GraphML file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/graph_preview.html"),
        help="Path to output HTML",
    )
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=0,
        help="Limit node count for browser performance (0 means no limit)",
    )
    parser.add_argument(
        "--min-node-size",
        type=float,
        default=14.0,
        help="Minimum node size",
    )
    parser.add_argument(
        "--max-node-size",
        type=float,
        default=48.0,
        help="Maximum node size",
    )
    parser.add_argument(
        "--repulsion",
        type=int,
        default=2200,
        help="Repulsion strength for layout (larger values spread nodes more)",
    )
    parser.add_argument(
        "--spring-length",
        type=int,
        default=110,
        help="Preferred edge length in layout",
    )
    return parser


TYPE_COLOR_MAP = {
    "PERSON": "#ef4444",
    "ORGANIZATION": "#2563eb",
    "GEO": "#059669",
    "EVENT": "#d97706",
    "WORK": "#7c3aed",
    "entity": "#4b5563",
}


def clean_text(value: object) -> str:
    text = str(value) if value is not None else ""
    text = html.unescape(text).strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    return text


def main() -> None:
    args = build_parser().parse_args()

    try:
        import networkx as nx
        from pyvis.network import Network
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency. Install with: uv add networkx pyvis"
        ) from exc

    if not args.graphml.exists():
        raise FileNotFoundError(f"GraphML not found: {args.graphml}")

    graph = nx.read_graphml(args.graphml)
    original_nodes = graph.number_of_nodes()
    original_edges = graph.number_of_edges()

    if args.max_nodes > 0 and original_nodes > args.max_nodes:
        # Keep highly connected nodes first to preserve the core structure.
        ranked = sorted(graph.degree, key=lambda item: item[1], reverse=True)
        keep_nodes = [node_id for node_id, _ in ranked[: args.max_nodes]]
        graph = graph.subgraph(keep_nodes).copy()

    net = Network(height="880px", width="100%", bgcolor="#f8fafc", font_color="#111827")
    net.barnes_hut(
        gravity=-args.repulsion,
        central_gravity=0.28,
        spring_length=args.spring_length,
        spring_strength=0.045,
        damping=0.88,
        overlap=0.0,
    )

    degree_map = dict(graph.degree())
    max_degree = max(degree_map.values()) if degree_map else 1

    for node_id, attrs in graph.nodes(data=True):
        label = clean_text(attrs.get("entity_name") or attrs.get("title") or node_id)
        node_type = clean_text(attrs.get("entity_type") or attrs.get("type") or "entity")
        description = clean_text(attrs.get("description") or "")
        degree = degree_map.get(node_id, 0)
        node_size = args.min_node_size
        if max_degree > 0:
            node_size += (args.max_node_size - args.min_node_size) * (degree / max_degree)

        net.add_node(
            str(node_id),
            label=label,
            title=f"type: {node_type}<br>degree: {degree}<br>{description}",
            group=node_type,
            value=node_size,
            color=TYPE_COLOR_MAP.get(node_type.upper(), "#6b7280"),
        )

    for source, target, attrs in graph.edges(data=True):
        relation = clean_text(attrs.get("relation") or attrs.get("description") or "")
        weight_raw = attrs.get("weight", 1)
        try:
            weight = float(weight_raw)
        except (TypeError, ValueError):
            weight = 1.0

        net.add_edge(str(source), str(target), value=max(weight, 0.1), title=relation)

    net.toggle_physics(True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    net.write_html(str(args.output), open_browser=False)

    print("=== Step4: GraphML Visualization ===")
    print(f"input graphml: {args.graphml}")
    print(f"nodes: {graph.number_of_nodes()} / {original_nodes}")
    print(f"edges: {graph.number_of_edges()} / {original_edges}")
    print(f"output html: {args.output}")
    print(f"open command (macOS): open {args.output}")


if __name__ == "__main__":
    main()
