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

    sock.send(get_main_menu().encode('utf-8'))
    current_menu = "main"

    # Loop to receive messages from this client
    while True:
        request = sock.recv(4096).decode('utf-8').strip()

        # client closed connection
        if not request:
            print("[DISCONNECTED]", client_name, "connection closed.")
            break

        print("[REQUEST]", client_name, "requested:", request)

        # ==============================
        # MAIN MENU
        # ==============================
        if current_menu == "main":
            if user_input == "1":
                current_menu = "headlines"
                sock.send(get_headlines_menu().encode('utf-8'))

            elif user_input == "2":
                current_menu = "sources"
                sock.send(get_sources_menu().encode('utf-8'))

            elif user_input == "3" or user_input == "quit":
                print("[DISCONNECTED]", client_name, "selected quit from main menu.")
                break

            else:
                response = "Invalid option in MAIN MENU. Please choose 1, 2, or 3.\n"
                sock.send(response.encode('utf-8'))

        # ==============================
        # HEADLINES MENU
        # ==============================
        elif current_menu == "headlines":
            if user_input == "5":
                current_menu = "main"
                sock.send(get_main_menu().encode('utf-8'))
            else:
                response = "Headlines option not implemented yet. Use 5 to go back.\n"
                sock.send(response.encode('utf-8'))

        # ==============================
        # SOURCES MENU
        # ==============================
        elif current_menu == "sources":
            if user_input == "5":
                current_menu = "main"
                sock.send(get_main_menu().encode('utf-8'))
            else:
                response = "Sources option not implemented yet. Use 5 to go back.\n"
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












     