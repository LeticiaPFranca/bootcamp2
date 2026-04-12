import customtkinter as ctk
from src.ui.perfil import PerfilWindow
from src.ui.main_app import MainApp

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MedControl")
        self.geometry("450x600")
        self.mostrar_perfil()

    def mostrar_perfil(self):
        self.view = PerfilWindow(self, self.mostrar_lista)
        self.view.pack(fill="both", expand=True)

    def mostrar_lista(self):
        self.view.destroy() 
        self.view = MainApp(self)
        self.view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()