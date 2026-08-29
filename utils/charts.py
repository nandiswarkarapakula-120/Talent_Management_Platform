"""
Talent Management Platform - Reusable Plotly Chart Components
"""

import plotly.graph_objects as go
import plotly.express as px

PALETTE = ["#6C5CE7", "#00CEC9", "#FDCB6E", "#FF7675", "#74B9FF", "#55EFC4", "#A29BFE", "#FAB1A0"]


def donut_chart(labels, values, title="", height=320):
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=PALETTE, line=dict(color="#FFFFFF", width=2)),
        textinfo="percent", hoverinfo="label+percent+value"
    )])
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#2D3436")),
        showlegend=True, height=height,
        margin=dict(t=50, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    return fig


def line_chart(x, y, title="", x_title="", y_title="", height=320, color="#6C5CE7"):
    fig = go.Figure(data=go.Scatter(
        x=x, y=y, mode="lines+markers", line=dict(color=color, width=3, shape="spline"),
        marker=dict(size=8, color=color), fill="tozeroy", fillcolor="rgba(108, 92, 231, 0.13)"
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#2D3436")),
        xaxis_title=x_title, yaxis_title=y_title, height=height,
        margin=dict(t=50, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#EEEEEE"),
    )
    return fig


def bar_chart(x, y, title="", x_title="", y_title="", height=320, horizontal=False):
    if horizontal:
        fig = go.Figure(go.Bar(x=y, y=x, orientation="h", marker=dict(color=PALETTE * 3)))
    else:
        fig = go.Figure(go.Bar(x=x, y=y, marker=dict(color=PALETTE * 3)))
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#2D3436")),
        xaxis_title=x_title, yaxis_title=y_title, height=height,
        margin=dict(t=50, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#EEEEEE"),
    )
    return fig


def radar_chart(categories, values, title="", height=380):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(108,92,231,0.3)",
        line=dict(color="#6C5CE7", width=2)
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#2D3436")),
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False, height=height,
        margin=dict(t=50, b=20, l=40, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def gauge_chart(value, title="", max_value=100, height=280, color="#6C5CE7"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, max_value]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, max_value * 0.4], "color": "#FFE8E8"},
                {"range": [max_value * 0.4, max_value * 0.75], "color": "#FFF3D6"},
                {"range": [max_value * 0.75, max_value], "color": "#DFF7E8"},
            ],
        }
    ))
    fig.update_layout(height=height, margin=dict(t=50, b=10, l=30, r=30),
                       paper_bgcolor="rgba(0,0,0,0)")
    return fig


def progress_area_chart(x, y, title="", height=300):
    fig = px.area(x=x, y=y, title=title)
    fig.update_traces(line_color="#00CEC9", fillcolor="rgba(0,206,201,0.25)")
    fig.update_layout(
        height=height, margin=dict(t=50, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title=""), yaxis=dict(showgrid=True, gridcolor="#EEEEEE", title=""),
    )
    return fig
