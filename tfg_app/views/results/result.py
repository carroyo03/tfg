import reflex as rx


from tfg_app.global_state import GlobalState
from tfg_app.styles.fonts import Font
from tfg_app.styles.styles import Size as size
from tfg_app.backend.pens import calcular_ratio_sustitucion
from tfg_app.views.pilar1.pilar1form import FormState
from tfg_app.components.info_button import info_button






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
                info_button("El ratio de sustitución es el porcentaje de tu salario medio que representa la pensión."),
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
                height=250,
            ),
            rx.text(f"{ratio_sust_1 + ratio_sust_2 + ratio_sust_3:.2f}% de cobertura", color="black", font_size="1.5em", text_align="center"),
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
        spacing="1"

    )





def final_results() -> rx.Component:

    # Salario
    salario_actual = FormState.form_data['salario_medio'].to(float)
    salario_mensual = redondear(salario_actual/12)

    # 1er pilar
    pension_primer_pilar = GlobalState.pension_primer_pilar.to(float)
    pension_1p_anual = redondear(pension_primer_pilar) * 12
    ratio_sust_1 = calcular_ratio_sustitucion(pension_primer_pilar, salario_actual)

    # 2o pilar
    pension_segundo_pilar = GlobalState.pension_segundo_pilar.to(float)
    pension_2p_anual = redondear(pension_segundo_pilar) * 12
    ratio_sust_2 = calcular_ratio_sustitucion(pension_segundo_pilar, salario_actual)
    
    # 3er pilar
    pension_tercer_pilar = GlobalState.pension_tercer_pilar.to(float)
    pension_3p_anual = redondear(pension_tercer_pilar) * 12
    ratio_sust_3 = calcular_ratio_sustitucion(pension_tercer_pilar, salario_actual)
    
    
    return rx.center(
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
                        rx.text(f"{redondear(pension_1p_anual + pension_2p_anual +pension_3p_anual)} € / año", color="black"),
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
                flex_direction="row",
                justify="between",
                width="100%",
            ),
            show_ratio_pie_chart(ratio_sust_1, ratio_sust_2,ratio_sust_3),
            align_items="center",
            justify_content="center",
            padding="1em",
            border_radius="4%",
            box_shadow="lg",
            background_color="white",
            width="100%",
            max_width="600px",  # Limita el ancho máximo
            margin_top="2em",
            margin_bottom="2em",
            height="auto",  # Cambiado de 70% a auto para mejor responsividad
        ),
        height="100vh",  # Asegura que el contenedor ocupe toda la altura de la pantalla
        width="100%",
    )