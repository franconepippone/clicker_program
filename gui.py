#!/usr/bin/env python3
"""
tiny_button.py

A minimal cross-platform GUI with a single button using Tkinter.
Run: python tiny_button.py
"""

import tkinter as tk
from tkinter import messagebox


def on_click():
    messagebox.showinfo("Hello", "Button clicked!")


def main():
    root = tk.Tk()
    root.title("Tiny Button App")
    root.geometry("300x120")
    root.resizable(True, False)

    btn = tk.Button(root, text="Click me", command=on_click, width=12, height=2)
    btn.pack(expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
