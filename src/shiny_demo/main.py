import io
from collections.abc import Generator

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route

# --- デモ用データ ------------------------------------------------------------
rng = np.random.default_rng(42)
df0 = pd.DataFrame(
    {
        "lifeExp": rng.normal(72, 10, 1_000).round(1),
        "gdpPercap": rng.lognormal(10, 1, 1_000).round(0),
        "pop": rng.integers(100_000, 100_000_000, 1_000, dtype=np.int64),
        "continent": rng.choice(["Africa", "Americas", "Asia", "Europe", "Oceania"], 1_000),
    }
)

# --- UI ---------------------------------------------------------------------
app_ui = ui.page_navbar(
    ui.nav_panel(
        "Histogram",
        ui.layout_sidebar(
            ui.sidebar(  # ← panel_sidebar → sidebar
                ui.input_slider("bins", "Bins", 5, 50, 20),
                ui.input_selectize(
                    "col",
                    "Column",
                    ["lifeExp", "gdpPercap", "pop"],
                    selected="lifeExp",
                ),
            ),
            ui.output_plot("hist"),  # ← panel_main 削除
        ),
    ),
    ui.nav_panel(
        "Table",
        ui.input_select(
            "continent",
            "Filter by continent",
            ["All", *sorted(df0.continent.unique())],
            selected="All",
        ),
        ui.output_data_frame("tbl"),
    ),
    ui.nav_panel(
        "Upload / Download",
        ui.input_file("file", "Upload a CSV"),
        ui.output_data_frame("preview"),
        ui.download_button("dl", "Download filtered CSV"),
    ),
    ui.nav_panel("About", ui.markdown("Powered by **Shiny for Python**.")),
    title="PyShiny Demo",
)


# --- Server -----------------------------------------------------------------
def server(input_: Inputs, output: Outputs, _session: Session) -> None:
    # 1. Histogram -----------------------------------------------------------
    @output
    @render.plot
    def hist() -> None:
        data = df0[input_.col()]
        plt.hist(data, bins=input_.bins(), edgecolor="white")
        plt.title(f"{input_.col()} distribution")

    # 2. Filtered table ------------------------------------------------------
    @reactive.Calc
    def filtered() -> pd.DataFrame:
        sel = input_.continent()
        return df0 if sel == "All" else df0[df0.continent == sel]

    @output
    @render.data_frame
    def tbl() -> pd.DataFrame:
        return filtered()

    # 3. Upload preview ------------------------------------------------------
    @reactive.Calc
    def uploaded_df() -> pd.DataFrame | None:
        files = input_.file()
        if not files:
            return None
        return pd.read_csv(files[0]["datapath"])

    @output
    @render.data_frame
    def preview() -> pd.DataFrame:
        df = uploaded_df()
        return df if df is not None else pd.DataFrame()

    # 4. Download ------------------------------------------------------------
    @output
    @render.download(filename="filtered.csv")
    def dl() -> Generator[str]:
        buf = io.StringIO()
        filtered().to_csv(buf, index=False)
        yield buf.getvalue()


shiny_app = App(app_ui, server)


def ping(_: Request) -> PlainTextResponse:
    return PlainTextResponse("ok")


routes = [
    Route("/healthz", ping, methods=["GET"]),
    Mount("/", shiny_app),
]

app = Starlette(routes=routes)
