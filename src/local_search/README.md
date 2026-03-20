# Local Search 学習ガイド（Notebook -> Python 版）

このディレクトリは、公式ノートブック
`https://microsoft.github.io/graphrag/examples_notebooks/local_search/`
の流れを、**段階的に実行しやすい `.py` 形式**へ分解したものです。

## 目的

- Local Search の実体（データ読み込み -> コンテキスト構築 -> 検索実行）を理解する
- ノートブック依存を減らし、再実行しやすい Python スクリプトとして学ぶ
- 質問生成（Question Generation）まで同じ文脈で体験する

## ディレクトリ構成

- `src/local_search/config.py`
  - パス・テーブル名・community level などの設定を集約
- `src/local_search/data_loader.py`
  - `output/*.parquet` と `output/lancedb` を読み込み、Local Search 用リソースを生成
- `src/local_search/engine.py`
  - `settings.yaml` からモデル設定を読み込み、`LocalSearchMixedContext` 構築、`LocalSearch`/`LocalQuestionGen` 生成
- `src/local_search/examples/step1_load_context.py`
  - Step 1: データ読み込み確認
- `src/local_search/examples/step2_run_local_search.py`
  - Step 2: Local Search 実行と context inspection
- `src/local_search/examples/step3_question_generation.py`
  - Step 3: 候補質問生成

## 事前準備

1. GraphRAG のインデックス出力があること
   - このリポジトリでは `output/` に `entities.parquet` などが存在
2. 環境変数 `GRAPHRAG_API_KEY` を設定すること
3. 依存ライブラリが入っていること
   - `graphrag>=3.0.6`
4. `settings.yaml` の `local_search` / `completion_models` / `embedding_models` が有効であること

## 学習ステップ

### Step 1: 入力データの確認

```bash
PYTHONPATH=src .venv/bin/python -m local_search.examples.step1_load_context
```

見るポイント:
- `entities / relationships / reports / text_units` 件数
- `covariates enabled`（`extract_claims` が無効なら通常 `False`）
- `output/lancedb` の entity description index 接続

### Step 2: Local Search 実行

```bash
PYTHONPATH=src .venv/bin/python -m local_search.examples.step2_run_local_search \
  --query "Tell me about Agent Mercer"
```

見るポイント:
- `result.response`
- `result.context_data["entities"]` など、回答に使われたコンテキスト
- `local_context_params` の値（`engine.py`）を変えたときの挙動差

### Step 3: Question Generation

```bash
PYTHONPATH=src .venv/bin/python -m local_search.examples.step3_question_generation \
  --history "Tell me about Agent Mercer" "What happens in Dulce military base?" \
  --count 5
```

見るポイント:
- 過去質問に基づくフォローアップ候補がどう変化するか
- `--count` を増減したときの質問の粒度

## Notebook 対応表

- Load tables to dataframes -> `data_loader.py`
- Create local search context builder -> `engine.py: build_context_builder`
- Create local search engine -> `engine.py: build_local_search_engine`
- Run local search -> `examples/step2_run_local_search.py`
- Inspect context data -> `examples/step2_run_local_search.py`
- Question generation -> `examples/step3_question_generation.py`

## カスタマイズの入り口

- モデル変更:
  - `settings.yaml` の `completion_models` / `embedding_models` / `local_search` のモデルID
- コンテキストの配分変更:
  - `engine.py` の `default_local_context_params`
- 応答形式変更:
  - `examples/step2_run_local_search.py --response-type`
