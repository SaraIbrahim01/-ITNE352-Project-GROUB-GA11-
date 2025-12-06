import socket
import threading
import json
import requests

HOST = "0.0.0.0"
PORT = 5000
API_KEY = "7e105333ff414544a47e8f0febc01b18"
HEADLINES_URL = "https://newsapi.org/v2/top-headlines"
SOURCES_URL = "https://newsapi.org/v2/top-headlines/sources"
GROUP_ID = "GA11"


def main_menu_text():
    return (
        "MAIN MENU:\n"
        "1 - Search headlines\n"
        "2 - List of Sources\n"
        "3 - Quit\n"
    )


def headlines_menu_text():
    return (
        "HEADLINES MENU:\n"
        "1 - Search for keywords\n"
        "2 - Search by category\n"
        "3 - Search by country\n"
        "4 - List all new headlines\n"
        "5 - Back to the main menu\n"
    )


def sources_menu_text():
    return (
        "SOURCES MENU:\n"
        "1 - Search by category\n"
        "2 - Search by country\n"
        "3 - Search by language\n"
        "4 - List all\n"
        "5 - Back to the main menu\n"
    )


def get_news_by_keyword(word):
    params = {
        "apiKey": API_KEY,
        "q": word,
        "language": "en",
    }
    r = requests.get(HEADLINES_URL, params=params)
    return r.json()


def get_news_by_category(cat):
    params = {
        "apiKey": API_KEY,
        "category": cat,
        "language": "en",
    }
    r = requests.get(HEADLINES_URL, params=params)
    return r.json()


def get_news_by_country(code):
    params = {
        "apiKey": API_KEY,
        "country": code,
        "language": "en",
    }
    r = requests.get(HEADLINES_URL, params=params)
    return r.json()


def get_all_news():
    params = {
        "apiKey": API_KEY,
        "language": "en",
        "country": "us",
    }
    r = requests.get(HEADLINES_URL, params=params)
    return r.json()


def show_article_details(art):
    source = (art.get("source") or {}).get("name", "Unknown")
    author = art.get("author", "Unknown")
    title = art.get("title", "No title")
    url = art.get("url", "No URL")
    desc = art.get("description", "No description")
    published = art.get("publishedAt", "Unknown")
    text = (
        "\nARTICLE DETAILS:\n"
        f"Source: {source}\n"
        f"Author: {author}\n"
        f"Title: {title}\n"
        f"URL: {url}\n"
        f"Description: {desc}\n"
        f"Published: {published}\n\n"
    )
    return text


def fetch_sources_by_category(cat):
    params = {
        "apiKey": API_KEY,
        "category": cat,
    }
    r = requests.get(SOURCES_URL, params=params)
    return r.json()

def fetch_sources_by_country(code):
    params = {
        "apiKey": API_KEY,
        "country": code,
    }
    r = requests.get(SOURCES_URL, params=params)
    return r.json()

def fetch_sources_by_language(lang):
    params = {
        "apiKey": API_KEY,
        "language": lang,
    }
    r = requests.get(SOURCES_URL, params=params)
    return r.json()



def source_details(src):
    name = src.get("name", "Unknown")
    country = src.get("country", "Unknown")
    desc = src.get("description", "No description")
    url = src.get("url", "No URL")
    category = src.get("category", "Unknown")
    language = src.get("language", "Unknown")

    text = (
        "\nSOURCE DETAILS:\n"
        f"Name: {name}\n"
        f"Country: {country}\n"
        f"Category: {category}\n"
        f"Language: {language}\n"
        f"URL: {url}\n"
        f"Description: {desc}\n\n"
    )
    return text


def handle_client(client_sock, client_addr, client_id):
    try:
        print(f"\n========== Start of thread id:{client_id} ==========")

        user_name = client_sock.recv(4096).decode("utf-8").strip()
        print(f">>> New client: {user_name} ({client_addr[0]}:{client_addr[1]})")

        welcome_msg = f"Welcome {user_name}! You are connected to the news server.\n"
        client_sock.sendall(welcome_msg.encode("utf-8"))
        client_sock.sendall(main_menu_text().encode("utf-8"))

        current_menu = "main"      
        view_state = "menu"
        current_results = [] 

        while True:
            data = client_sock.recv(4096)
            if not data:
                print(f"<<< {user_name} disconnected (no data)")
                break

            request = data.decode("utf-8").strip()
            print(f"[REQUEST] from {user_name}: {request}")

            # ================= MAIN MENU =================
            if current_menu == "main":
                if request == "1":
                    current_menu = "headlines"
                    view_state = "menu"
                    client_sock.sendall(headlines_menu_text().encode("utf-8"))

                elif request == "2":
                    current_menu = "sources"
                    view_state = "menu"
                    client_sock.sendall(sources_menu_text().encode("utf-8"))

                elif request == "3" or request.lower() == "quit":
                    print(f"[DISCONNECTED] {user_name} chose quit.")
                    break

                else:
                    msg = "Invalid option in MAIN MENU. Please choose 1, 2, or 3.\n"
                    client_sock.sendall(msg.encode("utf-8"))

            # ================= HEADLINES MENU =================
            elif current_menu == "headlines":
                if view_state == "menu":
                    if request == "1":
                        client_sock.sendall("Enter keyword:\n".encode("utf-8"))
                        view_state = "keyword_input"

                    elif request == "2":
                        txt = (
                            "Enter category (business, general, health, "
                            "science, sports, technology):\n"
                        )
                        client_sock.sendall(txt.encode("utf-8"))
                        view_state = "category_input"

                    elif request == "3":
                        txt = "Enter country code (au, ca, jp, ae, sa, kr, us, ma):\n"
                        client_sock.sendall(txt.encode("utf-8"))
                        view_state = "country_input"

                    elif request == "4":
                        # list all headlines
                        response = get_all_news()
                        articles = response.get("articles", [])
                        current_results = articles[:15]

                        file_name = f"{user_name}_headlines_all_{GROUP_ID}.json"
                        with open(file_name, "w", encoding="utf-8") as f:
                            json.dump(response, f, ensure_ascii=False, indent=2)

                        if not current_results:
                            client_sock.sendall("No headlines available.\n".encode("utf-8"))
                            client_sock.sendall(headlines_menu_text().encode("utf-8"))
                        else:
                            lines = []
                            for i, art in enumerate(current_results):
                                src = (art.get("source") or {}).get("name", "Unknown")
                                title = art.get("title", "No title")
                                lines.append(f"{i}) {src} | {title}")
                            lines.append("\nEnter article number OR B to go back:\n")
                            client_sock.sendall("\n".join(lines).encode("utf-8"))
                            view_state = "all_select"

                    elif request == "5":
                        current_menu = "main"
                        view_state = "menu"
                        client_sock.sendall(main_menu_text().encode("utf-8"))

                    else:
                        client_sock.sendall("Invalid option.\n".encode("utf-8"))

                # ------ keyword search ------
                elif view_state == "keyword_input":
                    keyword = request
                    response = get_news_by_keyword(keyword)
                    articles = response.get("articles", [])
                    current_results = articles[:15]

                    file_name = f"{user_name}_keyword_{GROUP_ID}.json"
                    with open(file_name, "w", encoding="utf-8") as f:
                        json.dump(response, f, ensure_ascii=False, indent=2)

                    if not current_results:
                        client_sock.sendall("No results found.\n".encode("utf-8"))
                        view_state = "menu"
                        client_sock.sendall(headlines_menu_text().encode("utf-8"))
                    else:
                        lines = []
                        for i, art in enumerate(current_results):
                            src = (art.get("source") or {}).get("name", "Unknown")
                            title = art.get("title", "No title")
                            lines.append(f"{i}) {src} | {title}")
                        lines.append("\nEnter article number OR B to go back:\n")
                        client_sock.sendall("\n".join(lines).encode("utf-8"))
                        view_state = "keyword_select"

                elif view_state == "keyword_select":
                    if request.upper() == "B":
                        view_state = "menu"
                        client_sock.sendall(headlines_menu_text().encode("utf-8"))
                    else:
                        try:
                            idx = int(request)
                        except ValueError:
                            client_sock.sendall("Please enter a number or B.\n".encode("utf-8"))
                        else:
                            if idx < 0 or idx >= len(current_results):
                                client_sock.sendall("Invalid index.\n".encode("utf-8"))
                            else:
                                art = current_results[idx]
                                txt = show_article_details(art)
                                client_sock.sendall(txt.encode("utf-8"))
                                client_sock.sendall("Press B to go back.\n".encode("utf-8"))

                # ------ category search ------
                elif view_state == "category_input":
                    category = request.strip().lower()
                    response = get_news_by_category(category)
                    articles = response.get("articles", [])
                    current_results = articles[:15]

                    file_name = f"{user_name}_headlines_category_{GROUP_ID}.json"
                    with open(file_name, "w", encoding="utf-8") as f:
                        json.dump(response, f, ensure_ascii=False, indent=2)

                    if not current_results:
                        client_sock.sendall("No results found for this category.\n".encode("utf-8"))
                        view_state = "menu"
                        client_sock.sendall(headlines_menu_text().encode("utf-8"))
                    else:
                        lines = []
                        for i, art in enumerate(current_results):
                            src = (art.get("source") or {}).get("name", "Unknown")
                            title = art.get("title", "No title")
                            lines.append(f"{i}) {src} | {title}")
                        lines.append("\nEnter article number OR B to go back:\n")
                        client_sock.sendall("\n".join(lines).encode("utf-8"))
                        view_state = "category_select"

                elif view_state == "category_select":
                    if request.upper() == "B":
                        view_state = "menu"
                        client_sock.sendall(headlines_menu_text().encode("utf-8"))
                    else:
                        try:
                            idx = int(request)
                        except ValueError:
                            client_sock.sendall("Please enter a number or B.\n".encode("utf-8"))
                        else:
                            if idx < 0 or idx >= len(current_results):
                                client_sock.sendall("Invalid index.\n".encode("utf-8"))
                            else:
                                art = current_results[idx]
                                txt = show_article_details(art)
                                client_sock.sendall(txt.encode("utf-8"))
                                client_sock.sendall("Press B to go back.\n".encode("utf-8"))

                # ------ country search ------
                elif view_state == "country_input":
                    country = request.strip().lower()
                    response = get_news_by_country(country)
                    articles = response.get("articles", [])
                    current_results = articles[:15]

                    file_name = f"{user_name}_headlines_country_{GROUP_ID}.json"
                    with open(file_name, "w", encoding="utf-8") as f:
                        json.dump(response, f, ensure_ascii=False, indent=2)

                    if not current_results:
                        client_sock.sendall("No results found for this country.\n".encode("utf-8"))
                        view_state = "menu"
                        client_sock.sendall(headlines_menu_text().encode("utf-8"))
                    else:
                        lines = []
                        for i, art in enumerate(current_results):
                            src = (art.get("source") or {}).get("name", "Unknown")
                            title = art.get("title", "No title")
                            lines.append(f"{i}) {src} | {title}")
                        lines.append("\nEnter article number OR B to go back:\n")
                        client_sock.sendall("\n".join(lines).encode("utf-8"))
                        view_state = "country_select"

                elif view_state == "country_select":
                    if request.upper() == "B":
                        view_state = "menu"
                        client_sock.sendall(headlines_menu_text().encode("utf-8"))
                    else:
                        try:
                            idx = int(request)
                        except ValueError:
                            client_sock.sendall("Please enter a number or B.\n".encode("utf-8"))
                        else:
                            if idx < 0 or idx >= len(current_results):
                                client_sock.sendall("Invalid index.\n".encode("utf-8"))
                            else:
                                art = current_results[idx]
                                txt = show_article_details(art)
                                client_sock.sendall(txt.encode("utf-8"))
                                client_sock.sendall("Press B to go back.\n".encode("utf-8"))

                # ------ all headlines ------
                elif view_state == "all_select":
                    if request.upper() == "B":
                        view_state = "menu"
                        client_sock.sendall(headlines_menu_text().encode("utf-8"))
                    else:
                        try:
                            idx = int(request)
                        except ValueError:
                            client_sock.sendall("Please enter a number or B.\n".encode("utf-8"))
                        else:
                            if idx < 0 or idx >= len(current_results):
                                client_sock.sendall("Invalid index.\n".encode("utf-8"))
                            else:
                                art = current_results[idx]
                                txt = show_article_details(art)
                                client_sock.sendall(txt.encode("utf-8"))
                                client_sock.sendall("Press B to go back.\n".encode("utf-8"))

            # ================= SOURCES MENU =================
            elif current_menu == "sources":
                if view_state == "menu":
                    if request == "1":
                        # Search sources by category
                        txt = (
                            "Enter category (business, general, health, "
                            "science, sports, technology):\n"
                        )
                        client_sock.sendall(txt.encode("utf-8"))
                        view_state = "src_category_input"

                    elif request == "2":
                        # Search sources by country
                        txt = "Enter country code (au, ca, jp, ae, sa, kr, us, ma):\n"
                        client_sock.sendall(txt.encode("utf-8"))
                        view_state = "src_country_input"

                    elif request == "5":
                        # Back to main menu
                        current_menu = "main"
                        view_state = "menu"
                        client_sock.sendall(main_menu_text().encode("utf-8"))

                    else:
                        # باقي الخيارات لسه مو مطبّقة
                        msg = (
                            "This SOURCES option is not implemented yet.\n"
                            "Choose 1 (category), 2 (country), or 5 to go back.\n"
                        )
                        client_sock.sendall(msg.encode("utf-8"))

                # ===== category input for sources =====
                elif view_state == "src_category_input":
                    category = request.strip().lower()
                    print(f"[SOURCES CATEGORY] user={user_name}, category={category}")

                    response = fetch_sources_by_category(category)
                    sources = response.get("sources", [])
                    current_results = sources[:15]

                    file_name = f"{user_name}_sources_category_{GROUP_ID}.json"
                    with open(file_name, "w", encoding="utf-8") as f:
                        json.dump(response, f, ensure_ascii=False, indent=2)

                    if not current_results:
                        client_sock.sendall(
                            "No sources found for this category.\n".encode("utf-8")
                        )
                        view_state = "menu"
                        client_sock.sendall(sources_menu_text().encode("utf-8"))
                    else:
                        lines = []
                        for i, src in enumerate(current_results):
                            name = src.get("name", "Unknown")
                            lines.append(f"{i}) {name}")
                        lines.append("\nEnter source number OR B to go back:\n")
                        client_sock.sendall("\n".join(lines).encode("utf-8"))
                        view_state = "src_category_select"

                elif view_state == "src_category_select":
                    if request.upper() == "B":
                        view_state = "menu"
                        client_sock.sendall(sources_menu_text().encode("utf-8"))
                    else:
                        try:
                            idx = int(request)
                        except ValueError:
                            client_sock.sendall(
                                "Please enter a number or B.\n".encode("utf-8")
                            )
                        else:
                            if idx < 0 or idx >= len(current_results):
                                client_sock.sendall("Invalid index.\n".encode("utf-8"))
                            else:
                                src = current_results[idx]
                                txt = source_details(src)
                                client_sock.sendall(txt.encode("utf-8"))
                                client_sock.sendall(
                                    "Press B to go back.\n".encode("utf-8")
                                )

                # ===== country input for sources =====
                elif view_state == "src_country_input":
                    country = request.strip().lower()
                    print(f"[SOURCES COUNTRY] user={user_name}, country={country}")

                    response = fetch_sources_by_country(country)
                    sources = response.get("sources", [])
                    current_results = sources[:15]

                    file_name = f"{user_name}_sources_country_{GROUP_ID}.json"
                    with open(file_name, "w", encoding="utf-8") as f:
                        json.dump(response, f, ensure_ascii=False, indent=2)

                    if not current_results:
                        client_sock.sendall(
                            "No sources found for this country.\n".encode("utf-8")
                        )
                        view_state = "menu"
                        client_sock.sendall(sources_menu_text().encode("utf-8"))
                    else:
                        lines = []
                        for i, src in enumerate(current_results):
                            name = src.get("name", "Unknown")
                            lines.append(f"{i}) {name}")
                        lines.append("\nEnter source number OR B to go back:\n")
                        client_sock.sendall("\n".join(lines).encode("utf-8"))
                        view_state = "src_country_select"

                elif view_state == "src_country_select":
                    if request.upper() == "B":
                        view_state = "menu"
                        client_sock.sendall(sources_menu_text().encode("utf-8"))
                    else:
                        try:
                            idx = int(request)
                        except ValueError:
                            client_sock.sendall(
                                "Please enter a number or B.\n".encode("utf-8")
                            )
                        else:
                            if idx < 0 or idx >= len(current_results):
                                client_sock.sendall("Invalid index.\n".encode("utf-8"))
                            else:
                                src = current_results[idx]
                                txt = source_details(src)
                                client_sock.sendall(txt.encode("utf-8"))
                                client_sock.sendall(
                                    "Press B to go back.\n".encode("utf-8")
                                )
                                

    finally:
        client_sock.close()
        print(f"========== End of thread id:{client_id} ==========")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(3)
        print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

        client_threads = []
        while True:
            client_sock, client_addr = s.accept()
            print(f"[ACCEPTED] Connection from {client_addr}")

            t = threading.Thread(
                target=handle_client,
                args=(client_sock, client_addr, len(client_threads) + 1)
            )
            client_threads.append(t)
            t.start()


if __name__ == "__main__":
    start_server()













     