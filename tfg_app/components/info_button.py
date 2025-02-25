import reflex as rx

def info_button(info:str,color:str):
    return rx.tooltip(
        rx.el.svg(
            rx.el.svg.circle(
                cx=8,
                cy=8,
                r=7,
                stroke=color,
                stroke_width=2,
                fill="transparent",
            ),
            rx.el.svg.text(
                "i",
                x=8,
                y=9,
                fill=color,
                text_anchor="middle",
                dominant_baseline="middle",
                font_weight="bold",
                font_size=9,
            ),
            width=16,
            height=16,
            overflow="visible",
        ),
        content=info,
    )