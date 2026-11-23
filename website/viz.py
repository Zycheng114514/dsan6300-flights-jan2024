"""Shared data loading and chart builders for the HW4 Quarto site.

All charts read the CSVs in ./data (exported from MySQL by scripts/build_site_data.py),
so the site renders without a database connection.
"""
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

DATA = Path(__file__).parent / "data"
PREFIX = "hw4_cheng_zhiyang_zc385"

# Reference palette (validated: blue, orange, aqua pass CVD + normal-vision checks).
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"
OTHER = "#b9b7ae"  # neutral for de-emphasised marks
FONT = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'

REASON_COLORS = {"Carrier": BLUE, "Weather": ORANGE, "National Air System": AQUA}

SHORT = {"WN": "Southwest", "AA": "American", "DL": "Delta", "UA": "United", "OO": "SkyWest",
         "YX": "Republic", "MQ": "Envoy", "NK": "Spirit", "B6": "JetBlue", "AS": "Alaska",
         "9E": "Endeavor", "OH": "PSA", "F9": "Frontier", "G4": "Allegiant", "HA": "Hawaiian"}

pio.templates["hw4"] = go.layout.Template(layout=go.Layout(
    font=dict(family=FONT, size=13, color=INK2),
    paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
    title=dict(font=dict(size=15, color=INK), x=0, xanchor="left", y=0.97),
    xaxis=dict(gridcolor=GRID, linecolor=AXIS, showline=True, zeroline=False,
               tickfont=dict(color=MUTED), title=dict(font=dict(color=INK2, size=12))),
    yaxis=dict(gridcolor=GRID, linecolor=AXIS, zeroline=False,
               tickfont=dict(color=MUTED), title=dict(font=dict(color=INK2, size=12))),
    legend=dict(orientation="h", x=0, y=1.0, yanchor="bottom", font=dict(color=INK2),
                bgcolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(family=FONT, color=INK)),
    margin=dict(l=10, r=20, t=70, b=10),
    bargap=0.3,
))
pio.templates.default = "plotly_white+hw4"
CONFIG = {"displayModeBar": False, "responsive": True}


def show(fig):
    fig.show(config=CONFIG)


def short_name(full):
    """'Alaska Airlines Inc.: AS' -> 'Alaska'."""
    code = full.split(":")[-1].strip()
    return SHORT.get(code, full)


def load(name):
    return pd.read_csv(DATA / f"{name}.csv")


def result(label):
    return load(f"{PREFIX}_problem{label}")


def problem_sql(label):
    """Return the query text for one problem from the submitted SQL file."""
    text = (DATA / f"{PREFIX}.sql").read_text()
    blocks = re.split(r"^# Problem (\S+)\s*$", text, flags=re.M)
    for lab, body in zip(blocks[1::2], blocks[2::2]):
        if lab.lower() == label.lower():
            lines = [l for l in body.splitlines()
                     if not l.lstrip().startswith("# rows returned")]
            return "\n".join(lines).strip()
    raise KeyError(label)


def event_line(fig, x, text, y=1.0, xanchor="left", label_x=None):
    fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=y, xref="x", yref="paper",
                  line=dict(color=MUTED, width=1))
    fig.add_annotation(x=label_x if label_x is not None else x, y=y, xref="x", yref="paper",
                       text=text, showarrow=False,
                       xanchor=xanchor, yanchor="top", xshift=4 if xanchor == "left" else -4,
                       font=dict(size=11, color=INK2), align=xanchor)


# ---------------------------------------------------------------- story charts
def fig_daily_cancellations():
    d = load("daily")
    d["flight_date"] = pd.to_datetime(d["flight_date"])
    fig = go.Figure()
    for col, name in [("cancel_carrier", "Carrier"), ("cancel_weather", "Weather"),
                      ("cancel_nas", "National Air System")]:
        fig.add_bar(x=d.flight_date, y=d[col], name=name, marker_color=REASON_COLORS[name],
                    marker_line_color=SURFACE, marker_line_width=1,
                    hovertemplate=f"{name}: %{{y:,}}<extra></extra>")
    fig.update_layout(barmode="stack", hovermode="x unified", height=430, bargap=0.15,
                      legend_traceorder="normal",
                      title="Cancelled flights per day, by reason",
                      yaxis_title="Cancelled flights", xaxis=dict(dtick=7 * 86400000, tick0="2024-01-01", tickformat="%b %d"))
    event_line(fig, pd.Timestamp("2024-01-06"), "Jan 6: FAA grounds<br>737 MAX 9 jets", y=0.97)
    event_line(fig, pd.Timestamp("2024-01-15"), "Jan 15: worst day,<br>2,962 cancellations", y=0.97,
               label_x=pd.Timestamp("2024-01-15 12:00"))
    event_line(fig, pd.Timestamp("2024-01-27"), "Jan 26–27: MAX 9s<br>back in service", y=0.62)
    return fig


def fig_carrier_cancellations():
    d = load("daily_carrier_cancel")
    d["flight_date"] = pd.to_datetime(d["flight_date"])
    fig = go.Figure()
    for col, name, color in [("united", "United", ORANGE), ("alaska", "Alaska", BLUE),
                             ("all_other_airlines", "All 13 other airlines", MUTED)]:
        fig.add_scatter(x=d.flight_date, y=d[col], name=name, mode="lines",
                        line=dict(color=color, width=2),
                        hovertemplate=f"{name}: %{{y:,}}<extra></extra>")
    # direct labels at the peak of each highlighted line
    for col, name, day in [("united", "United", "2024-01-22"), ("alaska", "Alaska", "2024-01-11")]:
        i = d.index[d.flight_date == pd.Timestamp(day)][0]
        fig.add_annotation(x=d.flight_date[i], y=d[col][i], text=f"<b>{name}</b>", showarrow=False,
                           yshift=12, font=dict(size=12, color=INK))
    fig.update_layout(hovermode="x unified", height=400, yaxis_range=[0, 300],
                      title="Cancellations the airline itself caused (code A), per day",
                      yaxis_title="Carrier-caused cancellations",
                      xaxis=dict(dtick=7 * 86400000, tick0="2024-01-01", tickformat="%b %d"))
    fig.add_vrect(x0=pd.Timestamp("2024-01-05 12:00"), x1=pd.Timestamp("2024-01-27 12:00"),
                  fillcolor=GRID, opacity=0.35, line_width=0, layer="below")
    fig.add_annotation(x=pd.Timestamp("2024-01-05 18:00"), y=1.0, yref="paper", showarrow=False,
                       text="737 MAX 9 grounding (Jan 6 – Jan 26/27)", yanchor="top", xanchor="left",
                       font=dict(size=11, color=INK2))
    return fig


POS = {"OO": "middle right", "F9": "middle right", "B6": "bottom center", "DL": "middle right",
       "OH": "top center", "G4": "top center", "AA": "top center"}


def fig_airline_bubble():
    s = load("airline_scorecard")
    s["short"] = s.code.map(SHORT)
    hi = s.code.isin(["AS", "UA"])
    fig = go.Figure()
    for mask, color, name in [(~hi, OTHER, "Other airlines"), (hi, BLUE, "Alaska & United (737 MAX 9 operators)")]:
        g = s[mask]
        fig.add_scatter(
            x=g.avg_dep_delay, y=g.pct_cancelled, mode="markers+text", name=name,
            text=g.short, textposition=[POS.get(c, "top center") for c in g.code],
            textfont=dict(size=11, color=INK2),
            marker=dict(size=10 + 30 * (g.flights / s.flights.max()) ** 0.5, color=color,
                        line=dict(color=SURFACE, width=2)),
            customdata=g[["airline_name", "flights", "cancelled", "pct_dep_delayed_15"]],
            hovertemplate=("<b>%{customdata[0]}</b><br>%{customdata[1]:,} flights<br>"
                           "Cancelled: %{customdata[2]:,} (%{y:.1f}%)<br>"
                           "Avg departure delay: %{x:.1f} min<br>"
                           "Left 15+ min late: %{customdata[3]:.1f}%<extra></extra>"))
    fig.update_layout(height=470, title="Average delay vs. cancellation rate, by airline (dot size = flights)",
                      xaxis_title="Average departure delay (minutes, early = 0)",
                      yaxis_title="Flights cancelled (%)", yaxis=dict(rangemode="tozero"),
                      xaxis=dict(range=[9, 28]))
    return fig


def fig_airports_scatter():
    a = load("airports")
    a = a[a.departed > 0]
    label = a.code.isin(["CKB", "ELM", "DSM", "ORD", "ATL", "DEN", "SJC"])
    fig = go.Figure()
    fig.add_scatter(x=a.departed, y=a.avg_dep_delay, mode="markers", name="Airport",
                    marker=dict(size=8, color=OTHER, line=dict(color=SURFACE, width=1)),
                    customdata=a[["airport_name", "code"]],
                    hovertemplate=("<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                                   "%{x:,} departures<br>Avg delay %{y:.1f} min<extra></extra>"),
                    showlegend=False)
    g = a[label]
    fig.add_scatter(x=g.departed, y=g.avg_dep_delay, mode="markers+text", text=g.code,
                    textposition="middle right", textfont=dict(size=11, color=INK),
                    marker=dict(size=9, color=BLUE, line=dict(color=SURFACE, width=2)),
                    customdata=g[["airport_name", "code"]], showlegend=False,
                    hovertemplate=("<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                                   "%{x:,} departures<br>Avg delay %{y:.1f} min<extra></extra>"))
    fig.add_shape(type="line", x0=1000, x1=1000, y0=0, y1=1, yref="paper",
                  line=dict(color=MUTED, width=1))
    fig.add_annotation(x=3, y=1, yref="paper", text="1,000 departures", showarrow=False,
                       xanchor="left", yanchor="top", xshift=4, font=dict(size=11, color=INK2))
    fig.update_layout(height=470, margin=dict(t=50), title="Each airport's average departure delay vs. how many flights it had",
                      xaxis=dict(type="log", title="Departures in January 2024 (log scale)"),
                      yaxis_title="Average departure delay (minutes)")
    return fig


def fig_reason_airports():
    r = load("cancel_reason_airports").iloc[::-1]
    r["label"] = r.code + "  " + r.airport_name.str.split(":").str[0]
    fig = go.Figure()
    for col, name in [("carrier", "Carrier"), ("weather", "Weather"), ("nas", "National Air System")]:
        fig.add_bar(y=r.label, x=r[col], name=name, orientation="h",
                    marker_color=REASON_COLORS[name], marker_line_color=SURFACE, marker_line_width=2,
                    hovertemplate=f"{name}: %{{x:,}}<extra></extra>")
    fig.update_layout(barmode="stack", height=520, hovermode="y unified", legend_traceorder="normal",
                      title="Cancellations at the 15 airports with the most, by reason",
                      xaxis_title="Cancelled departures", bargap=0.25)
    return fig


def fig_time_of_day():
    t = load("time_of_day")
    t["hour"] = t.dep_time_block.str[:2].astype(int)
    t.loc[t.dep_time_block == "0001-0559", "hour"] = 5
    t["label"] = t.dep_time_block.str[:2] + ":00"
    t.loc[t.dep_time_block == "0001-0559", "label"] = "before 6:00"
    fig = go.Figure()
    fig.add_scatter(x=t.label, y=t.pct_dep_delayed_15, mode="lines+markers", name="Left 15+ min late",
                    line=dict(color=BLUE, width=2), marker=dict(size=8, line=dict(color=SURFACE, width=2)),
                    customdata=t[["flights", "avg_dep_delay"]],
                    hovertemplate=("Scheduled %{x}<br>%{y:.1f}% left 15+ min late<br>"
                                   "Avg delay %{customdata[1]:.1f} min<br>%{customdata[0]:,} flights<extra></extra>"),
                    showlegend=False)
    lo = t.loc[t.dep_time_block == "0600-0659"].iloc[0]
    hi = t.loc[t.pct_dep_delayed_15.idxmax()]
    for row, pos in [(lo, "bottom center"), (hi, "top center")]:
        fig.add_annotation(x=row.label, y=row.pct_dep_delayed_15, text=f"{row.pct_dep_delayed_15:.1f}%",
                           showarrow=False, yshift=-16 if pos.startswith("bottom") else 16,
                           font=dict(size=12, color=INK))
    fig.update_layout(height=380, margin=dict(t=45), title="Share of flights leaving 15+ minutes late, by scheduled departure hour",
                      yaxis=dict(title="Flights delayed 15+ min (%)", rangemode="tozero"),
                      xaxis=dict(title="Scheduled departure hour", tickangle=-45))
    return fig


def fig_weekday():
    w = load("weekday").sort_values("day_code")
    w["short"] = w.day_of_week.str[:3]
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.12,
                        subplot_titles=("Total flights in January (what Problem 3 ranks)",
                                        "Average flights per day"))
    five = w.days_in_month == 5
    colors = [BLUE if f else OTHER for f in five]
    fig.add_bar(x=w.short, y=w.flights, marker_color=colors, row=1, col=1, showlegend=False,
                customdata=w.days_in_month,
                hovertemplate="%{x}: %{y:,} flights over %{customdata} days<extra></extra>")
    fig.add_bar(x=w.short, y=w.flights_per_day, marker_color=colors, row=1, col=2, showlegend=False,
                hovertemplate="%{x}: %{y:,.0f} flights per day<extra></extra>")
    fig.update_traces(marker_cornerradius=4)
    fig.update_layout(height=400, margin=dict(t=90),
                      title="Blue = the three weekdays that occur five times in January 2024")
    fig.update_annotations(font=dict(size=13, color=INK))
    fig.update_yaxes(rangemode="tozero")
    return fig


# ---------------------------------------------------------- per-question charts
def fig_q1():
    q = result("1")
    q["short"] = q.airline_name.map(short_name)
    fig = go.Figure(go.Bar(x=q.max_departure_delay_minutes, y=q.short, orientation="h",
                           marker=dict(color=BLUE, cornerradius=4),
                           text=(q.max_departure_delay_minutes / 60).round(1).astype(str) + " h",
                           textposition="outside", textfont=dict(color=INK2, size=11),
                           hovertemplate="%{y}: %{x:,} minutes<extra></extra>"))
    fig.update_layout(height=460, margin=dict(t=45), title="Longest single departure delay per airline",
                      xaxis_title="Minutes (label = hours)", xaxis=dict(range=[0, 3500]),
                      yaxis=dict(autorange="reversed"))
    return fig


def fig_q2():
    q = result("2")
    q["short"] = q.airline_name.map(short_name)
    fig = go.Figure(go.Bar(x=q.max_early_departure_minutes, y=q.short, orientation="h",
                           marker=dict(color=BLUE, cornerradius=4),
                           text=q.max_early_departure_minutes, textposition="outside",
                           textfont=dict(color=INK2, size=11),
                           hovertemplate="%{y}: left %{x} minutes early<extra></extra>"))
    fig.update_layout(height=460, margin=dict(t=45), title="Earliest departure per airline (minutes before schedule)",
                      xaxis_title="Minutes early", xaxis=dict(range=[0, 62]),
                      yaxis=dict(autorange="reversed"))
    return fig


def fig_q5():
    q = load("airline_airport_worst")
    q["short"] = q.airline_code.map(SHORT)
    q["label"] = q.short + " @ " + q.airport_code
    small = q.departures < 20
    fig = go.Figure()
    for mask, color, name in [(~small, BLUE, "20+ departures"), (small, OTHER, "Fewer than 20 departures")]:
        g = q[mask]
        fig.add_bar(x=g.avg_dep_delay, y=g.label, orientation="h", name=name,
                    marker=dict(color=color, cornerradius=4),
                    text="n=" + g.departures.astype(str), textposition="outside",
                    textfont=dict(color=INK2, size=11),
                    customdata=g[["airline_name", "airport_name", "departures"]],
                    hovertemplate=("<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
                                   "Avg delay %{x:.1f} min over %{customdata[2]} departures<extra></extra>"))
    fig.update_layout(height=500, title="Each airline's worst airport (n = departures behind the average)",
                      xaxis_title="Average departure delay (minutes)", xaxis=dict(range=[0, 250]),
                      yaxis=dict(categoryorder="array", categoryarray=list(q.label[::-1])),
                      barmode="overlay")
    return fig


def fig_q6b():
    b = result("6b")
    counts = b.most_frequent_reason.value_counts().reindex(["Weather", "Carrier", "National Air System"]).fillna(0)
    fig = go.Figure(go.Bar(x=counts.values, y=counts.index, orientation="h",
                           marker=dict(color=[REASON_COLORS[r] for r in counts.index], cornerradius=4),
                           text=counts.astype(int).astype(str) + " airports", textposition="outside",
                           textfont=dict(color=INK2, size=12),
                           hovertemplate="%{y}: top reason at %{x} airports<extra></extra>"))
    fig.update_layout(height=230, margin=dict(t=45), title="Airports grouped by their most frequent cancellation reason",
                      xaxis=dict(title="Airports (ties counted for each tied reason)", range=[0, 300]),
                      yaxis=dict(autorange="reversed"))
    return fig


def fig_q7():
    q = result("7")
    q["flight_date"] = pd.to_datetime(q["flight_date"])
    fig = go.Figure()
    fig.add_scatter(x=q.flight_date, y=q.num_flights, name="Flights that day", mode="lines+markers",
                    line=dict(color=OTHER, width=2), marker=dict(size=8, line=dict(color=SURFACE, width=2)),
                    hovertemplate="Flights: %{y:,}<extra></extra>")
    fig.add_scatter(x=q.flight_date, y=q.avg_flights_3day, name="3-day moving average",
                    mode="lines", line=dict(color=BLUE, width=2),
                    hovertemplate="3-day average: %{y:,.0f}<extra></extra>")
    sats = q[q.flight_date.dt.dayofweek == 5]
    for _, r in sats.iterrows():
        fig.add_annotation(x=r.flight_date, y=r.num_flights, text="Sat", showarrow=False,
                           yshift=-14, font=dict(size=10, color=MUTED))
    fig.update_layout(hovermode="x unified", height=400,
                      title="Scheduled flights per day and the 3-day moving average",
                      yaxis=dict(title="Flights", range=[14500, 19500]),
                      xaxis=dict(dtick=7 * 86400000, tick0="2024-01-01", tickformat="%b %d"))
    return fig


def md_table(df, floatfmt=",.2f"):
    from IPython.display import Markdown
    return Markdown(df.to_markdown(index=False, floatfmt=floatfmt, intfmt=","))
