# News Service Client - GUI Version (Tkinter)


import socket
import threading
import tkinter as tk
from tkinter import scrolledtext , messagebox


# Server settings (change HOST if the server is on another machine)

SERVER_HOST = "127.0.0.1"      # Server settings (change HOST if the server is on another machine)
SERVER_PORT = 5000             # Must match your server port

