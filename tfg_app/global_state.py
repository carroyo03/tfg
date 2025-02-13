import reflex as rx

class GlobalState(rx.State):
    pension_primer_pilar: float = 0
    pension_segundo_pilar: float = 0
    
    def set_pension_primer_pilar(self, pension: float):
        self.pension_primer_pilar = pension
    
    def get_pension_primer_pilar(self) -> float:
        return round(self.pension_primer_pilar.to(float),2)
    
    def set_pension_segundo_pilar(self, pension: float):
        self.pension_segundo_pilar = pension
    
    def get_pension_segundo_pilar(self) -> float:
        return round(self.pension_segundo_pilar.to(float),2)