import tkinter as tk
from src.app import XMLAnalyzerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = XMLAnalyzerApp(root)
    root.mainloop()