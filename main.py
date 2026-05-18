import sys
from pathlib import Path

# Configura o caminho do projeto
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import customtkinter as ctk
from src.ui.perfil import PerfilWindow


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MedControl")
        self.geometry("800x700")

        # Tema visual
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Tela de perfil
        self.perfil = PerfilWindow(
            self,
            callback_continuar=self.continuar
        )
        self.perfil.pack(fill="both", expand=True)

    def continuar(self):
        print("Continuando para próxima tela...")


if __name__ == "__main__":
    app = App()
    app.mainloop()