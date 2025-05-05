import reflex as rx

class GlobalState(rx.State):
    form_data_primer_pilar: dict = {}
    form_data_segundo_pilar: dict = {}
    form_data_tercer_pilar: dict = {}
    pension_primer_pilar: float = 0.0
    pension_segundo_pilar: float = 0.0
    pension_tercer_pilar: float = 0.0

    @rx.event
    def set_pension(self, n_pilar: str, pension: float):
        if n_pilar in ("primer", "segundo", "tercer"):
            setattr(self, f"pension_{n_pilar}_pilar", pension)
        else:
            raise ValueError("El pilar debe ser 'primer', 'segundo' o 'tercer'.")

    @rx.event
    def set_form_data(self, n_pilar: str, form_data: dict):
        if n_pilar in ("primer", "segundo", "tercer"):
            setattr(self, f"form_data_{n_pilar}_pilar", form_data.copy())
        else:
            raise ValueError("El pilar debe ser 'primer', 'segundo' o 'tercer'.")
        
    @rx.var
    def salario_anual(self) -> float:
        salario_anual = self.form_data_primer_pilar.get('salario_medio', 0)
        return salario_anual if salario_anual else 0.0

    @rx.var
    def salario_mensual(self) -> float:
        salario_anual = self.salario_anual
        return salario_anual / 12 if salario_anual else 0.0

    @rx.var
    def salario_mensual_neto_pilar2(self) -> float:
        salario_mensual = self.salario_mensual
        quiere_aportar = str(self.form_data_segundo_pilar.get('quiere_aportar'))
        aportacion_2p = 2 if quiere_aportar.lower().startswith('s') else 0
        aportacion_2p_mensual = aportacion_2p * salario_mensual / 12
        return salario_mensual - aportacion_2p_mensual if salario_mensual > 0 else 0.0

    @rx.var
    def salario_mensual_neto_pilar3(self) -> float:
        salario_mensual = self.salario_mensual_neto_pilar2
        aportacion_3p = self.form_data_tercer_pilar.get('aportacion_empleado_3p',0)
        aportacion_3p_mensual = float(aportacion_3p) / 12
        return salario_mensual - aportacion_3p_mensual if salario_mensual > 0 else 0.0

    @rx.var
    def pension_anual_primer(self) -> float:
        return self.pension_primer_pilar * 12

    @rx.var
    def pension_anual_segundo(self) -> float:
        return self.pension_segundo_pilar * 12

    @rx.var
    def pension_anual_tercer(self) -> float:
        return self.pension_tercer_pilar * 12

    
