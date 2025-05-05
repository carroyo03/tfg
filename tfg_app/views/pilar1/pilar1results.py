import reflex as rx #type:ignore


from tfg_app.components.leyenda import leyenda1
from tfg_app.global_state import GlobalState
from tfg_app.styles.fonts import Font
from tfg_app.styles.styles import Size as size
from tfg_app.backend.pens import RatioSust1
from tfg_app.views.pilar1.pilar1form import FormState
from tfg_app.components.info_button import info_button
from tfg_app.styles.colors import LegendColor as legcolor





import math


def redondear(numero):
    return math.ceil(numero*100)/100


def show_ratio_pie_chart(ratio_sustitucion) -> rx.Component:
    if type(ratio_sustitucion) != float:
        try:
            ratio_sustitucion = float(ratio_sustitucion)
        except (TypeError, ValueError):
            try:
                ratio_sustitucion = ratio_sustitucion.to(float)
            except (TypeError, ValueError):
                ratio_sustitucion = 0.0
    try:
        safe_ratio = max(min(float(ratio_sustitucion), 100), 0)
    except (TypeError, ValueError):
        rx.console_log("Error obtaining ratio data, defaulting to original value")
        safe_ratio = ratio_sustitucion
    safe_salary_ratio = 100 - safe_ratio
    # Prepara los datos del gráfico
    data = [
        {"name": "Pensión pública", "value": redondear(safe_ratio), "fill": "#00FF7F"},
        {"name": "Salario", "value": redondear(safe_salary_ratio), "fill": "#D3D3D3"},
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
            rx.text(f"{redondear(safe_ratio)}% de cobertura", color="black", font_size="1.5em", text_align="center",margin_top="-.5em"),
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


def show_pension_salary_comparison(pension_primer_pilar:float, salario_mensual) -> rx.Component:

    data = [
        {"name": "Comparación", "Pensión pública": pension_primer_pilar, "Salario": salario_mensual},
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



def results_pilar1(direction:str="") -> rx.Component:
    if (
        GlobalState.pension_primer_pilar is None or
        GlobalState.form_data_primer_pilar is None or
        GlobalState.form_data_primer_pilar.get("salario_medio") is None
    ):
        return rx.text('Datos no disponibles', color='red', font_size='1.2em', text_align='center')

    pension_primer_pilar = GlobalState.pension_primer_pilar
    print(f"Pension primer GS{pension_primer_pilar.to(rx.Var[float])}")
    salario_anual = GlobalState.salario_anual
    salario_mensual = GlobalState.salario_mensual
    print(f"Salario GS{salario_mensual.to(rx.Var[float])}")
    pension_1p_anual = GlobalState.pension_anual_primer
    ratio_sustitucion = pension_primer_pilar / salario_mensual * 100


    ratio_gt_100_component = rx.box(
        rx.vstack(
            rx.text(
                "El ratio de sustitución es superior al 100%. Esto significa que tu pensión pública es mayor que tu salario medio.",
                color="black",
                text_align="center",
                width=["100%", "90%"],  # Responsive width
            ),
            show_pension_salary_comparison(pension_primer_pilar, salario_mensual),
            leyenda1(pension_is_gt_salary=True),
            width="100%",
            spacing="5",
            align_items="center",
            justify="center",
            padding=rx.breakpoints(initial="1em", sm="2em", md="2em"),
            background_color="white",
            border_radius="md",
            box_shadow="lg",
            margin=rx.breakpoints(initial="1em auto", sm="2em auto"),
        ),
        width="100%",
        display="flex",
        justify_content="center",
        padding_top=rx.breakpoints(initial="2em", md="8em"),
        padding_bottom=rx.breakpoints(initial="1em", md="4em"),
    )

    ratio_lte_100_component = rx.box(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Pensión mensual:", size="4", color="black"),
                        rx.text(f"{pension_primer_pilar:.2f} €/ mes", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.heading("Pensión anual:", size="4", color="black"),
                        rx.text(f"{pension_1p_anual:.2f} €/ año", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.heading("Salario mensual:", size="4", color="black"),
                        rx.text(f"{salario_mensual:.2f} €/ mes", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.heading("Salario anual:", size="4", color="black"),
                        rx.text(f"{salario_anual:.2f} €/ año", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    width="100%",
                ),
                direction=rx.breakpoints(initial="column", md="row") if direction == "" else direction,  # Responsive direction
                justify_content="space-around",
                width="100%",
                spacing="2",

            ),
            show_ratio_pie_chart(ratio_sustitucion),
            leyenda1(),
            align_items="center",
            justify_content="center",
            padding=rx.breakpoints(initial="1em", sm="2em"),
            border_radius="md",
            box_shadow="lg",
            background_color="white",
            width='100%',
            max_width="1200px",
            #margin=rx.breakpoints(initial="1em auto", sm="2em auto"),
            spacing="4",
        ),
        width="100%",
        display="flex",
        justify_content="center",
        margin_bottom="15%",
    )
                                      

    return rx.cond(
        ratio_sustitucion > 100,
        ratio_gt_100_component,
        ratio_lte_100_component,
    )