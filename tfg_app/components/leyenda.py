import reflex as rx
from tfg_app.styles.colors import LegendColor as legcolor

def elem_leyenda(color:str,text:str):
    return rx.hstack(
        rx.icon("circle", color=color,fill=color),
        rx.text(text, color="black", margin_left=".1em"),
        justify="start",
        align="center",
    )


def leyenda1(pension_is_gt_salary:bool=False):
    return rx.card(
                    rx.text("Leyenda:", color="black",font_size="1em", font_weight="bold", margin_bottom=".1em"),
                    rx.cond(
                        pension_is_gt_salary == False,
                        elem_leyenda(legcolor.LEGEND_1.value,"Pensión pública"),
                        elem_leyenda(legcolor.LEGEND_3.value,'Pensión total')
                    ),
                    elem_leyenda(legcolor.LEGEND_2.value,"Salario por cubrir" if not pension_is_gt_salary else 'Salario'),
                    width="100%",
                    margin_top=".01%"
                )
def leyenda2(pension_is_gt_salary:bool=False):
    return rx.card(
                    rx.text("Leyenda:", color="black",font_size="1em", font_weight="bold", margin_bottom=".1em"),
                    elem_leyenda(legcolor.LEGEND_1.value,"Pensión pública"),
                    elem_leyenda(legcolor.LEGEND_1_1.value,"Pensión de empresa"),
                    rx.cond(
                        pension_is_gt_salary == True,
                        elem_leyenda(legcolor.LEGEND_3.value, 'Pensión total')
                    ),
                    elem_leyenda(legcolor.LEGEND_2.value,"Salario por cubrir"  if not pension_is_gt_salary else 'Salario'),
                    width="100%",
                    margin_top=".01%"
                )

def leyenda3(pension_is_gt_salary:bool=False):
    return rx.card(
                    rx.text("Leyenda:", color="black",font_size="1em", font_weight="bold", margin_bottom=".1em"),
                    elem_leyenda(legcolor.LEGEND_1.value,"Pensión pública"),
                    elem_leyenda(legcolor.LEGEND_1_1.value,"Pensión de empresa"),
                    elem_leyenda(legcolor.LEGEND_1_2.value,"Pensión privada"),
                    rx.cond(
                        pension_is_gt_salary == True,
                        elem_leyenda(legcolor.LEGEND_3.value, 'Pensión total')
                    ),
                    elem_leyenda(legcolor.LEGEND_2.value,"Salario por cubrir"  if not pension_is_gt_salary else 'Salario'),
                    width="100%",
                    margin_top=".01%"
                )
