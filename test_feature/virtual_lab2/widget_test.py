import tkinter as tk
from tkinter import ttk

def on_slider_change(event):
    value = slider.get()
    label.config(text=f"Valeur: {value:.2f}")

# Créez la fenêtre principale
root = tk.Tk()
root.title("FloatSlider Example")

# Créez un curseur de nombres décimaux (FloatSlider)
slider = ttk.Scale(root, from_=0.0, to=1.0, orient="horizontal", length=200, digits=2)
slider.set(0.5)  # Définissez la valeur initiale
slider.bind("<Motion>", on_slider_change)  # Réagir au changement de valeur

# Créez une étiquette pour afficher la valeur du curseur
label = tk.Label(root, text="Valeur: 0.50")

# Placez le curseur et l'étiquette dans la fenêtre
slider.pack(padx=20, pady=10)
label.pack(pady=10)

root.mainloop()
