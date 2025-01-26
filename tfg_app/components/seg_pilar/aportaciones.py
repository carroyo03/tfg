import reflex as rx

class Company2PState(rx.State):
    value:str = ".05"



class Employee2PState(rx.State):
    value:str = "0"
    quiere_aportar:str = ""

    def set_value(self):
        if self.quiere_aportar.lower() in ["si","sí"]:
            self.value = "0.02"
        else:
            self.value = "0"