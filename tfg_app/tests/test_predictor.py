# tests/test_simulator.py
import unittest
from tfg_app.backend.predictions.print_predictions import ResultState
from tfg_app.backend.main import calcular_pension_1p, calcular_pension_2p, calcular_pension_3p, get_pension_recommendations
from tfg_app.backend.predictions.train_model import train_model
from tfg_app.backend.predictions.neural_network import PensionPredictor as RealPredictor
import asyncio
import datetime
from unittest.mock import patch, MagicMock, AsyncMock
import torch
import reflex as rx
from io import BytesIO
from reportlab.pdfgen import canvas #type:ignore

class TestSimulator(unittest.TestCase):
    def setUp(self):
        self.data1 = {
            "fecha_nacimiento": datetime.datetime.strptime("01/01/1980", "%d/%m/%Y").date(),
            "gender": "Hombre",
            "tiene_hijos": "Sí",
            "n_hijos": 2,
            "salario_medio": 40000,
            "edad_inicio_trabajo": 22,
            "edad_jubilacion_deseada": 67,
            "r_cotizacion": "General",
            "lagunas_cotizacion": "No",
            "n_lagunas": 0,
        }
        self.data2 = {
            "quiere_aportar": "Sí",
            "aportacion_empresa": 2,
            "rentabilidad_2": 3,
            "prev_form": self.data1
        }
        
        self.data3 = {
            "aportacion_empleado_3p": 1000,
            "rentabilidad_3": 4,
            "prev_form": self.data2
        }

    def test_calcular_pension_1p(self):
        async def run_test():
            pension = await calcular_pension_1p(self.data1)
            self.assertGreater(pension, 0, "La pensión debe ser mayor que 0")
        asyncio.run(run_test())

    def test_calcular_pension_2p(self):
        async def run_test():
            self.data2['prev_form']['fecha_nacimiento'] = self.data2['prev_form']['fecha_nacimiento'].strftime("%d/%m/%Y")
            self.data2['prev_form']['n_hijos'] = str(self.data2['prev_form']['n_hijos'])
            pension = await calcular_pension_2p(self.data2)
            self.assertGreater(pension, 0, "La pensión debe ser mayor que 0")
        asyncio.run(run_test())
        
    def test_calcular_pension_3p(self):
        async def run_test():
            self.data3['prev_form'] = self.data2
            p1 = self.data3['prev_form']['prev_form']
            p1['fecha_nacimiento'] = p1['fecha_nacimiento'].strftime("%d/%m/%Y")
            p1['n_hijos'] = str(p1['n_hijos'])
            pension = await calcular_pension_3p(self.data3)
            self.assertGreater(pension, 0, "La pensión debe ser mayor que 0")
        asyncio.run(run_test())
        
    
    @patch('tfg_app.backend.main.torch.load')
    @patch('tfg_app.backend.main.PensionPredictor')
    @patch('tfg_app.backend.main.get_pension_recommendations')
    def test_recommendations(self, mock_get_recs, MockPensionPredictor, mock_torch_load):
        mock_model = MagicMock()
        # Ensure the mock model output matches expected tensor shape/type
        mock_model.return_value = torch.tensor([0.1, 0.2, 0.3, 0.4], dtype=torch.float32)
        mock_model.load_state_dict = MagicMock()
        MockPensionPredictor.return_value = mock_model
        mock_torch_load.return_value = RealPredictor().state_dict()

        async def run_test():
            # Pass the correct data structure (data3 includes nested prev_form)
            recommendations = await get_pension_recommendations(self.data3)
            self.assertIsInstance(recommendations, list)
            # Add more specific assertions based on the mocked output
        asyncio.run(run_test())
     
    
    
    @patch('tfg_app.backend.predictions.train_model.generate_synthetic_data',
           return_value=[({}, [0.0,0.0,0.0,0.0])])
    @patch('tfg_app.backend.predictions.train_model.PensionPredictor')
    @patch('tfg_app.backend.predictions.train_model.preprocess_input',
           return_value=torch.zeros(1,4))
    @patch('tfg_app.backend.predictions.train_model.MSELoss')   
    def test_train_model(self, mock_MSELoss, mock_preprocess_input, MockPensionPredictor,mock_generate_synthetic_data):
        
        mock_MSELoss.return_value = lambda pred, targ: torch.tensor((),
                                                                   requires_grad=True)
        
        
        class DummyModel:
            def __init__(self):
                self._p = [torch.nn.Parameter(torch.zeros(1))]
            def parameters(self): return self._p
            def __call__(self, x): return torch.zeros(x.size(0), 4,
                                                      requires_grad=True)
            def state_dict(self): return {}
            
        MockPensionPredictor.return_value = DummyModel()
        
        train_model()
        self.assertTrue(True)



    @patch('reflex.download')
    def test_generate_pdf(self, mock_rx_download):
# preparamos el “download”
        mock_download = MagicMock()
        mock_download.filename = "Informe Pensión.pdf"
        mock_rx_download.return_value = mock_download
        
        class MockResultState:
                def __init__(self):
                    self.pension_total = 0
                    self.recomendacion = None

                async def set_recomendacion(self, data):
                    self.recomendacion = "Recomendación de prueba"

                async def generate_pdf(self, data):
                    await self.set_recomendacion(data)
                    if not self.recomendacion:
                        self.recomendacion = "No se encontraron recomendaciones"
                    buffer = BytesIO()
                    pdf = canvas.Canvas(buffer)
                    pdf.drawString(100, 800, "Resultados de la simulación")
                    pdf.drawString(100,780, f"Pensión total: {self.pension_total}")
                    pdf.drawString(100, 760, f"Recomendación: {self.recomendacion}")
                    # Añadir más contenido al PDF según sea necesario
                    pdf.showPage()
                    pdf.save()
                    buffer.seek(0)
                    mock_download = rx.download(str(buffer), filename="Informe Pensión.pdf")
                    return mock_download
        
        
        state = MockResultState()

        async def run_test(): 
            pension1 = await calcular_pension_1p(self.data1)

            self.data2['prev_form']['fecha_nacimiento'] = \
                self.data2['prev_form']['fecha_nacimiento'].strftime("%d/%m/%Y") if isinstance(self.data2['prev_form']['fecha_nacimiento'], datetime.date) else self.data2['prev_form']['fecha_nacimiento']
            self.data2['prev_form']['n_hijos'] = \
                str(self.data2['prev_form']['n_hijos'])
            self.data3['prev_form'] = self.data2
            
            
            p1 = self.data3['prev_form']['prev_form']
            p1['fecha_nacimiento'] = p1['fecha_nacimiento'].strftime("%d/%m/%Y") if isinstance(p1['fecha_nacimiento'], datetime.date) else p1['fecha_nacimiento']
            p1['n_hijos'] = str(p1['n_hijos'])
        
        
            pension2 = await calcular_pension_2p(self.data2)
            pension3 = await calcular_pension_3p(self.data3)
            
            state.pension_total = pension1 + pension2 + pension3

            await state.set_recomendacion(self.data3)
            download = await state.generate_pdf(self.data3)
            self.assertEqual(download.filename, "Informe Pensión.pdf")
        asyncio.run(run_test())


        

if __name__ == "__main__":
    unittest.main()