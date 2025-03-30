import reflex as rx
from tfg_app.styles.fonts import Font
from tfg_app.components.info_button import info_button



class StartAgeState(rx.State):
    value: str = ""

    @rx.var
    def invalid_value(self) -> bool:
        if not self.empty_value:
            v = int(self.value)
            return v < 16 or v > 67
        return False
    @rx.var
    def empty_value(self) -> bool:
        return self.value == ""

    def set_value(self, value: str):
        print(f"Estableciendo edad: {value}")
        self.value = value
    @rx.event
    async def reset_values(self):
        print("Restableciendo edad")
        self.value = ""

class AgeState(rx.State):
    value: str = ""

    @rx.var
    def empty_value(self) -> bool:
        return self.value == ""
    
    @rx.var
    def invalid_value(self) -> bool:
        if not self.empty_value:
            try:
                v = int(self.value)
                # Debug the validation
                print(f"Validating retirement age: {v}")
                # Check if the age is within a reasonable range for retirement
                # In Spain, typical retirement ages are between 60-70
                return v < 60 or v > 75
            except ValueError:
                print(f"Invalid retirement age format: {self.value}")
                return True
        return False
    
    def set_value(self, value: str):
        print(f"Estableciendo edad: {value}")
        self.value = value
    
    @rx.event
    async def reset_values(self):
        print("Restableciendo edad")
        self.value = ""

class AvgSalaryState(rx.State):
    value = ""

    @rx.var
    def invalid_value(self) -> bool:
        if not self.empty_value:
            try:
                v = float(self.value)
                return v < 0
            except:
                return True
        return False

    @rx.var
    def empty_value(self) -> bool:
        return self.value == ""

    def set_value(self, value):
        print(f"Estableciendo salario medio: {value}")
        self.value = str(value)
        
    @rx.event
    async def reset_values(self):
        print("Restableciendo salario medio")
        self.set_value("")

def input_text(title: str, name:str, state:rx.State, type_: str,has_info_button:bool=False, info:str="", color_info_button:str="") -> rx.Component:
    return rx.vstack(
        rx.form.field(
            rx.cond(
                not has_info_button and info == "" and color_info_button == "",
                c1 = rx.text(
                    title,
                    color="white",
                    margin_bottom="0.5em"
                ),
                c2 = rx.hstack(
                    rx.text(
                        title,
                        color="white",
                        margin_bottom="0.5em",
                        margin_top="0.5em" 
                    ),
                    info_button(info=info, color=color_info_button),
                    align_items="center",
                    justify_content="flex-start",
                    width="100%"
                )
            ),
            rx.form.control(
                rx.input(
                    type=type_,
                    on_change=state.set_value,
                    name=name,
                    placeholder=title,
                    width="100%",
                    size="2",
                    border_radius="md",
                    debounce=300
                ),
                as_child=True,
            ),
            rx.form.message(
                f"Introduce {title.lower()} valido.",
                match="valueMissing",
                force_match=state.invalid_value if hasattr(state, "invalid_value") else False,
                color="var(--danger)",
            ),
            font_family=Font.DEFAULT.value,
            width="100%",
            align_items="flex-start"
        ),
        width="100%",
    )