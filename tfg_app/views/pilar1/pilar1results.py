import reflex as rx


from tfg_app.components.leyenda import leyenda1
from tfg_app.global_state import GlobalState
from tfg_app.styles.fonts import Font
from tfg_app.styles.styles import Size as size
from tfg_app.backend.pens import RatioSust1
from tfg_app.views.pilar1.pilar1form import FormState
from tfg_app.components.info_button import info_button
from tfg_app.styles.colors import LegendColor as legcolor

try:
    RATIO_SUSTITUCION = RatioSust1.ratio
except Exception as e:
    print(f"Error al obtener el ratio de sustitución: {e}")



import math


def redondear(numero):
    return math.ceil(numero*100)/100


def show_ratio_pie_chart(ratio_sustitucion) -> rx.Component:
    

    # Prepara los datos del gráfico
    data = [
        {"name": "Pensión pública", "value": redondear(ratio_sustitucion), "fill": "#00FF7F"},
        {"name": "Salario", "value": redondear(100 - ratio_sustitucion), "fill": "#D3D3D3"},
    ]

    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.heading("Ratio de Sustitución", size="4", color="black", aria_label="Ratio de Sustitución"),
                info_button(color="black",info="El ratio de sustitución es el porcentaje de tu salario medio que representa la pensión pública."),
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
                    end_angle=180+360,
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
            rx.text(f"{redondear(ratio_sustitucion)}% de cobertura", color="black", font_size="1.5em", text_align="center",margin_top="-.5em"),
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


def show_pension_salary_comparison(pension_primer_pilar:float, salario_actual:float) -> rx.Component:

    data = [
        {"name": "Comparación", "Pensión pública": pension_primer_pilar, "Salario": salario_actual},
    ]
    return rx.recharts.bar_chart(
        rx.recharts.cartesian_grid(),
        rx.recharts.bar(
            data_key="Pensión pública",
            stroke=legcolor.LEGEND_1.value,
            fill=legcolor.LEGEND_1.value,

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



def results_pilar1() -> rx.Component:

    pension_primer_pilar = GlobalState.pension_primer_pilar
    pension_1p_anual = pension_primer_pilar * 12
    
    salario_actual = FormState.salario_medio
    salario_mensual = redondear(salario_actual/12)

    # Get salario_medio from form data and properly convert to float
    print(f"salario_medio: {salario_actual}")
    #if salario_actual is None or salario_actual == 0:
    #    raise ValueError("El salario medio no puede ser nulo o cero.") 
        

    ratio_sustitucion = RATIO_SUSTITUCION

    ratio_gt_100_component = rx.box(
        rx.vstack(
            rx.text("El ratio de sustitución es superior al 100%. Esto significa que tu pensión pública es mayor que tu salario medio.", 
                   color="black",
                   text_align="center",
                   width="90%"),
            show_pension_salary_comparison(pension_primer_pilar, salario_mensual),
            leyenda1(),
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
        padding_top= "8em",
        padding_bottom="4em"
    )

    ratio_lte_100_component = rx.box(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Pensión mensual:", size="4", color="black"),
                        rx.text(f"{pension_primer_pilar} €/mes", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.heading("Pensión anual:", size="4", color="black"),
                        rx.text(f"{pension_1p_anual} €/año", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    width="50%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.heading("Salario mensual:", size="4", color="black"),
                        rx.text(f"{salario_mensual} €/mes", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.heading("Salario anual:", size="4", color="black"),
                        rx.text(f"{salario_actual} €/año", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    width="50%",
                ),
                display="flex",
                flex_direction=["column", "column", "row"],  # Responsive layout
                justify="between",
                width="100%",
                gap="4",
            ),
            show_ratio_pie_chart(ratio_sustitucion),
            leyenda1(),
            align_items="center",
            justify_content="center",
            padding="2em",
            border_radius="md",
            box_shadow="lg",
            background_color="white",
            width="90%",
            max_width="1200px",
            margin="2em auto",
            spacing="4",
        ),
        width="100%",
        display="flex",
        justify_content="center",
        margin_bottom="4em",
    )

    return rx.cond(
        ratio_sustitucion > 100,
        ratio_gt_100_component,
        ratio_lte_100_component
    )