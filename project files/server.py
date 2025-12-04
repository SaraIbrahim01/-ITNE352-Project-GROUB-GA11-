import socket
import threading
import json
import requests

HOST = "0.0.0.0"
PORT = 5000

def get_main_menu():
    menu = (
        "MAIN MENU:\n"
        "1 - Search headlines\n"
        "2 - List of Sources\n"
        "3 - Quit\n"
    )
    return menu
def get_headlines_menu():
    menu = (
        "HEADLINES MENU:\n"
        "1 - Search for keywords\n"
        "2 - Search by category\n"
        "3 - Search by country\n"
        "4 - List all new headlines\n"
        "5 - Back to the main menu\n"
    )
    return menu
def get_sources_menu():
    menu = (
        "SOURCES MENU:\n"
        "1 - Search by category\n"
        "2 - Search by country\n"
        "3 - Search by language\n"
        "4 - List all\n"
        "5 - Back to the main menu\n"
    )
    return menu

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
        if request == "1":
            sock.send(get_headlines_menu().encode('utf-8'))

        elif request == "2":
            sock.send(get_sources_menu().encode('utf-8'))

        elif request == "3" or request == "quit":
            print("[DISCONNECTED]", client_name, "selected quit.")
            break

        else:
            response = "Invalid option. Please choose from the menu.\n"
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












     