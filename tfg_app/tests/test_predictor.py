# tests/test_simulator.py
import unittest
from tfg_app.backend.main import calcular_pension_1p, calcular_pension_2p, calcular_pension_3p
import asyncio
import datetime
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





    def test_simulator(self):

        
        class MockResultState:
                def __init__(self):
                    self.pension_total = 0

        
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
            self.assertGreater(state.pension_total,0, "La pensión debería ser mayor que 0")
        asyncio.run(run_test())


        

if __name__ == "__main__":
    unittest.main()