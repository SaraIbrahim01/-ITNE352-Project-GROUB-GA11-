import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

ALLOWED_COUNTRIES = {"au", "ca", "jp", "ae", "sa", "kr", "us", "ma"}
ALLOWED_LANGUAGES = {"ar", "en"}
ALLOWED_CATEGORIES = {"business", "general", "health", "science", "sports", "technology"}


MAIN_MENU = (
    "\nMAIN MENU:\n"
    "1 - Search headlines\n"
    "2 - List of Sources\n"
    "3 - Quit\n"
)

HEADLINES_MENU = (
    "\nHEADLINES MENU:\n"
    "1 - Search for keywords\n"
    "2 - Search by category\n"
    "3 - Search by country\n"
    "4 - List all new headlines\n"
    "5 - Back to the main menu\n"
)

SOURCES_MENU = (
    "\nSOURCES MENU:\n"
    "1 - Search by category\n"
    "2 - Search by country\n"
    "3 - Search by language\n"
    "4 - List all\n"
    "5 - Back to the main menu\n"
)

INDEX_PROMPT = "\nEnter index number for details OR B to go back:\n"


class NewsClientGUI:
    def __init__(self, root):  
        self.root = root
        self.root.title("News Client (Very Simple)")

        self.sock = None
        self.username = ""

        self.menu = "main"          
        self.waiting = None        

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.build_login()

    # ---------- UI ----------
    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def build_login(self):
        self.clear()

        tk.Label(self.root, text="Username:", font=("Arial", 14)).pack(pady=10)
        self.user_entry = tk.Entry(self.root, font=("Arial", 14))
        self.user_entry.pack(pady=5)

        tk.Button(self.root, text="Connect", font=("Arial", 14), command=self.connect).pack(pady=10)

    def build_chat(self):
        self.clear()

        tk.Label(self.root, text=f"Connected as: {self.username}", font=("Arial", 11, "bold")).pack(pady=5)

        self.text = scrolledtext.ScrolledText(self.root, width=85, height=22, font=("Consolas", 11))
        self.text.pack(padx=10, pady=5)
        self.text.config(state=tk.DISABLED)

        bottom = tk.Frame(self.root)
        bottom.pack(pady=6)

        self.entry = tk.Entry(bottom, width=45, font=("Arial", 12))
        self.entry.pack(side=tk.LEFT, padx=5)

        tk.Button(bottom, text="Send", width=10, command=self.on_send).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom, text="Quit", width=10, command=self.quit_client).pack(side=tk.LEFT, padx=5)

        self.root.bind("<Return>", lambda e: self.on_send())

        self.show_menu("main")

    def append(self, msg: str):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, msg)
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def show_menu(self, which: str):
        self.menu = which
        self.waiting = None
        if which == "main":
            self.append(MAIN_MENU)
        elif which == "headlines":
            self.append(HEADLINES_MENU)
        elif which == "sources":
            self.append(SOURCES_MENU)

    def send_line(self, line: str):
        if not self.sock:
            return
        try:
            self.sock.sendall((line.strip() + "\n").encode("utf-8"))
        except:
            self.append("\n[Send error]\n")

    def receive_loop(self):
        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    self.append("\n[Disconnected from server]\n")
                    break

                msg = data.decode("utf-8", errors="replace")
                self.append(msg)

                if self._looks_like_list(msg):
                    self.waiting = "index"
                    self.append(INDEX_PROMPT)

        except:
            self.append("\n[Connection error]\n")

    def _looks_like_list(self, msg: str) -> bool:
        for ln in msg.splitlines():
            s = ln.strip()
            if s.startswith("0)") or s.startswith("0 )"):
                return True
        return False

    def connect(self):
        name = self.user_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter username")
            return

        self.username = name
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((SERVER_HOST, SERVER_PORT))
            self.sock.sendall((self.username + "\n").encode("utf-8"))
        except Exception as e:
            messagebox.showerror("Connection error", str(e))
            self.sock = None
            return

        self.build_chat()
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)

        self.append(f"\n> {text}\n")

        if self.waiting == "keyword":
            self.send_line(text)
            self.waiting = None
            return

        if self.waiting == "hl_category":
            if text not in ALLOWED_CATEGORIES:
                self.append(f"Invalid category. Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}\n")
                return
            self.send_line(text)
            self.waiting = None
            return

        if self.waiting == "hl_country":
            if text not in ALLOWED_COUNTRIES:
                self.append(f"Invalid country. Allowed: {', '.join(sorted(ALLOWED_COUNTRIES))}\n")
                return
            self.send_line(text)
            self.waiting = None
            return

        if self.waiting == "src_category":
            if text not in ALLOWED_CATEGORIES:
                self.append(f"Invalid category. Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}\n")
                return
            self.send_line(text)
            self.waiting = None
            return

        if self.waiting == "src_country":
            if text not in ALLOWED_COUNTRIES:
                self.append(f"Invalid country. Allowed: {', '.join(sorted(ALLOWED_COUNTRIES))}\n")
                return
            self.send_line(text)
            self.waiting = None
            return

        if self.waiting == "src_language":
            if text not in ALLOWED_LANGUAGES:
                self.append(f"Invalid language. Allowed: {', '.join(sorted(ALLOWED_LANGUAGES))}\n")
                return
            self.send_line(text)
            self.waiting = None
            return

        if self.waiting == "index":
            if text.upper() == "B":
                self.send_line("B")
                self.waiting = None
                self.show_menu(self.menu)
                return
            try:
                int(text)
                self.send_line(text)
            except:
                self.append("Please enter a number or B.\n")
            return

        if self.menu == "main":
            if text == "1":
                self.send_line("1")
                self.show_menu("headlines")
            elif text == "2":
                self.send_line("2")
                self.show_menu("sources")
            elif text == "3":
                self.quit_client()
            else:
                self.append("Invalid option.\n")
                self.append(MAIN_MENU)
            return

        if self.menu == "headlines":
            if text == "1":
                self.send_line("1")
                self.waiting = "keyword"
                self.append("Enter keyword:\n")
            elif text == "2":
                self.send_line("2")
                self.waiting = "hl_category"
                self.append(f"Enter category (Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}):\n")
            elif text == "3":
                self.send_line("3")
                self.waiting = "hl_country"
                self.append(f"Enter country code (Allowed: {', '.join(sorted(ALLOWED_COUNTRIES))}):\n")
            elif text == "4":
                self.send_line("4")
            elif text == "5":
                self.send_line("5")
                self.show_menu("main")
            else:
                self.append("Invalid option.\n")
                self.append(HEADLINES_MENU)
            return

        if self.menu == "sources":
            if text == "1":
                self.send_line("1")
                self.waiting = "src_category"
                self.append(f"Enter category (Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}):\n")
            elif text == "2":
                self.send_line("2")
                self.waiting = "src_country"
                self.append(f"Enter country code (Allowed: {', '.join(sorted(ALLOWED_COUNTRIES))}):\n")
            elif text == "3":
                self.send_line("3")
                self.waiting = "src_language"
                self.append(f"Enter language (Allowed: {', '.join(sorted(ALLOWED_LANGUAGES))}):\n")
            elif text == "4":
                self.send_line("4")
            elif text == "5":
                self.send_line("5")
                self.show_menu("main")
            else:
                self.append("Invalid option.\n")
                self.append(SOURCES_MENU)
            return

    def quit_client(self):
        try:
            if self.sock:
                self.send_line("3")
                self.sock.close()
        except:
            pass
        self.sock = None
        self.root.destroy()

    def on_close(self):
        self.quit_client()


if __name__ == "__main__":  
    root = tk.Tk()
    app = NewsClientGUI(root)
    root.mainloop()
