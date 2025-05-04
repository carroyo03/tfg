import reflex as rx #type:ignore
from tfg_app.components.leyenda import leyenda2
from tfg_app.global_state import GlobalState
from tfg_app.backend.pens import RatioSust1, RatioSust2
from tfg_app.views.pilar1.pilar1form import FormState
from tfg_app.components.info_button import info_button
from tfg_app.styles.colors import LegendColor as legcolor
import math

def redondear(numero):
    try:
        return math.ceil(float(numero)*100)/100
    except Exception:
        return 0.0



def show_ratio_pie_chart2(ratio_sust_1, ratio_sust_2) -> rx.Component:
    val1 = ratio_sust_1
    val2 = ratio_sust_2
    val3 = 100 - val1 - val2
    data = [
        {"name": "Pensión pública", "value": round(val1,2), "fill": "#00FF7F"},
        {"name": "Pensión de empresa", "value": round(val2,2), "fill": "#FFA500"},
        {"name": "Salario", "value": round(val3,2), "fill": "#D3D3D3"},
    ]
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.heading("Ratio de Sustitución", size="4", color="black", aria_label="Ratio de Sustitución"),
                info_button(color="silver", info="El ratio de sustitución es el porcentaje de tu salario medio que representa la pensión."),
                spacing="2",
                align="center"
            ),
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    data=data,
                    data_key="value",
                    name_key="name",
                    stroke="0",
                    start_angle=180,
                    end_angle=540,
                    inner_radius="60%",
                    active_index=0,
                    aria_label="Gráfico de tarta con el ratio de sustitución",
                ),
                rx.recharts.pie(
                    outer_radius="50%",
                ),
                rx.recharts.graphing_tooltip(),
                width="100%",
                height=225,
                margin_top="-1em"
            ),
            rx.text(f"{(val1 + val2):.2f}% de cobertura", color="black", font_size="1.5em", text_align="center", margin="-.5em .05em"),
            border_radius="md",
            box_shadow="lg",
            background_color="white",
            width="100%",
            justify_content="center",
            flex_direction="column",
        ),
        width="100%",
        height="auto",
        align_items="center",
        justify_content="center",
        padding="1em 0em",
    )

def show_pension_salary_comparison2(pension_primer_pilar: float, pension_segundo_pilar: float, salario_actual: float) -> rx.Component:
    v1 = pension_primer_pilar
    v2 = pension_segundo_pilar
    v3 = salario_actual
    data = [
        {"name": "Comparación", "Pensión pública": v1, "Pensión de empresa": v2, "Salario": v3},
    ]
    return rx.recharts.bar_chart(
        rx.recharts.cartesian_grid(),
        rx.recharts.bar(
            data_key="Pensión pública",
            stroke=legcolor.LEGEND_1.value,
            fill=legcolor.LEGEND_1.value,
            stack_id="pension"
        ),
        rx.recharts.bar(
            data_key="Pensión de empresa",
            stroke=legcolor.LEGEND_1_1.value,
            fill=legcolor.LEGEND_1_1.value,
            stack_id="pension"
        ),
        rx.recharts.bar(
            data_key="Salario",
            stroke=legcolor.LEGEND_2.value,
            fill=legcolor.LEGEND_2.value,
        ),
        rx.recharts.x_axis(
            data_key="name",
        ),
        rx.recharts.y_axis(),
        rx.recharts.graphing_tooltip(),
        data=data,
        width="100%",
        height=300,
    )

def results_pilar2() -> rx.Component:
    # Obtener datos del estado global
    global_state = GlobalState
    
    # Obtener datos del primer pilar
    form_data_1 = global_state.form_data_primer_pilar
    print(f"Form data 1: {form_data_1.to(dict)}")
    
    # Verificar que los datos existen
    if form_data_1 is None | form_data_1["salario_medio"] is None | form_data_1['salario_medio'] == 0:
        print("Error: No se encontraron datos del primer pilar o falta el salario medio")
        salario_anual = 0.0
    else:
        print(f"Salario anual obtenido: {form_data_1.salario_medio}")
    
    salario_mensual = form_data_1.salario_medio.to(float) / 12


    pension_primer_pilar = global_state.pension_primer_pilar.to(float)



    ratio_sust_1 = pension_primer_pilar / salario_mensual * 100


    pension_segundo_pilar = global_state.pension_segundo_pilar.to(float)



    ratio_sust_2 = pension_segundo_pilar / salario_mensual * 100
    
    # PRINTS para debug (puedes quitarlos en producción)
    print(f"salario_mensual: {salario_mensual}")
    print(f"pension_mensual: {(pension_primer_pilar + pension_segundo_pilar)} €/mes")
    print(f"Ratio sustitucion total: {ratio_sust_1} (Ratio 1er pilar) + {ratio_sust_2} (Ratio 2o pilar) = {ratio_sust_1 + ratio_sust_2} %")

    ratio_gt_100_component = rx.box(
        rx.vstack(
            rx.text("El ratio de sustitución es superior al 100%. Esto significa que tu pensión pública es mayor que tu salario medio.",
                   color="black",
                   text_align="center",
                   width="90%"),
            show_pension_salary_comparison2(pension_primer_pilar, pension_segundo_pilar, salario_mensual),
            leyenda2(pension_is_gt_salary=True),
            width="100%",
            spacing="5",
            align_items="center",
            justify="center",
            padding="2em",
            background_color="white",
            border_radius="md",
            box_shadow="lg",
            margin="2em auto",
        ),
        width="100%",
        display="flex",
        justify_content="center",
        padding_top="8em",
        padding_bottom="4em"
    )

    ratio_lte_100_component = rx.box(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Pensión mensual:", size="4", color="black"),
                        rx.text(f"{(pension_primer_pilar + pension_segundo_pilar):.2f} €/mes", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.heading("Pensión anual:", size="4", color="black"),
                        rx.text(f"{(12*(pension_primer_pilar + pension_segundo_pilar)):.2f} €/año", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.heading("Salario mensual:", size="4", color="black"),
                        rx.text(f"{salario_mensual:.2f} €/mes", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.heading("Salario anual:", size="4", color="black"),
                        rx.text(f"{(salario_mensual * 12):.2f} €/año", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    width="100%",
                ),
                direction=rx.breakpoints(initial="column", md="row"),
                justify_content="space-around",
                width="100%",
                spacing='2',
            ),
            show_ratio_pie_chart2(ratio_sust_1, ratio_sust_2),
            leyenda2(),
            align_items="center",
            justify_content="center",
            padding=rx.breakpoints(initial="1em", sm="2em"),
            border_radius="md",
            box_shadow="lg",
            background_color="white",
            width="100%",
            max_width="1200px",
            #margin="2em auto",
            spacing="4",
        ),
        width="100%",
        display="flex",
        justify_content="center",
        margin_bottom="4em",
    )

    ratio_sustitucion = ratio_sust_1 + ratio_sust_2
    return rx.cond(
        ratio_sustitucion > 100,
        ratio_gt_100_component,
        ratio_lte_100_component
    )