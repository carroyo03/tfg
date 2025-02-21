import reflex as rx

def elem_leyenda(color:str,text:str):
    return rx.hstack(
        rx.icon("circle", color=color,fill=color),
        rx.text(text, color="black", margin_left=".1em"),
        justify="start",
        align="center",
    )


def leyenda1():
    return rx.card(
                    rx.text("Leyenda:", color="black",font_size="1em", font_weight="bold", margin_bottom=".1em"),
                    elem_leyenda("#00FF7F","Pensión pública"),
                    elem_leyenda("#D3D3D3","Salario por cubrir"),
                    width="100%",
                    margin_top=".01%"
                )
def leyenda2():
    return rx.card(
                    rx.text("Leyenda:", color="black",font_size="1em", font_weight="bold", margin_bottom=".1em"),
                    elem_leyenda("#00FF7F","Pensión pública"),
                    elem_leyenda("#FFA500","Pensión de empresa"),
                    elem_leyenda("#D3D3D3","Salario por cubrir"),
                    width="100%",
                    margin_top=".01%"
                )

def leyenda3():
    return rx.card(
                    rx.text("Leyenda:", color="black",font_size="1em", font_weight="bold", margin_bottom=".1em"),
                    elem_leyenda("#00FF7F","Pensión pública"),
                    elem_leyenda("#FFA500","Pensión de empresa"),
                    elem_leyenda("#00D0FF","Pensión privada"),
                    elem_leyenda("#D3D3D3","Salario por cubrir"),
                    width="100%",
                    margin_top=".01%"
                )
