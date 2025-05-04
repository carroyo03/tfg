import reflex as rx

class GlobalState(rx.State):
    form_data_primer_pilar: dict = {}
    form_data_segundo_pilar: dict = {}
    form_data_tercer_pilar: dict = {}
    pension_primer_pilar: float = 0.0
    pension_segundo_pilar: float = 0.0
    pension_tercer_pilar: float = 0.0

    def set_pension(self, n_pilar: str, pension: float):
        if n_pilar in ("primer", "segundo", "tercer"):
            setattr(self, f"pension_{n_pilar}_pilar", pension)
        else:
            raise ValueError("El pilar debe ser 'primer', 'segundo' o 'tercer'.")

    def get_pension(self, n_pilar: str) -> float:
        if n_pilar in ("primer", "segundo", "tercer"):
            value = getattr(self, f"pension_{n_pilar}_pilar")
            # Check if value is already a float or needs conversion
            if isinstance(value, float):
                return round(value, 2)
            else:
                # It's a Var object, convert it to float
                return round(value.to(float), 2)
        else:
            raise ValueError("El pilar debe ser 'primer', 'segundo' o 'tercer'.")
    
    def set_form_data(self, n_pilar: str, form_data: dict):
        if n_pilar in ("primer", "segundo", "tercer"):
            setattr(self, f"form_data_{n_pilar}_pilar", form_data)
        else:
            raise ValueError("El pilar debe ser 'primer', 'segundo' o 'tercer'.")
