import reflex as rx


from tfg_app.components.leyenda import leyenda3
from tfg_app.global_state import GlobalState
from tfg_app.backend.pens import RatioSust1, RatioSust2, RatioSust3
from tfg_app.views.pilar1.pilar1form import FormState
from tfg_app.views.pilar3.pilar3form import Form3State
from tfg_app.components.info_button import info_button
from tfg_app.styles.colors import LegendColor as legcolor







import math


def redondear(numero):
    return math.ceil(numero*100)/100


def show_ratio_pie_chart(ratio_sust_1,ratio_sust_2,ratio_sust_3) -> rx.Component:
    # Prepara los datos del gráfico
    data = [
        {"name": "Pensión pública", "value": redondear(ratio_sust_1), "fill": "#00FF7F"},
        {"name":"Pensión de empresa","value":redondear(ratio_sust_2),"fill":"#FFA500"},
        {"name":"Pensión privada","value":redondear(ratio_sust_3),"fill":"#00D0FF"},
        {"name": "Salario", "value": redondear(100 - ratio_sust_1 - ratio_sust_2 - ratio_sust_3), "fill": "#D3D3D3"},
    ]
    
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.heading("Ratio de Sustitución", size="4", color="black", aria_label="Ratio de Sustitución"),
                info_button(color="silver",info="El ratio de sustitución es el porcentaje de tu salario medio que representa la pensión."),
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
            rx.text(f"{redondear(ratio_sust_1 + ratio_sust_2 + ratio_sust_3)}% de cobertura", color="black", font_size="1.5em", text_align="center",margin="-.5em .05em"),
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

def show_pension_salary_comparison3(pension_primer_pilar:float, pension_segundo_pilar:float,pension_tercer_pilar:float,salario_actual:float) -> rx.Component:

    data = [
        {"name": "Comparación", "Pensión pública": pension_primer_pilar, "Pensión de empresa": pension_segundo_pilar, "Pensión privada": pension_tercer_pilar,"Salario": salario_actual},
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
            data_key="Pensión privada",
            stroke=legcolor.LEGEND_1_2.value,
            fill=legcolor.LEGEND_1_2.value,
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



def final_results() -> rx.Component:

    # Salario
    salario_actual = FormState.salario_medio
    salario_mensual = redondear(salario_actual/12)

    # 1er pilar
    pension_primer_pilar = GlobalState.pension_primer_pilar
    pension_1p_anual = GlobalState.pension_anual_primer
    ratio_sust_1 = GlobalState.ratio_sustitucion_primer

    # 2o pilar
    pension_segundo_pilar = GlobalState.pension_segundo_pilar
    pension_2p_anual = GlobalState.pension_anual_segundo
    ratio_sust_2 = GlobalState.ratio_sustitucion_segundo
    
    # 3er pilar
    pension_tercer_pilar = GlobalState.pension_tercer_pilar.to(float)
    pension_3p_anual = redondear(pension_tercer_pilar) * 12
    ratio_sust_3 = GlobalState.ratio_sustitucion_tercer
    
    ratio_total = GlobalState.ratio_sustitucion_total
    
    ratio_gt_100_component = rx.box(
        rx.vstack(
            rx.text(f"Tu pensión es {ratio_total.to(rx.Var[float])- 100} % superior al salario.",
                   color="black",
                   text_align="center",
                   width="90%"),
            show_pension_salary_comparison3(pension_primer_pilar, pension_segundo_pilar, pension_tercer_pilar, salario_mensual),
            leyenda3(pension_is_gt_salary=True),
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
        padding_top="2em",
        padding_bottom="4em"
    )

    ratio_lte_100_component = rx.box(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Pensión mensual:", size="4", color="black"),
                        rx.text(f"{redondear(pension_primer_pilar + pension_segundo_pilar + pension_tercer_pilar)} € / mes", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.heading("Pensión anual:", size="4", color="black"),
                        rx.text(f"{redondear(pension_1p_anual + pension_2p_anual + pension_3p_anual)} € / año", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    width="50%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.heading("Salario mensual:", size="4", color="black"),
                        rx.text(f"{redondear(salario_mensual):.2f} € / mes", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.heading("Salario anual:", size="4", color="black"),
                        rx.text(f"{redondear(salario_actual):.2f} € / año", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    width="50%",
                ),
                display="flex",
                flex_direction=["column", "row"],
                justify="between",
                width="100%",
                gap="4",
            ),
            show_ratio_pie_chart(ratio_sust_1, ratio_sust_2,ratio_sust_3),
            leyenda3(),
            align_items="center",
            justify_content="center",
            padding="1.5em",
            border_radius="md",
            box_shadow="lg",
            background_color="white",
            width="90%",
            max_width="1200px",
            margin="2em auto",
            spacing="4"
        ),
        width="100%",
        display="flex",
        justify_content="center",
        margin_bottom=rx.breakpoints(initial='4em', sm='5em',md='6em',lg='7em'),
    )

    
    return rx.cond(
        ratio_total > 100,
        ratio_gt_100_component,
        ratio_lte_100_component
    )