# News Service Client - GUI Version (Tkinter)


import socket
import threading
import tkinter as tk
from tkinter import scrolledtext , messagebox


# Server settings (change HOST if the server is on another machine)

SERVER_HOST = "127.0.0.1"      # Server settings (change HOST if the server is on another machine)
SERVER_PORT = 5000             # Must match your server port

class NewsClientGUI:
    def __init__(self, root: tk.Tk):       # Initialize the GUI window and build the login screen.
      self.root = root
      self.root.title("News Client - GUI Version") 

      self.sock: socket.socket | None = None       # TCP socket connection
      self.username: str =""                        # User's chosen name

      self.build_login_screen()                   # Create the login page first

 # When the window closes, run cleanup
      self.root.protocol("WM_DELETE_WINDOW", self.on_close)

# Utility: Remove all widgets from the window
    def clear_window(self):
       for widget in self.root.winfo_children():
          widget.destroy()

 # Login screen (username + connect button)
    def build_login_screen(self):
       self.clear_window()

       tk.Label(
          self.root, text="Enter your username:", font=("Arial", 14)
       ).pack(pady=10)

       


     
       



