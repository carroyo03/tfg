from reportlab.pdfgen import canvas #type:ignore
from io import BytesIO
import reflex as rx
from tfg_app.backend.main import get_pension_recommendations

class ResultState(rx.State):
    pension_total: float = 0.0
    recomendacion: str = ""
    def set_pension_total(self, pension: float):
        self.pension_total = pension

    async def set_recomendacion(self, data:dict):
        self.recomendacion = await get_pension_recommendations(data)
        
    
    async def generate_pdf(self, data:dict):
        await self.set_recomendacion(data)
        if not self.recomendacion:
            self.recomendacion = "No se encontraron recomendaciones"
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.drawString(100, 800, "Resultados de la simulación")
        pdf.drawString(100,780, f"Pensión total: {self.pension_total}")
        pdf.drawString(100, 780, f"Recomendación: {self.recomendacion}")
        # Añadir más contenido al PDF según sea necesario
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return rx.download(str(buffer), filename="Informe Pensión.pdf")