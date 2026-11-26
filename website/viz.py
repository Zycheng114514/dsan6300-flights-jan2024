# Charts and tables for the website. All data comes from the CSVs in data/.
import pandas as pd
import plotly.express as px
from IPython.display import Markdown

BLUE, ORANGE, GREEN, GRAY = "steelblue", "darkorange", "seagreen", "lightgray"


def read(name):
    return pd.read_csv(f"data/{name}.csv")


def result(problem):
    return read(f"hw4_cheng_zhiyang_zc385_problem{problem}")


def table(df):
    return Markdown(df.to_markdown(index=False, floatfmt=",.2f", intfmt=","))


def short_name(names):
    # "Alaska Airlines Inc.: AS" -> "Alaska Airlines"
    return names.str.split(":").str[0].str.replace(" Inc.", "").str.replace(" Co.", "")


def style(fig, height=420):
    fig.update_layout(template="plotly_white", height=height, legend_title_text="",
                      margin=dict(l=10, r=10, t=60, b=10))
    return fig


def daily_cancellations():
    d = read("daily").rename(columns={"carrier": "Carrier", "weather": "Weather",
                                      "nas": "National Air System"})
    fig = px.bar(d, x="flight_date", y=["Carrier", "Weather", "National Air System"],
                 color_discrete_sequence=[BLUE, ORANGE, GREEN],
                 title="Cancelled flights per day, by reason",
                 labels={"flight_date": "", "value": "Cancelled flights"})
    fig.add_vline(x="2024-01-05 12:00", line_dash="dot", line_color="gray")
    fig.add_annotation(x="2024-01-05 12:00", y=1, yref="paper", text="737 MAX 9 grounded",
                       showarrow=False, xanchor="left", yanchor="top")
    return style(fig)


def airline_bar(column, title, xlabel):
    a = read("airlines")
    a["airline"] = short_name(a.airline_name)
    a = a.sort_values(column)
    colors = [BLUE if c in ("AS", "UA") else GRAY for c in a.code]
    fig = px.bar(a, x=column, y="airline", orientation="h", text=column, title=title,
                 labels={column: xlabel, "airline": ""})
    fig.update_traces(marker_color=colors, texttemplate="%{x:.1f}", textposition="outside")
    return style(fig, height=480)


def airline_cancellations():
    return airline_bar("pct_cancelled", "Share of flights cancelled (Alaska and United in blue)",
                       "Cancelled (%)")


def airline_delays():
    return airline_bar("avg_delay", "Average departure delay (Alaska and United in blue)",
                       "Minutes (early departures count as 0)")


def time_of_day():
    t = read("time_of_day")
    t["hour"] = t.time_block.str[:2] + ":00"
    t.loc[t.time_block == "0001-0559", "hour"] = "before 6"
    fig = px.bar(t, x="hour", y="pct_late", title="Flights that left 15+ minutes late, by scheduled hour",
                 labels={"hour": "Scheduled departure hour", "pct_late": "Left 15+ min late (%)"})
    fig.update_traces(marker_color=BLUE)
    return style(fig, height=380)


def q1_chart():
    q = result(1)
    q["airline"] = short_name(q.airline_name)
    fig = px.bar(q, x="max_departure_delay_minutes", y="airline", orientation="h",
                 title="Longest departure delay per airline",
                 labels={"max_departure_delay_minutes": "Minutes", "airline": ""})
    fig.update_traces(marker_color=BLUE)
    return style(fig, height=460)


def q3_chart():
    q = result(3)
    fig = px.bar(q, x="day_of_week", y="num_flights", title="Flights by day of the week",
                 labels={"day_of_week": "", "num_flights": "Flights"})
    fig.update_traces(marker_color=BLUE)
    return style(fig, height=360)


def q7_chart():
    q = result(7).rename(columns={"num_flights": "Flights that day",
                                  "avg_flights_3day": "3-day average"})
    fig = px.line(q, x="flight_date", y=["Flights that day", "3-day average"],
                  color_discrete_sequence=[GRAY, BLUE], markers=True,
                  title="Flights per day and 3-day moving average",
                  labels={"flight_date": "", "value": "Flights"})
    return style(fig, height=400)
