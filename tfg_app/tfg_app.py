import reflex as rx

from tfg_app.components.logout_button import logout_button
from tfg_app.views.pilar1.pilar1form import form1
from tfg_app.views.pilar2.pilar2form import form2
from tfg_app.styles import colors
from tfg_app.styles.fonts import Font
from tfg_app.backend.main import fastapi_app
from tfg_app.views.pilar3.pilar3form import form3, Form3State
from tfg_app.views.results.result import final_results
from tfg_app.views.pilar1.pilar1results import results_pilar1
from tfg_app.views.pilar2.pilar2results import results_pilar2
from tfg_app.styles.styles import Size as size
from tfg_app.views.login.login_form import AppState, sign_in_v1
from tfg_app.styles.styles import BASE_STYLE
from tfg_app.components.accordion import responsive_results_accordion


def loading():
    return rx.center(
        rx.spinner(size="3"),
        padding=["5em", "8em", "10em"],
        height="auto",
        color="white"
    )


@rx.page("/sign-in")
def sign_in():
    return sign_in_v1()


@rx.page("/authorize")
def authorize():
    code = AppState.router.page.params.get("code")
    state = AppState.router.page.params.get("state")
    print(f"Authorize route - Code: {code}, State: {state}")
    return rx.cond(
        code is None or state is None,
        sign_in_v1(),
        rx.vstack(
            rx.text(
                "Autenticando...",
                font_size=["1em", "1.2em", "1.5em"],
                color="white",
            ),
            loading(),
            on_mount=lambda: AppState.handle_authorize(code, state),
            width="100%",
            height="auto",
            align="center",
            justify="center",
            padding=["2em", "3em", "4em"]
        )
    )


@rx.page("/logout")
def logout():
    return rx.vstack(
        rx.text(
            "Cerrando sesión...",
            font_size=["1em", "1.2em", "1.5em"]
        ),
        loading(),
        on_mount=AppState.logout(),
        width="100%",
        height="auto",
        align="center",
        justify="center",
        padding=["2em", "3em", "4em"]
    )


@rx.page("/")
def form_pilar1():
    return rx.cond(
        AppState.signed_in | AppState.guest,
        rx.cond(
            rx.State.is_hydrated,
            rx.vstack(
                rx.vstack(
                    rx.hstack(
                        rx.heading(
                            "Simulador de pensiones",
                            color="white",
                            font_family=Font.TITLE.value,
                            font_size=rx.breakpoints(initial=size.LARGE.value, sm=size.BIG.value,
                                                     md=size.REALLY_BIG.value),
                            font_weight="bold",
                            margin_top=size.SMALL.value,
                            align="center",
                            width="100%",
                        ),
                        rx.cond(
                            AppState.signed_in,
                            logout_button(),
                        ),
                        align_items="center",
                    ),
                    form1(),
                    align="center",
                    padding_bottom="2rem",
                    height="auto",
                    overflow_y="auto",  # Permitir desplazamiento en el contenedor padre
                ),
                width="100%",
                max_width=["100%", "90%", "80%", "70%"],
                height="auto",
                spacing="1",
                align_items="center",
            ),
            loading(),
        ),
        sign_in_v1(),
    )


@rx.page("/pilar1")  # ,on_load=AuthState.on_load)
def pilar1():
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.heading(
                    "Plan Público de Pensiones",
                    color="white",
                    font_family=Font.TITLE.value,
                    font_size=rx.breakpoints(initial=size.BIG.value, sm=size.REALLY_BIG.value, md=size.SMALL.value),
                    font_weight="bold",
                    text_align="center",
                    width="100%",
                    padding_top=rx.breakpoints(initial="1.5rem", sm="2rem", md="3rem"),
                    margin_bottom=rx.breakpoints(initial="2rem", sm="3rem", md="4rem")
                ),
                rx.cond(
                    AppState.signed_in,
                    logout_button(),
                ),
                align="center"
            ),
            position="sticky",
            top="0",
            z_index="1",
            align="center"
            # ackground_color="rgba(0, 51, 141, 0.9)",  # Azul semi-transparente
            # backdrop_filter="blur(5px)",
        ),
        rx.box(
            results_pilar1(),
            width="100%",
            max_width=["95%", "90%", "85%", "800px"],  # Más anchura en móvil
            margin="0 auto",  # Centrar horizontalmente
            margin_top=["0rem", "-2rem", "-3rem"],  # Reducir márgenes negativos en móvil
            margin_bottom=rx.breakpoints(initial=".5rem", xs="2rem", sm="2rem", md="2rem", lg="4rem"),
            padding_x=rx.breakpoints(initial="1em", sm="1em", md="1em"),  # Mantener padding consistente
        ),
        rx.mobile_only(  # Sticky footer para botones en móvil
            rx.box(
                rx.center(
                    rx.button(
                        "Atrás",
                        on_click=rx.redirect("/"),
                        color="white",
                        background_color="transparent",
                        border="1px solid",
                        box_shadow="0 .25rem .375rem #0003",
                        width=rx.breakpoints(initial="80%", sm="70%", md="60%"),
                        height="auto",
                        font_size=["0.9em", "1em", "1.1em"],  # Responsive font size
                    ),
                    rx.button(
                        "Siguiente",
                        on_click=rx.redirect("/form2"),
                        background_color="white",
                        color=colors.Color.BACKGROUND.value,
                        border="1px solid",
                        box_shadow="0 .25rem .375rem #0003",
                        width=rx.breakpoints(initial="80%", sm="70%", md="60%"),
                        height="auto",
                        font_size=["0.9em", "1em", "1.1em"],  # Responsive font size
                        margin_bottom="5%",
                    ),
                    width="100%",
                    spacing="2",
                    align="center",
                    justify="center",
                    display="flex",
                    direction="column",
                ),
                position="fixed",
                bottom="0",
                width="100%",
                background_color="rgba(0, 51, 141, 0.9)",
                # padding_y="1rem",
                z_index="10",
            ),
        ),
        rx.tablet_and_desktop(  # Botones en su lugar original para tablet/escritorio
            rx.center(
                rx.button(
                    "Atrás",
                    on_click=rx.redirect("/"),
                    color="white",
                    background_color="transparent",
                    border="1px solid",
                    box_shadow="0 .25rem .375rem #0003",
                    width=["40%", "30%", "20%"],
                    height="auto",
                    font_size=["0.9em", "1em", "1.1em"],
                ),
                rx.button(
                    "Siguiente",
                    on_click=rx.redirect("/form2"),
                    background_color="white",
                    color=colors.Color.BACKGROUND.value,
                    border="1px solid",
                    box_shadow="0 .25rem .375rem #0003",
                    width=["40%", "30%", "20%"],
                    height="auto",
                    font_size=["0.9em", "1em", "1.1em"],
                ),
                width="100%",
                margin_top=["-6rem", "-7rem", "-8rem"],  # Responsive margin
                spacing="2",
                align="center",
                justify="center",
            ),
        ),
        width="100%",
        min_height=["auto", "80vh", "100vh"],  # Responsive min-height
        spacing="1",
        align_items="stretch",
        background_color="#00338D",
        overflow_y="auto"
    )


@rx.page("/form2")
def form_pilar2():
    return rx.cond(
        AppState.signed_in | AppState.guest,
        rx.cond(
            rx.State.is_hydrated,
            rx.vstack(
                rx.mobile_only(
                    rx.vstack(
                        rx.button(
                            rx.hstack(
                                rx.icon("arrow-left", color="white", size=16),
                                "Atrás",
                                spacing="2"
                            ),
                            on_click=rx.redirect("/pilar1"),
                            color="white",
                            background_color="transparent",
                            border="1px solid",
                            box_shadow="0 .25rem .375rem #0003",
                            width="auto",
                            height="auto",
                            position="sticky",
                            top="1rem",
                            left="1rem",
                            font_size=["0.9em", "1em", "1.1em"],
                            _hover={"bg": colors.Color.SECONDARY.value, "color": "white"},
                            z_index="10",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.box(
                                    rx.heading(
                                        "Pensión de empresa",
                                        color="white",
                                        font_family=Font.TITLE.value,
                                        font_size=rx.breakpoints(initial="1.5em", sm="1.8em", md="2.2em"),
                                        font_weight="bold",
                                        margin_top=size.SMALL.value,
                                        margin_bottom=size.SMALL.value,
                                        text_align="center",  # Centra el texto
                                    ),
                                    responsive_results_accordion("Resultados de la pensión pública", results_component=results_pilar1(direction="row"), is_mobile=True),
                                    width="100%",
                                    padding_x="0.5rem",
                                    margin_top="1em",
                                    justify="center"
                                ),
                                form2(is_mobile=True),
                                overflow="hidden",
                                align="end",
                                padding=["0.5em", "0.8em", "1em"],
                                height="auto",
                                width="100%",
                                justify='end'
                            ),
                            width=["100%", "90%", "50%"],
                            max_width=["100%", "90%", "80%", "70%"],
                            height="auto",
                            spacing="1",
                            align_items="flex-end",
                            justify_content="center",
                        ),
                        rx.cond(AppState.signed_in, logout_button()),
                    ),
                ),
                rx.tablet_and_desktop(
                    rx.hstack(
                        rx.button(
                            rx.hstack(
                                rx.icon("arrow-left", color="white", size=16),
                                "Atrás",
                                spacing="2"
                            ),
                            on_click=rx.redirect("/pilar1"),
                            color="white",
                            background_color="transparent",
                            border="1px solid",
                            box_shadow="0 .25rem .375rem #0003",
                            width="auto",
                            height="auto",
                            position="absolute",
                            top="1rem",
                            left="1rem",
                            font_size=["0.9em", "1em", "1.1em"],
                            _hover={"bg": colors.Color.SECONDARY.value, "color": "white"},
                        ),
                        rx.center(
                            rx.vstack(
                                rx.heading(
                                    "Pensión de empresa",
                                    color="white",
                                    font_family=Font.TITLE.value,
                                    font_size=rx.breakpoints(initial="1.2em", sm="1.5em", md="1.8em"),
                                    font_weight="bold",
                                    margin_top=size.SMALL.value,
                                    margin_bottom=size.SMALL.value,
                                    text_align="center",
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.box(
                                        responsive_results_accordion(title="Resultados de la pensión pública", results_component=results_pilar1(), is_mobile=False),
                                        width='100%',
                                        min_width="450px",
                                        #padding="-8rem",
                                        align="flex-start",
                                        justify="center",
                                        height="auto",
                                    ),
                                    rx.box(
                                        form2(),
                                        width="100%",
                                        # Responsive width that decreases as screen size increases
                                        min_width="300px",  # Ensure form has minimum width
                                    ),
                                    width="100%",
                                    max_width="100%",
                                    spacing="3",  # Responsive spacing
                                    display="flex",
                                    align_items="flex-start",
                                    justify="between",  # Better space distribution
                                    padding=["0.5rem", "1rem", "1.5rem"],
                                ),
                                width="100%",
                                align_items="center",
                                margin_left=["0%", "10%", "20%"],  # Desplaza a la derecha según el tamaño de pantalla
                            ),
                        ),
                        rx.cond(
                            AppState.signed_in,
                            rx.box(logout_button(), margin_right="1rem"),
                        ),
                        align_items="center",
                        width="100%",
                        justify_content="center",

                    )
                ),

                width="100%",
                max_width=["100%", "90%", "80%", "70%"],
                height="auto",
                justify="center"
            ),
            loading(),
        ),
        sign_in_v1(),
    )


@rx.page("/pilar2")
def pilar2():
    return rx.cond(
        AppState.signed_in | AppState.guest,
        rx.cond(
            rx.State.is_hydrated,
            rx.vstack(
                rx.cond(
                    AppState.signed_in,
                    logout_button(),
                ),
                rx.box(
                    rx.heading(
                        "Cálculo de pensión pública y de empresa",
                        color="white",
                        font_family=Font.TITLE.value,
                        font_size=rx.breakpoints(initial="1.5em", sm="2em", md="2.5em"),  # Responsive font size
                        font_weight="bold",
                        text_align="center",
                        width="100%",
                        padding_top=["1.5rem", "2rem", "3rem"],
                        margin_bottom='4rem'
                    ),
                    width="100%",
                    position="sticky",
                    top="0",
                    z_index="1",
                    #background_color="rgba(0, 51, 141, 0.9)",
                    #backdrop_filter="blur(5px)",
                ),
                rx.box(
                    results_pilar2(),
                    width="100%",
                    max_width=["100%", "90%", "85%", "800px"],
                    margin="0 auto",
                    margin_top=["-2.3rem", "-3.3rem", "-4.3rem"],
                    margin_bottom="4rem",
                    padding_x=["0.5rem", "0.8rem", "1rem"],
                ),
                rx.mobile_only(
                    rx.box(
                        rx.center(
                            rx.button(
                                "Atrás",
                                on_click=rx.redirect("/form2"),
                                color="white",
                                background_color="transparent",
                                border="1px solid",
                                box_shadow="0 .25rem .375rem #0003",
                                width=["40%", "30%", "20%"],
                                height="auto",
                                font_size=["0.9em", "1em", "1.1em"],
                            ),
                            rx.button(
                                "Siguiente",
                                on_click=rx.redirect("/form3"),
                                background_color="white",
                                color=colors.Color.BACKGROUND.value,
                                border="1px solid",
                                box_shadow="0 .25rem .375rem #0003",
                                width=["40%", "30%", "20%"],
                                height="auto",
                                font_size=["0.9em", "1em", "1.1em"],
                            ),
                            width="100%",
                            spacing="2",
                            align="center",
                            justify="center",
                        ),
                        position="sticky",
                        bottom="0",
                        width="100%",
                        background_color="rgba(0, 51, 141, 0.9)",
                        padding_y="1rem",
                        z_index="10",
                    ),
                ),
                rx.tablet_and_desktop(
                    rx.center(
                        rx.button(
                            "Atrás",
                            on_click=rx.redirect("/form2"),
                            color="white",
                            background_color="transparent",
                            border="1px solid",
                            box_shadow="0 .25rem .375rem #0003",
                            width=["40%", "30%", "20%"],
                            height="auto",
                            font_size=["0.9em", "1em", "1.1em"],
                        ),
                        rx.button(
                            "Siguiente",
                            on_click=rx.redirect("/form3"),
                            background_color="white",
                            color=colors.Color.BACKGROUND.value,
                            border="1px solid",
                            box_shadow="0 .25rem .375rem #0003",
                            width=["40%", "30%", "20%"],
                            height="auto",
                            font_size=["0.9em", "1em", "1.1em"],
                        ),
                        width="100%",
                        margin_top=["-5rem", "-6rem", "-7rem"],
                        spacing="2",
                        align="center",
                        justify="center",
                    ),
                ),
                width="100%",
                min_height=["auto", "80vh", "100vh"],
                spacing="0",
                align_items="stretch",
                background_color="#00338D",
            ),
            loading(),
        ),
        sign_in_v1()
    )


@rx.page("/form3")
def form_pilar3():
    return rx.cond(
        AppState.signed_in | AppState.guest,
        rx.cond(
            rx.State.is_hydrated,
            rx.vstack(
                rx.mobile_only(
                    rx.vstack(
                        rx.button(
                            rx.hstack(
                                rx.icon('arrow-left', color='white', size=16),
                                "Atrás",
                                spacing='2',
                            ),
                            on_click=rx.redirect("/pilar2"),
                            color="white",
                            background_color="transparent",
                            border="1px solid",
                            box_shadow="0 .25rem .375rem #0003",
                            width="auto",
                            height="auto",
                            position="sticky",
                            top="1rem",
                            left="1rem",
                            font_size=["0.9em", "1em", "1.1em"],
                            _hover={"bg": colors.Color.SECONDARY.value, "color": "white"},
                            z_index="10",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.box(
                                    rx.heading(
                                        "Pensión privada",
                                        color="white",
                                        font_family=Font.TITLE.value,
                                        font_size=rx.breakpoints(initial="1.5em", sm="1.8em", md="2.2em"),
                                        font_weight="bold",
                                        margin_top=size.SMALL.value,
                                        margin_bottom=size.SMALL.value,
                                        text_align="center",
                                    ),
                                    responsive_results_accordion("Resultados calculados hasta ahora", results_component=results_pilar2(direction='row'), is_mobile=True),
                                    width="100%",
                                    padding_x="0.5rem",
                                    margin_top="1em",
                                    justify="center"
                                ),
                                form3(is_mobile=True),
                                overflow='hidden',
                                align='end',
                                padding=['0.5em','0.8em', '1em'],
                                height='auto',
                                width='100%'
                            ),
                            width=["100%", "90%", "50%"],
                            max_width=["100%", "90%", "80%", "70%"],
                            height="auto",
                            spacing="1",
                            align_items="flex-end",
                            justify_content="center",
                        ),
                        rx.cond(AppState.signed_in, logout_button()),
                        justify='center'
                    )
                ),
                rx.tablet_and_desktop(
                    rx.hstack(
                        rx.button(
                            rx.hstack(
                                rx.icon('arrow-left', color='white', size = 16),
                                'Atrás',
                                spacing='2'
                            ),
                            on_click=rx.redirect('/pilar2'),
                            color='white',
                            background_color='transparent',
                            border='1px solid',
                            box_shadow="0 .25rem .375rem #0003",
                            width="auto",
                            height="auto",
                            position="absolute",
                            top="1rem",
                            left="1rem",
                            font_size=["0.9em", "1em", "1.1em"],
                            _hover={"bg": colors.Color.SECONDARY.value, "color": "white"},
                        ),
                        rx.center(
                            rx.vstack(
                                rx.heading(
                                    "Pensión privada",
                                    color="white",
                                    font_family=Font.TITLE.value,
                                    font_size=rx.breakpoints(initial="1.2em", sm="1.5em", md="1.8em"),
                                    font_weight="bold",
                                    margin_top=size.SMALL.value,
                                    margin_bottom=size.SMALL.value,
                                    text_align="center",
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.box(
                                        responsive_results_accordion(title='Resultados hasta ahora', results_component=results_pilar2(), is_mobile=False),
                                        width=["50%", "55%", "60%"],
                                        min_width="450px",
                                        #padding="-8rem",
                                        align="flex-start",
                                        justify="end",
                                        height="auto",
                                    ),
                                    rx.box(
                                        form3(),
                                        width='100%',
                                        # Responsive width that decreases as screen size increases
                                        min_width="300px",  # Ensure form has minimum width
                                    ),
                                    width="100%",
                                    max_width="100%",
                                    spacing="3",  # Responsive spacing
                                    display="flex",
                                    align_items="flex-start",
                                    justify="between",  # Better space distribution
                                    padding=["0.5rem", "1rem", "1.5rem"],
                                ),
                                width="100%",
                                align_items="center",
                                margin_left=["0%", "10%", "20%"],
                            ),
                        ),
                        rx.cond(
                            AppState.signed_in,
                            rx.box(logout_button(), margin_right='1rem')
                        ),
                        align_items="center",
                        width="100%",
                        justify_content="center",
                    )
                ),
                width="100%",
                max_width=["100%", "90%", "80%", "70%"],
                height="auto",
                justify="center"
            ),
            loading()
        ),
        sign_in_v1(),
    )


@rx.page("/results")
def result():
    return rx.cond(
        AppState.signed_in | AppState.guest,
        rx.cond(
            rx.State.is_hydrated,
            rx.vstack(
                rx.hstack(
                rx.cond(
                    AppState.signed_in,
                    logout_button(),
                ),
                rx.button(
                    rx.hstack(
                        rx.icon('arrow-left', color='white', size=16),
                        'Atrás',
                        spacing='2'
                    ),
                    on_click=rx.redirect("/form3"),
                    color='white',
                    background_color='transparent',
                    border='1px solid',
                    box_shadow="0 .25rem .375rem #0003",
                    width="auto",
                    height="auto",
                    position="relative",
                    top="1rem",
                    left="1rem",
                    font_size=["0.9em", "1em", "1.1em"],
                    _hover={"bg": colors.Color.SECONDARY.value, "color": "white"},
                ),
                rx.center(
                    rx.heading(
                        "Resultados",
                        color="white",
                        font_family=Font.TITLE.value,
                        font_size=rx.breakpoints(initial="1.5em", sm="2em", md="2.5em"),
                        font_weight="bold",
                        text_align="center",
                        width="100%",
                        padding_top=["1.5rem", "2rem", "3rem"],
                        margin_bottom='4rem',
                    ),
                    width="100%",
                    position="sticky",
                    top="0",
                    z_index="1",

                    #background_color="rgba(0, 51, 141, 0.9)",
                    #backdrop_filter="blur(5px)",
                ),
                ),
                rx.box(
                    rx.box(
                        final_results(),
                        width="100%",
                        max_width=["100%", "90%", "85%", "800px"],
                        margin="0 auto",
                        margin_top=["-2.3rem", "-3.3rem", "-4.3rem"],
                        margin_bottom='4rem',
                        padding_x=["0.5rem", "0.8rem", "1rem"],
                    ),
                ),
                width="100%",
                min_height=["auto", "80vh", "100vh"],
                spacing="0",
                align_items="stretch",
                background_color="#00338D",
            ),
            loading(),
        ),
        sign_in_v1(),
    )


app = rx.App(style=BASE_STYLE, stylesheets=[f"https://fonts.googleapis.com/css?family={font.value}" for font in Font if
                                            font != Font.TITLE.value])
app.add_page(sign_in)
app.add_page(authorize)
app.add_page(logout)
# app.add_page(check_email)
app.add_page(form_pilar1, on_load=AppState.check_session("/"))
app.api_transformer = fastapi_app
app.add_page(pilar1, on_load=AppState.check_session("/pilar1"))
app.add_page(form_pilar2, on_load=AppState.check_session("/form2"))
app.add_page(pilar2, on_load=AppState.check_session("/pilar2"))
app.add_page(form_pilar3, on_load=AppState.check_session("/form3"))
app.add_page(result, on_load=AppState.check_session("/results"))
