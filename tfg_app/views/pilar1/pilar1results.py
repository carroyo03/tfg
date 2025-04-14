import reflex as rx


from tfg_app.components.leyenda import leyenda1
from tfg_app.global_state import GlobalState
from tfg_app.styles.fonts import Font
from tfg_app.styles.styles import Size as size
from tfg_app.backend.pens import calcular_ratio_sustitucion
from tfg_app.views.pilar1.pilar1form import FormState
from tfg_app.components.info_button import info_button


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
                info_button(color="silver",info="El ratio de sustitución es el porcentaje de tu salario medio que representa la pensión pública."),
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
            stroke=rx.color("accent",9),
            fill=rx.color("accent", 8),
        ),
        rx.recharts.bar(
            data_key="Salario",
            stroke=rx.color("blue", 7),
            fill=rx.color("blue", 6),
        ),
        rx.recharts.x_axis(
            data_key="name",
        ),
        rx.recharts.y_axis(),
        rx.recharts.legend(),
        rx.recharts.graphing_tooltip(),
        data=data,
        width="100%",
        height=300,
    )



def results_pilar1() -> rx.Component:

    pension_primer_pilar = GlobalState.pension_primer_pilar
    pension_1p_anual = pension_primer_pilar * 12
    
    # Get salario_medio from form data and properly convert to float
    try:
        # Extract the value and convert to float
        salario_actual_value = FormState.form_data.get('salario_medio')
        # Convert to float - this handles both primitive values and Reflex state objects
        salario_actual = float(salario_actual_value) if salario_actual_value is not None else 0.0
    except (TypeError, ValueError, KeyError):
        # Fallback if conversion fails or key doesn't exist
        salario_actual = 0.0
        
    # Now that salario_actual is a proper float, we can safely perform division
    salario_mensual = salario_actual / 12
    ratio_sustitucion = calcular_ratio_sustitucion(pension_primer_pilar, salario_actual)

    ratio_gt_100_component = rx.box(
        rx.vstack(
            rx.text("El ratio de sustitución es superior al 100%. Esto significa que tu pensión pública es mayor que tu salario medio.", 
                   color="black",
                   text_align="center",
                   width="90%"),
            show_pension_salary_comparison(pension_primer_pilar, salario_actual),
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
    )

    return rx.cond(
        ratio_sustitucion > 100,
        ratio_gt_100_component,
        ratio_lte_100_component
    )