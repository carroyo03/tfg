from reportlab.pdfgen import canvas
from io import BytesIO
import reflex as rx
from tfg_app.backend.main import get_pension_recommendations, calcular_pension_1p, calcular_pension_2p, calcular_pension_3p
import datetime

class ResultState(rx.State):
    pension_total: float = 0.0
    recomendacion: str = ""

    def set_pension_total(self, pension: float):
        print(f"Setting pension_total to {pension}")  # Log para depurar
        self.pension_total = pension

    async def set_recomendacion(self, data: dict):
        recommendations = await get_pension_recommendations(data)
        if recommendations and isinstance(recommendations, list) and len(recommendations) > 0:
            self.recomendacion = recommendations[0][0]
        else:
            self.recomendacion = "No se encontraron recomendaciones"

    async def calculate_pensions(self, data3: dict):
        # Asegurarse de que data tenga el formato correcto para los tres pilares
        data1 = data3['prev_form']['prev_form']
        data2 = data3['prev_form']
        data1["fecha_nacimiento"] = datetime.datetime.strptime(data1['fecha_nacimiento'], "%d/%m/%Y")
        data1['n_hijos'] = str(data1['n_hijos']) 
        data1['edad_jubilacion_deseada'] = int(data1['edad_jubilacion_deseada']) if isinstance(data1['edad_jubilacion_deseada'], str) else data1['edad_jubilacion_deseada']
        pension1 = await calcular_pension_1p(data1)

        data2['prev_form']['fecha_nacimiento'] = data2['prev_form']['fecha_nacimiento'].strftime("%d/%m/%Y")
        pension2 = await calcular_pension_2p(data2)

        pension3 = await calcular_pension_3p(data3)
        # Sumar las pensiones
        total = pension1 + pension2 + pension3
        self.set_pension_total(total)

    async def generate_pdf(self, data3: dict):
        # Calcular las pensiones si no se ha hecho
        if self.pension_total == 0.0:
            await self.calculate_pensions(data3)
        await self.set_recomendacion(data3)
        if not self.recomendacion:
            self.recomendacion = "No se encontraron recomendaciones"
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.drawString(100, 800, "Resultados de la simulación")
        pdf.drawString(100, 780, f"Pensión total: €{self.pension_total:.2f}")
        # Ajustar el texto de la recomendación para que no se corte
        recomendacion_text = f"Recomendación: {self.recomendacion}"
        if len(recomendacion_text) > 50:  # Limitar longitud para evitar cortes
            recomendacion_text = recomendacion_text[:47] + "..."
        pdf.drawString(100, 760, recomendacion_text)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return rx.download(buffer.getvalue(), filename="Informe_Pension.pdf")