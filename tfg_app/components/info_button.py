import reflex as rx

def info_button(info:str,color:str):
    return rx.tooltip(
        rx.icon("info",
                width=16,
                height=16,
                overflow="visible",
                color=color),
        content=info,
    )
   