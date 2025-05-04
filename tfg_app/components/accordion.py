import reflex as rx #type:ignore

from tfg_app.styles import colors


# Componente reutilizable para el acordeón de resultados

def responsive_results_accordion(title, results_component, is_mobile=False):
    """
    Create a responsive accordion component for displaying results.
    Args:
        title: The title of the accordion.
        results_component: The component to display inside the accordion.
        is_mobile: Boolean indicating if the view is mobile or not.
    Returns:
        A responsive accordion component.
    """


    # Estilos comunes para el acordeón

    accordion_styles = {

        "width": "100%",

        "border-radius": "8px",

        "overflow": "hidden",

        "box-shadow": "0 2px 10px rgba(0, 0, 0, 0.1)",

    }

    # Estilos para el header del acordeón

    header_styles = {

        "background-color": "#4285F4",  # Color azul que coincide con tus capturas

        "color": "white",

        "font-weight": "bold",

        "padding": rx.breakpoints(

            initial="0.75rem 1rem",

            sm="0.75rem 1.25rem",

            md="0.75rem 1.5rem"

        ),

        "align-items": "center",

        "justify-content": "space-between",

        "border-radius": "8px 8px 0 0",

    }

    # Estilos para el contenido del acordeón

    content_styles = {
        "background-color": "white",
        "padding": '0',
        "margin": "0",
        "border-radius": "0 0 8px 8px",
        "overflow": "hidden",
    }

    # Contenedor para asegurar dimensiones consistentes

    content_container_styles = {

        "width": "100%",

        "max-width": "100%",

        "padding": rx.breakpoints(

            initial="0",

            sm="0",

            md="0"

        ),

        "margin": "0 auto",

        "overflow": "hidden",
        
        "align-items": "flex-start",
        

    }

    # Ajustes específicos para móvil o escritorio

    if is_mobile:

        accordion_styles["max_width"] = "100%"

        content_container_styles["max_width"] = "100%"

    else:

        accordion_styles["max_width"] = rx.breakpoints(

            initial="100%",

            sm="95%",

            md="90%"

        )

        content_container_styles["max_width"] = "100%"

    return rx.accordion.root(

        rx.accordion.item(

            header=rx.text(

                title,

                color="white",

                font_weight="bold",

            ),

            content=rx.container(

                rx.box(

                    results_component,

                    width="100%",

                    padding="1rem",

                    margin="0",

                    overflow_x="hidden",

                    background_color="white",
                    
                    justify_content="center",
                    

                ),

                **content_container_styles,
                align="center",

            ),

            width="100%",

        ),

        collapsible=True,

        style=accordion_styles,

        header_style=header_styles,

        content_style=content_styles,

    )