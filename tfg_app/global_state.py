import reflex as rx
from reflex.state import State

class GlobalState(State):
    pension_primer_pilar: float = 0

    @rx.event
    def set_pension_primer_pilar(self, pension: float):
        self.pension_primer_pilar = pension
    
    @rx.event
    def get_pension_primer_pilar(self):
        return self.pension_primer_pilar