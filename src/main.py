import customtkinter as ctk
from ui_manager import UIManager

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    ui = UIManager(app)
    app.mainloop()
