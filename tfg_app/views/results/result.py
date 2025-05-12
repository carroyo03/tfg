from ast import Try
import reflex as rx

from tfg_app.backend.cache import CacheState
from tfg_app.components.leyenda import leyenda3
from tfg_app.global_state import GlobalState
from tfg_app.backend.pens import RatioSust1, RatioSust2, RatioSust3
from tfg_app.views.login.login_form import AppState
from tfg_app.views.pilar1.pilar1form import FormState
from tfg_app.views.pilar3.pilar3form import Form3State
from tfg_app.components.info_button import info_button
from tfg_app.styles.colors import LegendColor as legcolor
import math


def redondear(numero):
    return math.ceil(numero*100)/100

TOOLTIP_PROPS = {
    "separator": "",
    "cursor": False,
    "is_animation_active": False,
    "label_style": {"fontWeight": "500"},
    "item_style": {
        "color": "currentColor",
        "display": "flex",
        "paddingBottom": "0px",
        "justifyContent": "space-between",
        "textTransform": "capitalize",
    },
    "content_style": {
        "borderRadius": "5px",
        "boxShadow": "0px 24px 12px 0px light-dark(rgba(28, 32, 36, 0.02), rgba(0, 0, 0, 0.00)), 0px 8px 8px 0px light-dark(rgba(28, 32, 36, 0.02), rgba(0, 0, 0, 0.00)), 0px 2px 6px 0px light-dark(rgba(28, 32, 36, 0.02), rgba(0, 0, 0, 0.00))",
        "fontFamily": "var(--font-instrument-sans)",
        "fontSize": "0.875rem",
        "lineHeight": "1.25rem",
        "fontWeight": "500",
        "letterSpacing": "-0.01rem",
        "minWidth": "8rem",
        "width": "200px",
        "padding": "0.375rem 0.625rem",
        "position": "relative",
        "background": rx.color("gray", 1),
        "borderColor": rx.color("gray", 4),
    },
}



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
                info_button(color="black",info="El ratio de sustitución es el porcentaje de tu salario medio que representa la pensión."),
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

def show_pension_salary_comparison3(pension_primer_pilar:float, pension_segundo_pilar:float,pension_tercer_pilar:float,salario_anual:float) -> rx.Component:
    v1 = pension_primer_pilar
    v2 = pension_segundo_pilar
    v3 = pension_tercer_pilar
    v4 = salario_anual
    data = [
        {"name": "Pensión pública", "valor": round(v1,2), "fill": legcolor.LEGEND_1.value},
        {'name': "Pensión de empresa", "valor": round(v2,2), "fill": legcolor.LEGEND_1_1.value},
        {'name': "Pensión privada", "valor": round(v3,2), "fill": legcolor.LEGEND_1_2.value},
        {'name': 'Pensión total', 'valor': round(v1 + v2 + v3,2), "fill": legcolor.LEGEND_3.value},
        {'name': 'Salario', "valor": round(v4, 2), 'fill': legcolor.LEGEND_2.value},  # Data for the salary bar group
    ]
    return rx.recharts.bar_chart(
        rx.recharts.cartesian_grid(),
        rx.recharts.bar(
            data_key="valor",
            fill="fill",
            stroke='fill'
        ),
        rx.recharts.x_axis(
            data_key="name",
            hide = True
        ),
        rx.recharts.y_axis(),
        rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
        data=data,
        width='100%',
        height=300,
    )



def final_results() -> rx.Component:
    if AppState.signed_in is True and AppState.user_info.get('email'):
        user_email = AppState.user_info.get('email')
        cached_results = CacheState.get_cache_results(user_email)

    else:
        cached_results = CacheState.get_cache_results()
    if cached_results:
        print("Using cached results")
        salario_mensual = cached_results['salario_mensual_neto_pilar3']
        salario_anual = cached_results['salario_mensual_neto_pilar3'] * 12
        pension_primer_pilar = cached_results['pension_primer_pilar']
        pension_1p_anual = cached_results['pension_anual_primer']
        ratio_sust_1 = cached_results['pension_anual_primer'] / salario_anual * 100
        pension_segundo_pilar = cached_results['pension_segundo_pilar']
        pension_2p_anual = cached_results['pension_anual_segundo']
        ratio_sust_2 = cached_results['pension_anual_segundo'] / salario_anual * 100
        pension_tercer_pilar = cached_results['pension_tercer_pilar'].to(float)
        pension_3p_anual = redondear(pension_tercer_pilar) * 12
        ratio_sust_3 = cached_results['pension_tercer_pilar'].to(float) / salario_anual * 100
        pension_mensual_total = pension_primer_pilar + pension_segundo_pilar + pension_tercer_pilar
        pension_anual_total = pension_1p_anual + pension_2p_anual + pension_3p_anual
        ratio_total = ratio_sust_1 + ratio_sust_2 + ratio_sust_3
    else:
        # Salario
        salario_mensual = GlobalState.salario_mensual_neto_pilar3
        salario_anual = salario_mensual * 12

        # 1er pilar
        pension_primer_pilar = GlobalState.pension_primer_pilar
        pension_1p_anual = GlobalState.pension_anual_primer
        try:
            ratio_sust_1 = pension_1p_anual / salario_anual * 100
        except Exception:
            ratio_sust_1 = 0

        # 2o pilar
        pension_segundo_pilar = GlobalState.pension_segundo_pilar
        pension_2p_anual = GlobalState.pension_anual_segundo
        try:
            ratio_sust_2 = pension_2p_anual / salario_anual * 100
        except Exception:
            ratio_sust_2 = 0


        # 3er pilar
        pension_tercer_pilar = GlobalState.pension_tercer_pilar.to(float)
        pension_3p_anual = redondear(pension_tercer_pilar) * 12

        try:
            ratio_sust_3 = pension_3p_anual / salario_anual * 100
        except Exception:
            ratio_sust_3 = 0
        # total
        pension_mensual_total = pension_primer_pilar + pension_segundo_pilar + pension_tercer_pilar
        pension_anual_total = pension_1p_anual + pension_2p_anual + pension_3p_anual
        ratio_total = ratio_sust_1 + ratio_sust_2 + ratio_sust_3

        results_to_cache = {
            'salario_mensual_neto_pilar3': salario_mensual,
            'salario_anual': salario_anual,
            'pension_primer_pilar': pension_primer_pilar,
            'pension_1p_anual': pension_1p_anual,
            'pension_segundo_pilar': pension_segundo_pilar,
            'pension_2p_anual': pension_2p_anual,
            'pension_tercer_pilar': pension_tercer_pilar,
            'pension_3p_anual': pension_3p_anual,
            'pension_mensual_total': pension_mensual_total,
            'pension_anual_total': pension_anual_total,
            'ratio_sust_1': ratio_sust_1,
            'ratio_sust_2': ratio_sust_2,
            'ratio_sust_3': ratio_sust_3,
            'ratio_total': ratio_total
        }

        CacheState.cache_results(results_to_cache)



    ratio_gt_100_component = rx.box(
        rx.vstack(
            rx.text(f"Tu pensión es {(ratio_total.to(rx.Var[float])- 100):.2f} % superior al salario neto, tras considerar las aportaciones al plan de empresa y privado.",
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
        padding_bottom="4em"
    )

    ratio_lte_100_component = rx.box(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Pensión mensual:", size="4", color="black"),
                        rx.text(f"{redondear(pension_mensual_total)} € / mes", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.heading("Pensión anual:", size="4", color="black"),
                        rx.text(f"{redondear(pension_anual_total)} € / año", color="black"),
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
                        rx.text(f"{redondear(salario_anual):.2f} € / año", color="black"),
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
    # total
    pension_mensual_total = pension_primer_pilar + pension_segundo_pilar + pension_tercer_pilar
    pension_anual_total = pension_1p_anual + pension_2p_anual + pension_3p_anual
    ratio_total = ratio_sust_1 + ratio_sust_2 + ratio_sust_3


    
    ratio_gt_100_component = rx.box(
        rx.vstack(
            rx.text(f"Tu pensión es {(ratio_total.to(rx.Var[float])- 100):.2f} % superior al salario neto, tras considerar las aportaciones al plan de empresa y privado.",
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
        padding_bottom="4em"
    )

    ratio_lte_100_component = rx.box(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Pensión mensual:", size="4", color="black"),
                        rx.text(f"{redondear(pension_mensual_total)} € / mes", color="black"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.heading("Pensión anual:", size="4", color="black"),
                        rx.text(f"{redondear(pension_anual_total)} € / año", color="black"),
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
                        rx.text(f"{redondear(salario_anual):.2f} € / año", color="black"),
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