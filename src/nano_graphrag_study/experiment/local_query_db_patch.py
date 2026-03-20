import os
from typing import Any


def _truncate_text(value: Any, max_len: int = 220) -> str:
    text = str(value)
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _dump_kv_storage(name: str, storage: Any, sample_limit: int = 5) -> None:
    print(f"\\n[DB:{name}] type={storage.__class__.__name__}")
    file_name = getattr(storage, "_file_name", None)
    if file_name:
        print(f"  file={file_name}")

    data = getattr(storage, "_data", None)
    if isinstance(data, dict):
        keys = list(data.keys())
        print(f"  total_keys={len(keys)}")
        for i, key in enumerate(keys[:sample_limit]):
            print(f"  sample_key[{i}]={key}")
            print(f"  sample_value[{i}]={_truncate_text(data.get(key))}")


async def _dump_graph_storage(graph_storage: Any, sample_limit: int = 5) -> None:
    print(f"\\n[DB:knowledge_graph] type={graph_storage.__class__.__name__}")
    graph_file = getattr(graph_storage, "_graphml_xml_file", None)
    if graph_file:
        print(f"  file={graph_file}")

    graph = getattr(graph_storage, "_graph", None)
    if graph is not None:
        print(
            f"  node_count={graph.number_of_nodes()}, edge_count={graph.number_of_edges()}"
        )
        for i, (node_id, node_data) in enumerate(list(graph.nodes(data=True))[:sample_limit]):
            print(f"  node_sample[{i}] id={node_id}")
            print(f"  node_data[{i}]={_truncate_text(node_data)}")
        for i, (src, tgt, edge_data) in enumerate(list(graph.edges(data=True))[:sample_limit]):
            print(f"  edge_sample[{i}] src={src}, tgt={tgt}")
            print(f"  edge_data[{i}]={_truncate_text(edge_data)}")


def _dump_vector_storage(name: str, vector_storage: Any) -> None:
    print(f"\\n[DB:{name}] type={vector_storage.__class__.__name__}")
    client_file = getattr(vector_storage, "_client_file_name", None)
    index_file = getattr(vector_storage, "_index_file_name", None)
    metadata_file = getattr(vector_storage, "_metadata_file_name", None)
    if client_file:
        print(f"  file={client_file}")
    if index_file:
        print(f"  index_file={index_file}")
    if metadata_file:
        print(f"  metadata_file={metadata_file}")

    metadata = getattr(vector_storage, "_metadata", None)
    if isinstance(metadata, dict):
        print(f"  metadata_count={len(metadata)}")
        for i, (k, v) in enumerate(list(metadata.items())[:3]):
            print(f"  metadata_sample[{i}] key={k}, value={_truncate_text(v)}")

    current_elements = getattr(vector_storage, "_current_elements", None)
    if current_elements is not None:
        print(f"  current_elements={current_elements}")


async def _debug_dump_local_query_inputs(
    query: str,
    query_param: Any,
    knowledge_graph_inst: Any,
    entities_vdb: Any,
    community_reports: Any,
    text_chunks_db: Any,
    sample_limit: int,
) -> None:
    print("\\n========== local_query DB debug (wrapper patch) ==========")
    print(f"query={_truncate_text(query, max_len=300)}")
    print(f"top_k={getattr(query_param, 'top_k', None)}")

    await _dump_graph_storage(knowledge_graph_inst, sample_limit=sample_limit)
    if entities_vdb is not None:
        _dump_vector_storage("entities_vdb", entities_vdb)
    if community_reports is not None:
        _dump_kv_storage("community_reports", community_reports, sample_limit=sample_limit)
    if text_chunks_db is not None:
        _dump_kv_storage("text_chunks", text_chunks_db, sample_limit=sample_limit)

    if entities_vdb is not None:
        results = await entities_vdb.query(query, top_k=query_param.top_k)
        print(f"\\n[PIPELINE] entities_vdb.query_count={len(results)}")
        for i, row in enumerate(results[:sample_limit]):
            print(f"  query_result[{i}]={_truncate_text(row)}")

    print("========== /local_query DB debug (wrapper patch) ==========")


def install_local_query_db_debug_patch(sample_limit: int = 5) -> bool:
    """Monkey patch nano_graphrag._op._build_local_query_context from project side."""

    from nano_graphrag import _op as op

    if getattr(op, "_local_query_db_debug_patch_installed", False):
        return False

    original_func = op._build_local_query_context

    async def wrapped_build_local_query_context(
        query,
        knowledge_graph_inst,
        entities_vdb,
        community_reports,
        text_chunks_db,
        query_param,
    ):
        enabled = bool(os.getenv("NANO_GRAPHRAG_DEBUG_LOCAL_QUERY_DB"))
        if enabled:
            try:
                await _debug_dump_local_query_inputs(
                    query=query,
                    query_param=query_param,
                    knowledge_graph_inst=knowledge_graph_inst,
                    entities_vdb=entities_vdb,
                    community_reports=community_reports,
                    text_chunks_db=text_chunks_db,
                    sample_limit=sample_limit,
                )
            except Exception as exc:
                print(f"[local_query_db_debug] pre-dump failed: {exc}")

        return await original_func(
            query,
            knowledge_graph_inst,
            entities_vdb,
            community_reports,
            text_chunks_db,
            query_param,
        )

    op._build_local_query_context = wrapped_build_local_query_context
    op._local_query_db_debug_patch_installed = True
    op._local_query_db_debug_patch_original = original_func
    return True
