from tkinter import *
from tkinter import scrolledtext, messagebox
from tkinter import ttk
import datetime
import os

class ChatWindow:
    def __init__(self, nickname, on_send, on_close):
        self.window = Tk()
        self.window.title(f"Cryptochat - {nickname}")
        self.window.geometry("600x600")
        self.window.minsize(600, 600)
        self.nickname = nickname
        
        # Adicionando ícone à janela
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cryptochatIcon.ico")
        if os.path.exists(icon_path):
            try:
                self.window.iconbitmap(icon_path)
            except TclError:
                print(f"Não foi possível carregar o ícone: {icon_path}")
        
        # Configurando cores
        self.bg_color = "#f0f0f0"
        self.text_bg = "#ffffff"
        
        # Configurando o estilo
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Send.TButton", background="#45a049", foreground="black")
        self.style.map("Send.TButton",
                       background=[("active", "#45a049"), ("pressed", "#28852b")],
                       foreground=[("disabled", "#45a049")])
        self.style.configure("Exit.TButton", background="#e53935", foreground="black")
        self.style.map("Exit.TButton",
                       background=[("active", "#e53935"), ("pressed", "#9c1e1e")],
                       foreground=[("disabled", "#e53935")])
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=BOTH, expand=True)
        
        # Status bar
        self.status_var = StringVar()
        self.status_var.set("Connected")
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=X, pady=(0, 5))
        
        ttk.Label(status_frame, text=f"Logged in as: {nickname}").pack(side=LEFT)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="green")
        self.status_label.pack(side=RIGHT)
        
        # Área de mensagens
        chat_frame = ttk.Frame(main_frame)
        chat_frame.pack(fill=BOTH, expand=True)
        
        self.text_area = scrolledtext.ScrolledText(chat_frame, wrap=WORD, bg=self.text_bg)
        self.text_area.pack(padx=5, pady=5, fill=BOTH, expand=True)
        self.text_area.config(state=DISABLED)
        
        # Frame de entrada e botões
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=X, pady=(5, 0))
        
        self.msg_entry = ttk.Entry(input_frame)
        self.msg_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        self.msg_entry.bind("<Return>", lambda event: self._send())
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X, pady=(5, 0))
        
        self.send_btn = ttk.Button(button_frame, text="Send", command=self._send, style="Send.TButton")
        self.send_btn.pack(side=LEFT, padx=5)
        
        self.exit_btn = ttk.Button(button_frame, text="Exit", command=self._on_close, style="Exit.TButton")
        self.exit_btn.pack(side=RIGHT, padx=5)
        
        self.on_send = on_send
        self.on_close = on_close
        
        # Configurando evento de fechamento da janela
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Foco inicial
        self.msg_entry.focus()
    
    def _send(self):
        msg = self.msg_entry.get()
        if msg.strip():
            self.on_send(msg)
            self.msg_entry.delete(0, END)
    
    def _on_close(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit the chat?"):
            self.on_close()
            self.window.destroy()
    
    def set_status(self, status, color="green"):
        self.status_var.set(status)
        self.status_label.config(foreground=color)
    
    def display(self, message: str):
        self.text_area.config(state=NORMAL)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if message.startswith("[SYSTEM]"):
            # Mensagem do sistema
            self.text_area.insert(END, f"{timestamp} {message}\n", "system")
            self.text_area.tag_configure("system", foreground="#C46D02")
        elif message.startswith(f"[{self.nickname}]") or message.startswith("[You]"):
            # Mensagem do usuário
            self.text_area.insert(END, f"{timestamp} {message}\n", "self")
            self.text_area.tag_configure("self", foreground="#000000")
        else:
            # Mensagem do outro usuário
            self.text_area.insert(END, f"{timestamp} {message}\n", "other")
            self.text_area.tag_configure("other", foreground="#2800AA")
        
        self.text_area.config(state=DISABLED)
        self.text_area.yview(END)
    
    def run(self):
        try:
            self.display("[SYSTEM] Welcome to Cryptochat! Your messages are end-to-end encrypted.")
            self.window.mainloop()
        except Exception as e:
            import traceback
            print(f"Error in chat window: {e}")
            print(traceback.format_exc())