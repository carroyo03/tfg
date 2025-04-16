import datetime

import reflex as rx
import logging
from tfg_app.styles.styles import Size as size

class DateState(rx.State):

    # Value ranges for the date
    day_values: list[str] = [str(i) for i in range(1, 32)]
    month_values: list[str] = [str(i) for i in range(1, 13)]
    year_values: list[str] = [str(i) for i in range(2005,1950,-1)]

    # Default values for the date
    day: str = ""
    month: str = ""
    year: str = ""
    date: str = ""

    @rx.var
    def invalid_value(self) -> bool:
        return self.day == "" or self.month == "" or self.year == "" or datetime.datetime.strptime(self.date, "%d/%m/%Y") is None


    def update_date(self):
        self.date = f"{self.day}/{self.month}/{self.year}"
        logging.info(f"Fecha actualizada: {self.date}")

    def set_day(self, day: str):
        self.day = day
        self.update_date()


    def set_month(self, month: str):
        self.month = month
        self.update_date()
    
    def set_year(self, year: str):
        self.year = year
        self.update_date()

    @rx.event
    async def reset_values(self):
        self.day = ""
        self.month = ""
        self.year = ""
        self.update_date()

def date_picker(text: str) -> rx.Component:
    return rx.vstack(
        rx.text(text, color="white", margin_bottom="0.5em", font_size=rx.breakpoints(initial=size.DEFAULT.value, sm=size.LARGE.value, md=size.BIG.value)),
        rx.hstack(
                rx.select(
                    DateState.day_values,
                    placeholder="Día",
                    on_change=DateState.set_day,
                    name="day",
                    width="29%",
                    color="black"
                ),
                rx.select(
                    DateState.month_values,
                    placeholder="Mes",
                    on_change=DateState.set_month,
                    name="month",
                    width="29%",
                    color="black"
                ),
                rx.select(
                    DateState.year_values,
                    placeholder="Año",
                    on_change=DateState.set_year,
                    name="year",
                    width="29%",
                    color="black"
                ),
                spacing="5",
                width="100%"
            ),
            width="100%",
            align_items="flex-start",
    )