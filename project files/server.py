import socket
import threading
import json
import requests 

HOST = "0.0.0.0"
PORT = 5000
API_KEY = '7e105333ff414544a47e8f0febc01b18'
HEADLINES_URL ="https://newsapi.org/v2/top-headlines"
GROUP_ID = 'GA11'

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
    def fetch_headlines_by_keyword(keyword):
     params = {
        "apiKey": API_KEY,
        "q": keyword,
        "language": "en"
    }

    response = requests.get(HEADLINES_URL, params=params)
    return response.json()


def handle_client(sock_a, sock_addr, client_id):
    try:
        print(f"\n========== Start of thread id:{client_id} ==========")

        client_name = sock_a.recv(4096).decode('utf-8').strip()
        print(f">>> Connection has been established with >> {client_name} "
              f"({sock_addr[0]}:{sock_addr[1]})")

        welcome_msg = f"Welcome {client_name}! You are connected to the news server.\n"
        sock_a.sendall(welcome_msg.encode('utf-8'))
        sock_a.sendall(get_main_menu().encode('utf-8'))

        current_menu = "main"

        state = "menu"
        news_list = []
        while True:
            request = sock_a.recv(4096).decode('utf-8').strip()
            if not request:
                print(f"<<< {client_name} disconnected (empty request)")
                break

            print(f"[REQUEST] from {client_name}: {request}")

            # ================= MAIN MENU =================
            if current_menu == "main":

                if request == "1":
                    current_menu = "headlines"
                    state = "menu"
                    sock_a.sendall(get_headlines_menu().encode('utf-8'))

                elif request == "2":
                    current_menu = "sources"
                    sock_a.sendall(get_sources_menu().encode('utf-8'))

                elif request == "3" or request == "quit":
                    print(f"[DISCONNECTED] {client_name} selected quit from main menu.")
                    break

                else:
                    msg = "Invalid option in MAIN MENU. Please choose 1, 2, or 3.\n"
                    sock_a.sendall(msg.encode('utf-8'))

            # ================= HEADLINES MENU =================
            elif current_menu == "headlines":

                if state == "menu":

                    if request == "1":
                        sock_a.send("Enter keyword:\n".encode('utf-8'))
                        state = "keyword_input"

                    elif request == "2":
                        sock_a.send("Category search not done yet.\n".encode('utf-8'))

                    elif request == "3":
                        sock_a.send("Country search not done yet.\n".encode('utf-8'))

                    elif request == "4":
                        sock_a.send("List all headlines not done yet.\n".encode('utf-8'))

                    elif request == "5":
                        current_menu = "main"
                        state = "menu"
                        sock_a.send(get_main_menu().encode('utf-8'))

                    else:
                        sock_a.send("Invalid option.\n".encode('utf-8'))

                elif state == "keyword_input":

                    kw = request

                    data = fetch_headlines_by_keyword(kw)
                    articles = data.get("articles", [])
                    news_list = articles[:15]

                    fname = f"{client_name}_kw_{GROUP_ID}.json"
                    with open(fname, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    if not news_list:
                        sock_a.send("No results.\n".encode('utf-8'))
                        state = "menu"
                        sock_a.send(get_headlines_menu().encode('utf-8'))
                    else:
                        lines = []
                        for i, a in enumerate(news_list):
                            src = (a.get("source") or {}).get("name", "Unknown")
                            title = a.get("title") or "No title"
                            lines.append(f"{i}) {src} | {title}")

                        lines.append("\nEnter number or B:\n")
                        sock_a.send("\n".join(lines).encode('utf-8'))

                        state = "keyword_select"
                        


            # ================= SOURCES MENU =================
            elif current_menu == "sources":
                if request == "5":
                    current_menu = "main"
                    sock_a.sendall(get_main_menu().encode('utf-8'))
                else:
                    msg = "Sources options not implemented yet. Use 5 to go back.\n"
                    sock_a.sendall(msg.encode('utf-8'))

    finally:
        sock_a.close()
        print(f"========== End of thread id:{client_id} ==========")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(3)  
        print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

        client_threads = []
        while True:
            sock_a, sock_addr = s.accept()
            print(f"[ACCEPTED] Connection from {sock_addr}")

            t = threading.Thread(
                target=handle_client,
                args=(sock_a, sock_addr, len(client_threads) + 1)
            )
            client_threads.append(t)
            t.start()


if __name__ == "__main__":
    start_server()












     