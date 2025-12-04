import socket
import threading
import json
import requests
HOST = "0.0.0.0"
PORT= 5000
# handle_client function will process client connection
def handle_client(sock, addr):
    print(f"[THREAD START] New client from {addr}")  # new client arrived
    client_name = sock.recv(4096).decode('utf-8').strip()
    print(f"[NEW CONNECTION] {client_name} ({addr[0]}:{addr[1]})")
    welcome_msg = f"Welcome {client_name}! You are connected to the news server."
    sock.send(welcome_msg.encode('utf-8'))
    

     