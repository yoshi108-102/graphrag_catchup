# nano-graphrag Learning Guide

`src/nano_graphrag_study` is a step-by-step rewrite of the old `local_search` study flow.

## Steps

1. `step1_build_index.py`
- Load `input/book.txt`
- Build index into `cache/nano_graphrag`

2. `step2_run_local_search.py`
- Run local query with `QueryParam(mode="local")`
- Optionally inspect only retrieved context

3. `step3_question_generation.py`
- Create follow-up questions from question history and local context

4. `step4_visualize_graphml.py`
- Read `graph_chunk_entity_relation.graphml`
- Generate interactive HTML graph into `output/graph_preview.html`

## Run

```bash
PYTHONPATH=src .venv/bin/python -m nano_graphrag_study.examples.step1_build_index
PYTHONPATH=src .venv/bin/python -m nano_graphrag_study.examples.step2_run_local_search --query "Tell me about Agent Mercer"
PYTHONPATH=src .venv/bin/python -m nano_graphrag_study.examples.step3_question_generation --history "Tell me about Agent Mercer" "What happens in Dulce military base?" --count 5
uv add networkx pyvis
PYTHONPATH=src .venv/bin/python -m nano_graphrag_study.examples.step4_visualize_graphml
open output/graph_preview.html
```

Defaults are already tuned for medium-sized graphs (around a few hundred nodes).
Use overrides only when needed:

```bash
PYTHONPATH=src .venv/bin/python -m nano_graphrag_study.examples.step4_visualize_graphml \
	--graphml dickens/graph_chunk_entity_relation.graphml \
	--min-node-size 14 \
	--max-node-size 48 \
	--repulsion 2600 \
	--spring-length 120
```

## Environment

Set `OPENAI_API_KEY`.
For migration convenience, these scripts automatically reuse `GRAPHRAG_API_KEY` if set.
