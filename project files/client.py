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
      
                       

