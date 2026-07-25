"""
Streamlit sample : Markdown ノートを ChatGPT で要約 & キーワード抽出
"""

import json

import streamlit as st
import tiktoken
from openai import OpenAI
from pydantic import BaseModel

from src.libs.settings import settings

# ────────────────────────────────
#   ページ設定
# ────────────────────────────────
st.set_page_config(page_title="Markdown Summarizer", page_icon="📝", layout="wide")
st.title("📝 Markdown Summarizer & Keyword Extractor")

# ────────────────────────────────
#   API キー確認
# ────────────────────────────────
if not settings.openai_api_key:
    st.error("OpenAI API キーが設定されていません。.env ファイルに OPENAI_API_KEY を設定してください。")
    st.stop()

client = OpenAI(api_key=settings.openai_api_key)

# ────────────────────────────────
#   入力: ファイル or テキストエリア
# ────────────────────────────────
uploaded = st.file_uploader(
    "Markdown (.md / .txt) をアップロードするか、下のテキストエリアに直接貼り付けてください",
    type=["md", "txt"],
)

default_md = """\
# 🌐 2025 Q2 LLM Megareport
*“技術・ビジネス・政策を 360° 俯瞰する 40 K‑word ロングリード”*

---

## 📜 目次
1. [フロンティアモデル（クローズド）](#ch1)
2. [オープンソース & 準オープンモデル](#ch2)
3. [コア技術トレンド詳細](#ch3)
4. [インフラ & ハードウェア](#ch4)
5. [規制・ガバナンス](#ch5)
6. [ベンチマーク & 評価](#ch6)
7. [商用エコシステム](#ch7)
8. [研究フロンティア & 未解決課題](#ch8)
9. [12 か月予測と戦略指針](#ch9)
10. [Appendix A — 用語集 & 略語](#appA)

---

<a name="ch1"></a>
## 1️⃣ フロンティアモデル（クローズド）

> **要点** ― 3 社 6 系統が “性能×コスト×モーダル” の三角形で競合。GPT‑4o と Claude 3 Opus が長文脈・マルチモーダルで先行し、Gemini 2.5 が**推論予算 API**でコスト制御に革新を起こした。

### 1‑A. **OpenAI**
| モデル | 構造 | 主な機能 | API 価格* |
| --- | --- | --- | --- |
| **GPT‑4o** | Vision+Audio+Text 統合 Transformer | 2× 速 / ½ 価格 / 5× Rate‑Limit  [oai_citation_attribution:0‡OpenAI](https://openai.com/index/hello-gpt-4o/?utm_source=chatgpt.com) | \\$5/M **out**, \\$1/M **in** |
| **o3** | 8 T 総パラの Gradient‑MoE | 専門家比率 3 % で GPT‑4 同等  [oai_citation_attribution:1‡OpenAI](https://openai.com/index/introducing-4o-image-generation/?utm_source=chatgpt.com) | \\$0.8/M in |
| **o4‑mini** | 46 B 密結合 + LoRA | GPT‑3.5→4.5 の隙間  [oai_citation_attribution:2‡OpenAI Help Center](https://help.openai.com/en/articles/7102672-how-can-i-access-gpt-4-gpt-4o-and-gpt-4o-mini?utm_source=chatgpt.com) | \\$0.5/M in |

> 💡 **API スニペット**
> ```python
> client.chat.completions.create(
>   model="gpt-4o",
>   messages=[{"role":"system","content":"You are a RAG agent."}, ...],
>   tools=[{"type":"retrieval"}],
>   max_tokens=4096, temperature=0.3
> )
> ```

#### *内部実装*
- **Router**: Top‑k=2 softmax ルーティング
- **KV‑Cache**: Bfloat16→FP4 圧縮 (Blackwell互換)
- **Speculative Decoding**: Fast‑Draft 4‑step→Verifier

---

### 1‑B. **Anthropic Claude 3**
> 📝 *“Stretch‑RoPE” により **1 M tokens** コンテキスト長を実用化*

| Variant | 文脈長 | 定評ベンチ | 価格 (in/out) | 用途例 |
| --- | --- | --- | --- | --- |
| Haiku | 200 K | GSM8K 82 % | \\$0.25 / \\$1 | FAQ Bot |
| Sonnet | 400 K | MMLU 87 % | \\$1.5 / \\$5 | RAG+分析 |
| **Opus** | **1 M** | Codeforces 1900+ | \\$6 / \\$15 | 複合レポート生成 |

> > **Blockquote: Opus 開発者談**
> > *“Windowed Compression によって、128 K 超の KV‑Cache を GPU HBM 64 GB 内に収めた。”*

---

### 1‑C. **Google Gemini 2.5 / 2.5 Flash**
- **Thinking‑Budget** パラメータで `steps`×`breadth` を制御し、呼び出し側で *品質‑遅延‑コスト* を数式的に最適化。
- Flash 版は探索幅を 1/2 に縮小し **コスト‑68 %**／*品質‑35 %*

```mermaid
flowchart LR
  User -->|Budget=0| Gemini{Search}
  Gemini -->|Docs| RAG
  RAG -->|Budget=5| Gemini
  Gemini --> Answer
```

---

<a name="ch2"></a>
## 2️⃣ オープンソース & 準オープンモデル

### 2‑A. **Meta Llama 4**
Meta は *Scout 17 B / Maverick 140 B / Behemoth 2 T* を発表。Scout & Maverick は **MoE + マルチモーダル** の OSS、Behemoth は教師モデル  [oai_citation_attribution:3‡Log in or sign up to view](https://about.fb.com/ja/news/2025/04/llama-4-multimodal-intelligence/?utm_source=chatgpt.com)。

| Variant | Active Params | Experts | Max Ctx | DL‑Arena ELO |
| --- | --- | --- | --- | --- |
| Scout | 17 B | 16 | 10 M | 1298 |
| Maverick | 17 B | 128 | 10 M | 1417 |
| Behemoth | 288 B | 16 | **訓練中** | — |

> ✅ **Hugging Face** で即 DL → `pip install llama4-scout`

---

### 2‑B. **DeepSeek‑R1 671 B**
MIT ライセンスで ①完全オープン、②MoTE=“Mixture‑of‑Top‑Experts”。活性パラ 44 B で GPT‑4‑class。【価格】\\$0.14/M in  [oai_citation_attribution:4‡Your First API Call | DeepSeek API Docs](https://api-docs.deepseek.com/news/news250120?utm_source=chatgpt.com)

> ```bash
> accelerate launch deepseek_inference.py \
>   --model deepseek-reasoner --dtype int4_bcq
> ```

### 2‑C. その他 OSS
- **Mixtral 8×22 B** ‑ 7‑bit W/A 量子化で M2 上 25 tok s⁻¹  [oai_citation_attribution:5‡OpenAI Community](https://community.openai.com/t/api-for-image-generation-for-gpt-4o-model/1153132?utm_source=chatgpt.com)
- **Phi‑3‑mini‑128K** ‑ 3.8 B でも GPT‑3.5 同等（Microsoft）
- **Qwen‑2** ‑ gQA + 千億コーパス、中国語タスク首位

---

<a name="ch3"></a>
## 3️⃣ コア技術トレンド詳細

### 3‑1. **Mixture‑of‑Experts (MoE)**

| Router | 方式 | スループット | Comm. Overhead |
| --- | --- | --- | --- |
| Switch‑MLP | token‑wise K=1 | ★★★★☆ | ▲ gRPC 多発 |
| Gradient Router (o3) | K=2 + Clip | ★★★★★ | ● 低 |
| **Hierarchical Router** (Meta) | 2‑level | ★★★★★ | ◎ ‑48 % band use  [oai_citation_attribution:6‡Log in or sign up to view](https://about.fb.com/ja/news/2025/04/llama-4-multimodal-intelligence/?utm_source=chatgpt.com) |

> **数式**
> $$\text{MoE\\_Loss} = \\mathcal{L}_{\text{task}} + \\lambda \\sum_g (\text{load}_g - \bar{\text{load}})^2$$
> *λ*=0.01 で load‑balancing 損失を勾配の 2 % 以下に抑制。

---

### 3‑2. **長文脈技術**
1. **Stretch‑RoPE**: スケーリング係数 *α* をトークン位置で可変に。(Claude)
2. **Dynamic‑NTK**: `exp(i·pos·θ/NTK(pos))` の NTK を対数縮小。
3. **Windowed Compression**: 古い KV‑Cache を 8‑bit → 4‑bit 要約後 1/8 サイズに収納。

```ascii
CTX 0-----128K====256K==...==1M
       ↑RoPE直  ↑NTK   ↑WinCompr
```

---

### 3‑3. **量子化 & 省メモリ**
- **BCQ (Block‑Clustered Quantization)**: W4A4 で < 1 % 損失  [oai_citation_attribution:7‡OpenAI Cookbook](https://cookbook.openai.com/examples/gpt4-1_prompting_guide?utm_source=chatgpt.com)
- **FP4**: Blackwell TensorCore 対応。
- **gQA**: KV を Head=1 に集約、長文脈で 1.7× 速。

> **実験** (Llama 4 Maverick)
> | dtype | 32 K ctx tok s⁻¹ | perplexity |
> |---|---|---|
> | FP16 | 560 | 5.7 |
> | **FP4** | **1320** | 5.9 |

---

<a name="ch4"></a>
## 4️⃣ インフラ & ハードウェア

### 4‑1. GPU スペック比較

| GPU | FP16 TFLOPS | FP4 | HBM | Max Ctx† | Ref |
| --- | --- | --- | --- | --- | --- |
| **NVIDIA B200** | 145 | ✅ | 192 GB | 256 K |  [oai_citation_attribution:8‡NVIDIA](https://resources.nvidia.com/en-us-blackwell-architecture/blackwell-architecture-technical-brief?utm_source=chatgpt.com) |
| **Grace‑Blackwell GB200 NVL72** | 1.44 PF | ✅ | 8 TB (NVSwitch) | 4 M | 同上 |
| AMD MI300X | 130 | ❌ | 192 GB | 128 K | — |
| Intel Falcon Shores | 85 | ❌ | 128 GB | 64 K | (roadmap) |

†推論時 vLLM + chunked‑prefill 前提

> > ⚙️ **運用 Tip**
> > “GB200 NVL72 × vLLM 0.4” で GPT‑4‑class を 1 K tok s⁻¹ / node、電力 4.2 kW【試算】。

---

<a name="ch5"></a>
## 5️⃣ 規制・ガバナンス

### 5‑A. **EU AI Act (Reg 2024/1689)**
- **一般目的 AI (GPAI)** プロバイダは
  1. トレデータ要約公開
  2. 技術文書提出
  3. 「AI Office」登録
  4. リスク管理体系の公表  [oai_citation_attribution:9‡EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/LSU/?uri=oj%3AL_202401689&utm_source=chatgpt.com)

> **タイムライン**
> - 2025‑08 : トランスペアレンシー条項発効
> - 2026‑02 : GPAI 評価基準を EU 標準化機構が制定

### 5‑B. **米国 EO 14110 → 2025 EO 改訂**
- 2023 EO 14110（Biden）… 安全性・レッドチーム義務  [oai_citation_attribution:10‡The White House](https://www.whitehouse.gov/briefing-room/statements-releases/2023/10/30/fact-sheet-president-biden-issues-executive-order-on-safe-secure-and-trustworthy-artificial-intelligence/?goal=0_7f08f27dbf-f00f5eef50-54576006&utm_source=chatgpt.com)
- 2025 EO（Trump）… 報告義務緩和・イノベーション促進  [oai_citation_attribution:11‡The White House](https://www.whitehouse.gov/fact-sheets/2025/01/fact-sheet-president-donald-j-trump-takes-action-to-enhance-americas-ai-leadership/?utm_source=chatgpt.com)

| 事項 | 2023 EO | 2025 EO |
| --- | :white_check_mark: | :x: |
| レッドチーム結果 DoC 提出 | ✅ | ❌ |
| Frontier 訓練計算量報告 | ✅ | ❌ |
| **サイバー安全監査** | ✅ | ✅ |

---

<a name="ch6"></a>
## 6️⃣ ベンチマーク & 評価

### 6‑A. **HELM 2.0**
25 能力 × 30 シナリオのスコアマトリクス。モデルを “Spider” レーダーチャートで表示  [oai_citation_attribution:12‡OpenAI Community](https://community.openai.com/t/the-official-4o-and-dall-e-image-megathread/1230134?utm_source=chatgpt.com)

### 6‑B. **Chatbot Arena (v2)**
- 4 月版で GPT‑4o が 1 位 (ELO 1468)、Llama‑4 Maverick が 2 位 (ELO 1417)。
- Llama 側が “蒸留≒問題リーク” 疑義→ **評価再設計** 始動。

```python
# vLLM-based automated Arena evaluator
from vllm import LLM, SamplingParams
llm = LLM("scout-llama4-int4")
sp = SamplingParams(temperature=0, max_tokens=1)
score = compare_pair(llm, reference_model="gpt-4o", dataset="arena-hard")
```

---

<a name="ch7"></a>
## 7️⃣ 商用エコシステム

### 7‑1. MaaS 価格表 (2025‑04)

| Provider | Flagship | \\$ / M in | \\$ / M out | 備考 |
| --- | --- | --- | --- | --- |
| OpenAI | GPT‑4o | **1.0** | **5.0** |
| Anthropic | Claude Opus | 6.0 | 15.0 |
| Google | Gemini 2.5 | 0.6 | 3.0 |
| DeepSeek | R1 | 0.14 | 2.19 |
| Mistral | Mixtral 8x22B | 0.2 | 1.5 |

> **アプライアンス潮流**
> - Lambda Hyperplane (8×B200)
> - Groq Rack (Gaudi3 ASIC)
> - Cerebras CS‑3 RAG‑Ready

---

<a name="ch8"></a>
## 8️⃣ 研究フロンティア & 未解決課題

| 課題 | 進展 | 未踏ポイント |
| --- | --- | --- |
| ハルシネーション | Agentic‑RAG で ▲50 % | **Source‑Tight Loss** 未普及 |
| 自己検証 | GPT‑o3 内包 | コスト ↔ 低遅延 |
| ASL‑3 安全水準 | Opus v2 β | 意図‑隠蔽検知 |
| 合成データ | GPT‑4o Self‑Play | 分布シフト管理 |

> **タスクリスト**
> - [ ] RoPE+NTK のスケールロジック実装
> - [ ] BCQ カーネルを Triton で拡張
> - [ ] EU AI Act リスク報告テンプレ作成

---

<a name="ch9"></a>
## 9️⃣ 12 か月予測と戦略指針

1. **Edge‑MoE** PC (20‑70 B) → ローカル AI スタンダード
2. **ASL‑3**: 行動隠蔽検知器実装 → API 付加価値
3. **IDE × Agentic‑RAG** → コード改修まで自動
4. **合成＋実データ ハイブリッド学習** 競争
5. **リージョン分割 API**：EU‑Only エンドポイント義務化

> > “**計画→デザイン→実装** の全フェーズで *Risk & Compliance by Design* が必須になる”

---

<a name="appA"></a>
## Appendix A — 用語集 & 略語

| 略語 | 意味 |
| --- | --- |
| **MoE** | Mixture‑of‑Experts |
| **gQA** | Grouped Query Attention |
| **BCQ** | Block‑Clustered Quantization |
| **RAG** | Retrieval‑Augmented Generation |
| **ASL** | Anthropic Safety Level |
| **GPAI** | General‑Purpose AI (EU AI Act) |

---

> © 2025 LLM Megareport. 引用・転載時は本ドキュメント URL を併記してください。
> *Prepared for advanced practitioners & policy designers.*

---

[^*]: API 価格は 2025‑04‑15 時点公式発表に基づく。

<!-- ⬆︎ ページ上部へ戻る → `[Ctrl]+[Home]` -->
"""

text_input = st.text_area(
    "▼ 直接入力する場合はこちら",
    default_md if uploaded is None else "",
    height=250,
)

# 再実行ボタン
rerun_button = st.button("🔄 テキストを変更して再実行", type="primary")

if uploaded:
    text_md = uploaded.read().decode("utf-8")
elif text_input.strip():
    text_md = text_input
else:
    st.info("Markdown を入力／アップロードすると結果が表示されます。")
    st.stop()


# ────────────────────────────────
#   structured output 用モデル
# ────────────────────────────────
class SummaryResponse(BaseModel):
    summary: str
    keywords: list[str]


# ────────────────────────────────
#   OpenAI へ問い合わせ
# ────────────────────────────────
@st.cache_data(show_spinner="ChatGPT が要約中です…")
def call_openai(md: str) -> SummaryResponse:
    """
    OpenAI API を使用して Markdown テキストを要約・キーワード抽出する。
    Structured output を用いるため文字列パースは不要。
    """
    # 入力トークン数の軽い検査（極端な長文のときに警告したい場合などに使用）
    enc = tiktoken.get_encoding("cl100k_base")
    _ = len(enc.encode(md))

    system_msg = (
        "あなたは優秀な日本語編集者です。\n"
        "ユーザーから渡される Markdown ノートを 300 文字以内で要約し、主要キーワードを最大 10 語抽出して下さい。\n"
        '出力は JSON で {"summary": ..., "keywords": [...]} 形式とします。'
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": md},
        ],
        max_tokens=600,
    )

    # content は必ず JSON 文字列で返る
    data = json.loads(response.choices[0].message.content or "{}")
    return SummaryResponse(**data)


# ボタンが押されたらキャッシュをクリア
if rerun_button:
    call_openai.clear()
    st.success("キャッシュをクリアしました。新しい要約を生成します。")

with st.spinner("OpenAI へ問い合わせ中…"):
    result = call_openai(text_md)

# ────────────────────────────────
#   結果表示
# ────────────────────────────────
st.subheader("📄 入力 Markdown（抜粋）")
MAX_LEN = 2000
st.code(text_md[:MAX_LEN] + (" …" if len(text_md) > MAX_LEN else ""), language="markdown")

st.subheader("📝 要約")
st.write(result.summary)

st.subheader("🔑 キーワード")
st.write(", ".join(result.keywords))

st.download_button("🔽 要約をテキストで保存", result.summary, file_name="summary.txt")
