"""
Streamlit sample : generic CSV explorer / BI dashboard
"""

import io

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from pandas import DataFrame


def setup_page() -> None:
    """アプリのページ設定を行う"""
    st.set_page_config("CSV Explorer", layout="wide", page_icon="📊")
    st.title("📊 CSV Explorer")


@st.cache_data(show_spinner="CSV 解析中…")
def load_data(file: io.BytesIO) -> DataFrame:
    """CSVファイルを読み込みDataFrameを返す

    Args:
        file: CSVファイルのバイトストリーム

    Returns:
        読み込んだデータのDataFrame
    """
    return pd.read_csv(file)


def create_sample_data() -> io.BytesIO:
    """サンプルデータを作成して返す

    Returns:
        サンプルデータのCSVバイトストリーム
    """
    sample_df = pd.DataFrame(
        {
            "date": pd.date_range("2025-01-01", periods=50, freq="D"),
            "category": ["A", "B", "C", "D"] * 13 + ["A", "B"],
            "value": np.random.default_rng().integers(0, 100, 50),
        }
    )
    return io.BytesIO(sample_df.to_csv(index=False).encode())


def upload_csv() -> io.BytesIO | None:
    """CSVファイルのアップロード処理

    Returns:
        アップロードされたCSVファイル、なければNone
    """
    csv_file = st.file_uploader("CSV ファイルを選択してください", type="csv")
    if not csv_file:
        st.info("👉 左上のボタンでサンプル CSV を読み込みます")
        if st.button("サンプルデータをロード"):
            return create_sample_data()
    return csv_file


def apply_filters(df: DataFrame) -> DataFrame:
    """サイドバーフィルターを適用

    Args:
        df: 元のDataFrame

    Returns:
        フィルター適用後のDataFrame
    """
    st.sidebar.header("🔍 フィルター")
    sel = pd.Series(data=True, index=df.index)

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            min_v, max_v = st.sidebar.slider(
                f"{col} (range)",
                float(df[col].min()),
                float(df[col].max()),
                (float(df[col].min()), float(df[col].max())),
            )
            sel &= df[col].between(min_v, max_v)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            start, end = st.sidebar.date_input(f"{col} (期間)", (df[col].min(), df[col].max()))  # type: ignore[misc]
            sel &= df[col].between(pd.to_datetime(start), pd.to_datetime(end))
        else:
            opts: list[str] = st.sidebar.multiselect(f"{col} (値選択)", df[col].unique().tolist())
            if opts:
                sel &= df[col].isin(opts)

    return df[sel]


def display_kpi_and_charts(df: DataFrame) -> None:
    """KPIとチャートを表示

    Args:
        df: 表示対象のDataFrame
    """
    numeric_cols = df.select_dtypes("number").columns.tolist()
    if not numeric_cols:
        return

    # KPI表示
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("行数", len(df))
    kpi2.metric("数値列", len(numeric_cols))
    kpi3.metric("合計", df[numeric_cols[0]].sum())

    # チャート表示
    chart_col = st.selectbox("チャート対象列", numeric_cols)
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{chart_col}:Q", bin=alt.Bin(maxbins=30)),
            y="count()",
        )
        .properties(height=300)
    )

    st.altair_chart(chart, use_container_width=True)


def enable_download(df: DataFrame) -> None:
    """フィルター後のデータをダウンロード可能にする

    Args:
        df: ダウンロード対象のDataFrame
    """
    csv = df.to_csv(index=False).encode()
    st.download_button("⬇️ フィルタ後 CSV をダウンロード", csv, "filtered.csv", "text/csv")


def main() -> None:
    """メイン処理"""
    setup_page()

    # CSVファイルの読み込み
    csv_file = upload_csv()
    if not csv_file:
        return

    # データの読み込みと表示
    raw_df = load_data(csv_file)
    st.success(f"✅ 読込完了 - {len(raw_df):,} rows * {len(raw_df.columns)} cols")
    st.dataframe(raw_df.head())

    # フィルター適用
    filtered_df = apply_filters(raw_df)
    st.subheader(f"📈 フィルタ後 {len(filtered_df):,} rows")
    st.data_editor(filtered_df, use_container_width=True)

    # KPIとチャートの表示
    display_kpi_and_charts(filtered_df)

    # ダウンロード機能
    enable_download(filtered_df)


if __name__ == "__main__":
    main()
