import reflex as rx
from tfg_app.styles.colors import TextColor as txcolor
from tfg_app.styles.styles import Size as size
from tfg_app.styles.fonts import Font
from tfg_app.components.input_text import input_text
from reflex_calendar.calendar import calendar

class FormState(rx.State):
    form_data: dict = {}

    def handle_submit(self, form_data: dict):
        """Handle the form submit."""
        self.form_data = form_data

def form_example():
    return rx.form(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        calendar(),
                        input_text("Edad deseada de jubilación","65"),
                        rx.input(
                            placeholder="Last Name",
                            name="last_name",
                        )
                    ),
                ),
                #rx.hstack(
                 #   rx.checkbox("Checked", name="check"),
                  #  rx.switch("Switched", name="switch"),
                #),
                rx.button("Submit", type="submit"),
            ),
            on_submit=FormState.handle_submit,
            reset_on_submit=True,
        )

def header():
    return rx.vstack(
        rx.vstack(
            rx.heading(
                "Simulador de pensiones",
                color = "white",
                font_family = Font.TITLE.value,
                font_size = size.BIG.value,
                font_weight = "bold",
                margin_top = size.SMALL.value
            ),
            form_example(),
            
        ),
    )
