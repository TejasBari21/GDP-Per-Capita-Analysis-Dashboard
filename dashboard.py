# main_dashboard.py
import pandas as pd
import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go

# ---------- Load data ----------
FILE = r"Dataset\gapminder_large_2014_2024.xlsx"   # keep this file next to this script
df = pd.read_excel(FILE)
df["year"] = df["year"].astype(int)
df.columns = [c.strip() for c in df.columns]

years = sorted(df["year"].unique())
countries = sorted(df["country"].unique())
continents = sorted(df["continent"].dropna().unique())

# ---------- App ----------
app = dash.Dash(__name__)
app.title = "INTERACTIVE DASHBOARD"

PAGE_BG = "#0b1220"
CARD_BG = "#121a2b"
TEXT = "#e6edf3"
ACCENT = "#46c2ff"

app.layout = html.Div(
    style={"background": PAGE_BG, "minHeight": "100vh", "padding": "16px"},
    children=[
        html.H1(
            "GDP Per Capita Analysis",
            style={
                "textAlign": "center",
                "color": ACCENT,
                "margin": "8px 0 18px",
                "letterSpacing": "1.5px",
                "fontWeight": "800",
            },
        ),

        # Controls
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "12px", "marginBottom": "14px"},
            children=[
                html.Div(
                    style={"background": CARD_BG, "padding": "12px", "borderRadius": "14px"},
                    children=[
                        html.Label("Year", style={"color": TEXT, "fontWeight": 600}),
                        dcc.Dropdown(
                            id="year_dd",
                            options=[{"label": str(y), "value": y} for y in years],
                            value=max(years),
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    style={"background": CARD_BG, "padding": "12px", "borderRadius": "14px"},
                    children=[
                        html.Label("Countries (multi-select)", style={"color": TEXT, "fontWeight": 600}),
                        dcc.Dropdown(
                            id="country_dd",
                            options=[{"label": c, "value": c} for c in countries],
                            value=[],
                            multi=True,
                            placeholder="All countries",
                        ),
                    ],
                ),
                html.Div(
                    style={"background": CARD_BG, "padding": "12px", "borderRadius": "14px"},
                    children=[
                        html.Label("Continents (multi-select)", style={"color": TEXT, "fontWeight": 600}),
                        dcc.Dropdown(
                            id="continent_dd",
                            options=[{"label": c, "value": c} for c in continents],
                            value=[],
                            multi=True,
                            placeholder="All continents",
                        ),
                    ],
                ),
            ],
        ),

        # KPI row
        html.Div(
            id="kpis",
            style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "12px", "marginBottom": "14px"},
        ),

        # Charts grid
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px"},
            children=[
                html.Div(style={"background": CARD_BG, "padding": "10px", "borderRadius": "14px"},
                         children=[dcc.Graph(id="scatter_gdp_life", config={"displayModeBar": False})]),
                html.Div(style={"background": CARD_BG, "padding": "10px", "borderRadius": "14px"},
                         children=[dcc.Graph(id="bar_pop", config={"displayModeBar": False})]),
                html.Div(style={"background": CARD_BG, "padding": "10px", "borderRadius": "14px"},
                         children=[dcc.Graph(id="pie_gdp", config={"displayModeBar": False})]),
                html.Div(style={"background": CARD_BG, "padding": "10px", "borderRadius": "14px"},
                         children=[dcc.Graph(id="line_country", config={"displayModeBar": False})]),  # Line (replaced density)
                html.Div(style={"background": CARD_BG, "padding": "10px", "borderRadius": "14px"},
                         children=[dcc.Graph(id="box_gdp", config={"displayModeBar": False})]),  # Box (replaced trend)
                html.Div(style={"background": CARD_BG, "padding": "10px", "borderRadius": "14px"},
                         children=[dcc.Graph(id="candle_gdp", config={"displayModeBar": False})]),
            ],
        ),
    ],
)

# ---------- Helpers ----------
def apply_filters(data, year, countries_sel, continents_sel):
    d = data.copy()
    if year is not None:
        d = d[d["year"] == year]
    if countries_sel:
        d = d[d["country"].isin(countries_sel)]
    if continents_sel:
        d = d[d["continent"].isin(continents_sel)]
    return d

# ---------- Callbacks ----------
@callback(
    Output("kpis", "children"),
    Output("scatter_gdp_life", "figure"),
    Output("bar_pop", "figure"),
    Output("pie_gdp", "figure"),
    Output("line_country", "figure"),   # Line (simplified)
    Output("box_gdp", "figure"),        # Box
    Output("candle_gdp", "figure"),
    Input("year_dd", "value"),
    Input("country_dd", "value"),
    Input("continent_dd", "value"),
)
def update_dashboard(year_sel, countries_sel, continents_sel):
    d_year = apply_filters(df, year_sel, countries_sel, continents_sel)

    # KPI cards
    if len(d_year) == 0:
        kpi_items = [html.Div("No data for current selection.",
                              style={"background": CARD_BG, "padding": "16px", "borderRadius": "14px", "color": TEXT})]
    else:
        total_pop = d_year["pop"].sum()
        avg_life = d_year["lifeExp"].mean()
        avg_gdp = d_year["gdpPercap"].mean()
        n_countries = d_year["country"].nunique()

        def kpi(title, value):
            return html.Div(
                style={"background": CARD_BG, "padding": "14px", "borderRadius": "14px"},
                children=[
                    html.Div(title, style={"color": "#9fb3c8", "fontSize": "12px"}),
                    html.Div(value, style={"color": TEXT, "fontSize": "22px", "fontWeight": "700"}),
                ],
            )

        kpi_items = [
            kpi("Countries", f"{n_countries:,}"),
            kpi("Total Population", f"{int(total_pop):,}"),
            kpi("Avg Life Expectancy", f"{avg_life:,.2f}"),
            kpi("Avg GDP per Capita", f"{avg_gdp:,.2f}"),
        ]

    # Scatter
    fig_scatter = px.scatter(
        d_year, x="gdpPercap", y="lifeExp", size="pop", color="continent",
        hover_name="country", title=f"GDP vs Life Expectancy — {year_sel}", template="plotly_dark", size_max=35
    )

    # Bar
    topN = d_year.sort_values("pop", ascending=False).head(15)
    fig_bar = px.bar(
        topN, x="country", y="pop", color="continent",
        title=f"Top 15 Population — {year_sel}", template="plotly_dark"
    )
    fig_bar.update_layout(xaxis_tickangle=-30)

    # Pie GDP
    fig_pie = px.pie(
        d_year, names="country", values="gdpPercap",
        title=f"GDP per Capita Share by Country — {year_sel}", template="plotly_dark"
    )
    fig_pie.update_traces(textinfo="label+percent")

    # --- Line chart (avg GDP per continent for selected year) ---
    d_line = d_year.groupby("continent", as_index=False)["gdpPercap"].mean()
    fig_line = px.line(
        d_line, x="continent", y="gdpPercap", markers=True,
        title=f"Avg GDP per Capita by Continent — {year_sel}", template="plotly_dark"
    )

    # --- Box plot (distribution over 2014–2024) ---
    d_box = apply_filters(df, None, countries_sel, continents_sel)
    fig_box = px.box(
        d_box, x="year", y="gdpPercap", color="continent",
        title="GDP per Capita Distribution (2014–2024)", template="plotly_dark"
    )

    # --- Candlestick (country-wise) ---
    d_candle = apply_filters(df, year_sel, countries_sel, continents_sel).copy()

    if d_candle.empty:
        fig_candle = go.Figure()
        fig_candle.update_layout(title=f"GDP Candlestick Chart — {year_sel}", template="plotly_dark")
    else:
        # Compute OHLC per country for selected year
        d_candle = d_candle.groupby("country").agg(
            open=("gdpPercap", "first"),
            high=("gdpPercap", "max"),
            low=("gdpPercap", "min"),
            close=("gdpPercap", "last"),
        ).reset_index()

        # Sort countries by close for neat display
        d_candle = d_candle.sort_values("close")

        # Assign a unique color per country
        palette = px.colors.qualitative.Plotly + px.colors.qualitative.Set2 + px.colors.qualitative.Dark24
        color_map = {country: palette[i % len(palette)]
                     for i, country in enumerate(d_candle["country"].unique())}

        # Add candlesticks (countries shown on x-axis, legend removed)
        fig_candle = go.Figure()
        for _, row in d_candle.iterrows():
            fig_candle.add_trace(go.Candlestick(
                x=[row["country"]],
                open=[row["open"]],
                high=[row["high"]],
                low=[row["low"]],
                close=[row["close"]],
                increasing_line_color=color_map[row["country"]],
                decreasing_line_color=color_map[row["country"]],
                showlegend=False   # no legend, countries only on x-axis
            ))

        fig_candle.update_layout(
            title=f"GDP Candlestick Chart (Country-wise) — {year_sel}",
            template="plotly_dark",
            xaxis_title="Country",
            yaxis_title="GDP per Capita",
            xaxis_rangeslider_visible=False
        )




    return kpi_items, fig_scatter, fig_bar, fig_pie, fig_line, fig_box, fig_candle


if __name__ == "__main__":
    app.run(debug=True)
