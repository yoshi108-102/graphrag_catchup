# graph-rag-study

Microsoft GraphRAG の学習コードを整理しつつ、読みやすい `nano-graphrag` ベースへ移行したリポジトリです。

## 現在の構成

- 旧実装: `src/archive/local_search`
- 新実装: `src/nano_graphrag_study`

## nano-graphrag 学習ステップ

1. Step1: インデックス作成

```bash
PYTHONPATH=src .venv/bin/python -m nano_graphrag_study.examples.step1_build_index
```

2. Step2: Local 検索

```bash
PYTHONPATH=src .venv/bin/python -m nano_graphrag_study.examples.step2_run_local_search \
	--query "Tell me about Agent Mercer"
```

3. Step3: フォローアップ質問生成

```bash
PYTHONPATH=src .venv/bin/python -m nano_graphrag_study.examples.step3_question_generation \
	--history "Tell me about Agent Mercer" "What happens in Dulce military base?" \
	--count 5
```

4. Step4: GraphML 可視化 (HTML)

```bash
uv add networkx pyvis
PYTHONPATH=src .venv/bin/python -m nano_graphrag_study.examples.step4_visualize_graphml
open output/graph_preview.html
```

このスクリプトは `dickens/graph_chunk_entity_relation.graphml` 規模を想定したデフォルトに調整済みです。
必要なときだけパラメータを上書きしてください。

上書き例:

```bash
PYTHONPATH=src .venv/bin/python -m nano_graphrag_study.examples.step4_visualize_graphml \
	--graphml dickens/graph_chunk_entity_relation.graphml \
	--min-node-size 14 \
	--max-node-size 48 \
	--repulsion 2600 \
	--spring-length 120
```

## 必要な環境変数

- `OPENAI_API_KEY`
- 互換のため、`GRAPHRAG_API_KEY` が設定されていれば自動的に再利用します。
