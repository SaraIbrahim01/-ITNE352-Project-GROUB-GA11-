import socket
import threading
import json
import requests

HOST = "0.0.0.0"
PORT = 5000


# handle_client function will process each client connection
def handle_client(sock, addr):
    print(f"[THREAD START] New client from {addr}")  # new client arrived

    # Receive client name
    client_name = sock.recv(4096).decode('utf-8').strip()
    print(f"[NEW CONNECTION] {client_name} ({addr[0]}:{addr[1]})")

    # Send welcome message to client
    welcome_msg = f"Welcome {client_name}! You are connected to the news server.\n"
    sock.send(welcome_msg.encode('utf-8'))

    # Loop to receive messages from this client
    while True:
        request = sock.recv(4096).decode('utf-8').strip()

        # client closed connection
        if not request:
            print("[DISCONNECTED]", client_name, "connection closed.")
            break

        print("[REQUEST]", client_name, "requested:", request)

        # quit command
        if request == "quit":
            print("[DISCONNECTED]", client_name, "sent quit.")
            break

        # simple response (placeholder)
        response = "Server received your request: " + request + "\n"
        sock.send(response.encode('utf-8'))

    # close socket
    sock.close()
    print("[THREAD END] Finished handling client", client_name)



# start server function (listening and accepting clients)
def start_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen(3)

    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    # Accept loop
    while True:
        client_sock, client_addr = server_sock.accept()
        print(f"[ACCEPTED] Connection from {client_addr}")

        t = threading.Thread(target=handle_client, args=(client_sock, client_addr))
        t.start()


# Run server
start_server()





     