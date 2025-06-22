import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

SERVER_PATH = os.path.abspath(os.path.join("source_code", "server.py"))
CLIENT_PATH = os.path.abspath(os.path.join("source_code", "client.py"))

processes = {"server": None, "clients": [None, None]}

def start_server():
    if processes["server"] is not None:
        messagebox.showinfo("Warning", "Server was already started.")
        return
    try:
        processes["server"] = subprocess.Popen([sys.executable, SERVER_PATH])
        messagebox.showinfo("Server", "Server started successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Error starting server:\n{e}")

def open_client():
    if None not in processes["clients"]:
        messagebox.showinfo("Warning", "Maximum of 2 clients are already open.")
        return
    try:
        proc = subprocess.Popen([sys.executable, CLIENT_PATH])
        for i in range(len(processes["clients"])):
            if processes["clients"][i] is None:
                processes["clients"][i] = proc
                break
    except Exception as e:
        messagebox.showerror("Error", f"Error opening client:\n{e}")

def shutdown_all():
    try:
        if processes["server"]:
            processes["server"].terminate()
        for p in processes["clients"]:
            if p is not None:
                p.terminate()
    except:
        pass
    root.destroy()

# Interface gráfica
root = tk.Tk()
root.title("CryptoChat Launcher")
root.geometry("320x200")
root.resizable(False, False)

title = tk.Label(root, text="CryptoChat Launcher", font=("Helvetica", 16, "bold"))
title.pack(pady=10)

btn_server = tk.Button(root, text="Start Server", width=25, command=start_server, bg="#4CAF50", fg="white")
btn_server.pack(pady=5)

btn_client = tk.Button(root, text="Open Client", width=25, command=open_client, bg="#2196F3", fg="white")
btn_client.pack(pady=5)

btn_exit = tk.Button(root, text="Close All", width=25, command=shutdown_all, bg="#f44336", fg="white")
btn_exit.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", shutdown_all)
root.mainloop()
