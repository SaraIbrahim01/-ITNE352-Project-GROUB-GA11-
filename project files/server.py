import socket
import threading
import json
import requests

# Server settings (IP and Port)
HOST = "0.0.0.0"      # Listen on all available network interfaces
PORT = 5000           # Port number for the server

# NewsAPI data (API key and URLs)
API_KEY = "7e105333ff414544a47e8f0febc01b18"
HEADLINES_URL = "https://newsapi.org/v2/top-headlines"
SOURCES_URL = "https://newsapi.org/v2/top-headlines/sources"

GROUP_ID = "GA11"     # My group ID for saving JSON files


# Text for the main menu
def main_menu_text():
    return (
        "MAIN MENU:\n"
        "1 - Search headlines\n"
        "2 - List of Sources\n"
        "3 - Quit\n"
    )


# Text for headlines menu
def headlines_menu_text():
    return (
        "HEADLINES MENU:\n"
        "1 - Search for keywords\n"
        "2 - Search by category\n"
        "3 - Search by country\n"
        "4 - List all new headlines\n"
        "5 - Back to the main menu\n"
    )


# Text for sources menu
def sources_menu_text():
    return (
        "SOURCES MENU:\n"
        "1 - Search by category\n"
        "2 - Search by country\n"
        "3 - Search by language\n"
        "4 - List all\n"
        "5 - Back to the main menu\n"
    )


# Get headlines using keyword
def get_news_by_keyword(word):
    params = {"apiKey": API_KEY, "q": word, "language": "en"}
    return requests.get(HEADLINES_URL, params=params).json()


# Get headlines using category
def get_news_by_category(cat):
    params = {"apiKey": API_KEY, "category": cat, "language": "en"}
    return requests.get(HEADLINES_URL, params=params).json()


# Get headlines using country
def get_news_by_country(code):
    params = {"apiKey": API_KEY, "country": code, "language": "en"}
    return requests.get(HEADLINES_URL, params=params).json()


# Get all top headlines
def get_all_news():
    params = {"apiKey": API_KEY, "language": "en", "country": "us"}
    return requests.get(HEADLINES_URL, params=params).json()


# Format full article details
def show_article_details(art):
    # Extract different fields from article safely
    source = (art.get("source") or {}).get("name", "Unknown")
    author = art.get("author", "Unknown")
    title = art.get("title", "No title")
    url = art.get("url", "No URL")
    desc = art.get("description", "No description")
    published = art.get("publishedAt", "Unknown")

    return (
        "\nARTICLE DETAILS:\n"
        f"Source: {source}\nAuthor: {author}\nTitle: {title}\nURL: {url}\n"
        f"Description: {desc}\nPublished: {published}\n\n"
    )


# Fetch sources by category
def fetch_sources_by_category(cat):
    params = {"apiKey": API_KEY, "category": cat}
    return requests.get(SOURCES_URL, params=params).json()


# Fetch sources by country
def fetch_sources_by_country(code):
    params = {"apiKey": API_KEY, "country": code}
    return requests.get(SOURCES_URL, params=params).json()


# Fetch sources by language
def fetch_sources_by_language(lang):
    params = {"apiKey": API_KEY, "language": lang}
    return requests.get(SOURCES_URL, params=params).json()


# Fetch all sources
def fetch_all_sources():
    params = {"apiKey": API_KEY}
    return requests.get(SOURCES_URL, params=params).json()


# Format full source details
def source_details(src):
    name = src.get("name", "Unknown")
    country = src.get("country", "Unknown")
    desc = src.get("description", "No description")
    url = src.get("url", "No URL")
    category = src.get("category", "Unknown")
    language = src.get("language", "Unknown")

    return (
        "\nSOURCE DETAILS:\n"
        f"Name: {name}\nCountry: {country}\nCategory: {category}\n"
        f"Language: {language}\nURL: {url}\nDescription: {desc}\n\n"
    )


# Write JSON file for storing API results
def write_json_file(user, tag, data):
    # File name follows required format
    file_name = f"{user}_{tag}_{GROUP_ID}.json"

    # Save JSON data into file
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return file_name


# Create menu list for articles
def format_articles_menu(results):
    lines = []
    # Show article number with source, author, and title
    for i, art in enumerate(results):
        src = (art.get("source") or {}).get("name", "Unknown")
        author = art.get("author", "Unknown")
        title = art.get("title", "No title")
        lines.append(f"{i}) {src} | {author} | {title}")
    lines.append("\nEnter article number OR B to go back:\n")
    return "\n".join(lines)


# Create menu list for sources
def format_sources_menu(results):
    lines = []
    for i, src in enumerate(results):
        name = src.get("name", "Unknown")
        lines.append(f"{i}) {name}")
    lines.append("\nEnter source number OR B to go back:\n")
    return "\n".join(lines)


# Show full article details when user chooses index
def show_article_by_index(req, results, client):
    try:
        idx = int(req)   # Convert input to number
    except:
        client.sendall("Please enter a number or B.\n".encode("utf-8"))
        return

    # Check if index is valid
    if idx < 0 or idx >= len(results):
        client.sendall("Invalid index.\n".encode("utf-8"))
        return

    art = results[idx]
    client.sendall(show_article_details(art).encode("utf-8"))
    client.sendall("Press B to go back.\n".encode("utf-8"))


# Show full source details when user chooses index
def show_source_by_index(req, results, client):
    try:
        idx = int(req)
    except:
        client.sendall("Please enter a number or B.\n".encode("utf-8"))
        return

    if idx < 0 or idx >= len(results):
        client.sendall("Invalid index.\n".encode("utf-8"))
        return

    src = results[idx]
    client.sendall(source_details(src).encode("utf-8"))
    client.sendall("Press B to go back.\n".encode("utf-8"))


# Main function for handling each client connection
def handle_client(client_sock, client_addr, client_id):
    try:
        print(f"\n========== Start of thread id:{client_id} ==========")

        # Receive username from client
        user_name = client_sock.recv(4096).decode("utf-8").strip()
        print(f">>> New client: {user_name}")

        # Send welcome message and main menu
        client_sock.sendall(f"Welcome {user_name}! You are connected.\n".encode())
        client_sock.sendall(main_menu_text().encode())

        current_menu = "main"        # Track which menu we are in
        view_state = "menu"          # Track what we expect next
        current_results = []         # Store latest API results

        while True:
            # Receive data from client
            data = client_sock.recv(4096)
            if not data:
                print(f"<<< {user_name} disconnected")
                break

            request = data.decode().strip()
            print(f"[REQUEST] {user_name}: {request}")

            # ---------------- MAIN MENU ----------------
            if current_menu == "main":

                if request == "1":
                    current_menu = "headlines"
                    view_state = "menu"
                    client_sock.sendall(headlines_menu_text().encode())

                elif request == "2":
                    current_menu = "sources"
                    view_state = "menu"
                    client_sock.sendall(sources_menu_text().encode())

                elif request == "3" or request.lower() == "quit":
                    print(f"[DISCONNECTED] {user_name} quit.")
                    break

                else:
                    client_sock.sendall("Invalid option.\n".encode())


            # ---------------- HEADLINES MENU ----------------
            elif current_menu == "headlines":

                if view_state == "menu":

                    if request == "1":
                        client_sock.sendall("Enter keyword:\n".encode())
                        view_state = "keyword_input"

                    elif request == "2":
                        client_sock.sendall("Enter category:\n".encode())
                        view_state = "category_input"

                    elif request == "3":
                        client_sock.sendall("Enter country code:\n".encode())
                        view_state = "country_input"

                    elif request == "4":
                        # Get all headlines
                        response = get_all_news()
                        articles = response.get("articles", [])
                        current_results = articles[:15]   # Limit results

                        write_json_file(user_name, "headlines_all", response)

                        if not current_results:
                            client_sock.sendall("No headlines available.\n".encode())
                            client_sock.sendall(headlines_menu_text().encode())
                        else:
                            client_sock.sendall(format_articles_menu(current_results).encode())
                            view_state = "all_select"

                    elif request == "5":
                        # Back to main menu
                        current_menu = "main"
                        view_state = "menu"
                        client_sock.sendall(main_menu_text().encode())


                elif view_state == "keyword_input":
                    response = get_news_by_keyword(request)
                    current_results = response.get("articles", [])[:15]

                    write_json_file(user_name, "headlines_keyword", response)

                    if not current_results:
                        client_sock.sendall("No results.\n".encode())
                        client_sock.sendall(headlines_menu_text().encode())
                        view_state = "menu"
                    else:
                        client_sock.sendall(format_articles_menu(current_results).encode())
                        view_state = "keyword_select"


                elif view_state == "category_input":
                    response = get_news_by_category(request)
                    current_results = response.get("articles", [])[:15]

                    write_json_file(user_name, "headlines_category", response)

                    if not current_results:
                        client_sock.sendall("No results.\n".encode())
                        view_state = "menu"
                        client_sock.sendall(headlines_menu_text().encode())
                    else:
                        client_sock.sendall(format_articles_menu(current_results).encode())
                        view_state = "category_select"


                elif view_state == "country_input":
                    response = get_news_by_country(request)
                    current_results = response.get("articles", [])[:15]

                    write_json_file(user_name, "headlines_country", response)

                    if not current_results:
                        client_sock.sendall("No results.\n".encode())
                        client_sock.sendall(headlines_menu_text().encode())
                        view_state = "menu"
                    else:
                        client_sock.sendall(format_articles_menu(current_results).encode())
                        view_state = "country_select"


                elif view_state in ["keyword_select", "category_select", "country_select", "all_select"]:
                    if request.upper() == "B":
                        view_state = "menu"
                        client_sock.sendall(headlines_menu_text().encode())
                    else:
                        show_article_by_index(request, current_results, client_sock)


            # ---------------- SOURCES MENU ----------------
            elif current_menu == "sources":

                if view_state == "menu":

                    if request == "1":
                        client_sock.sendall("Enter category:\n".encode())
                        view_state = "src_category_input"

                    elif request == "2":
                        client_sock.sendall("Enter country code:\n".encode())
                        view_state = "src_country_input"

                    elif request == "3":
                        client_sock.sendall("Enter language:\n".encode())
                        view_state = "src_language_input"

                    elif request == "4":
                        response = fetch_all_sources()
                        sources = response.get("sources", [])
                        current_results = sources[:15]

                        write_json_file(user_name, "sources_all", response)

                        if not current_results:
                            client_sock.sendall("No sources.\n".encode())
                            client_sock.sendall(sources_menu_text().encode())
                        else:
                            client_sock.sendall(format_sources_menu(current_results).encode())
                            view_state = "src_all_select"

                    elif request == "5":
                        # Return to main menu
                        current_menu = "main"
                        view_state = "menu"
                        client_sock.sendall(main_menu_text().encode())


                elif view_state == "src_category_input":
                    response = fetch_sources_by_category(request)
                    current_results = response.get("sources", [])[:15]

                    write_json_file(user_name, "sources_category", response)

                    if not current_results:
                        client_sock.sendall("No results.\n".encode())
                        client_sock.sendall(sources_menu_text().encode())
                        view_state = "menu"
                    else:
                        client_sock.sendall(format_sources_menu(current_results).encode())
                        view_state = "src_category_select"


                elif view_state == "src_country_input":
                    response = fetch_sources_by_country(request)
                    current_results = response.get("sources", [])[:15]

                    write_json_file(user_name, "sources_country", response)

                    if not current_results:
                        client_sock.sendall("No results.\n".encode())
                        client_sock.sendall(sources_menu_text().encode())
                        view_state = "menu"
                    else:
                        client_sock.sendall(format_sources_menu(current_results).encode())
                        view_state = "src_country_select"


                elif view_state == "src_language_input":
                    response = fetch_sources_by_language(request)
                    current_results = response.get("sources", [])[:15]

                    write_json_file(user_name, "sources_language", response)

                    if not current_results:
                        client_sock.sendall("No results.\n".encode())
                        client_sock.sendall(sources_menu_text().encode())
                        view_state = "menu"
                    else:
                        client_sock.sendall(format_sources_menu(current_results).encode())
                        view_state = "src_language_select"


                elif view_state in ["src_category_select", "src_country_select", "src_language_select", "src_all_select"]:
                    if request.upper() == "B":
                        view_state = "menu"
                        client_sock.sendall(sources_menu_text().encode())
                    else:
                        show_source_by_index(request, current_results, client_sock)


    finally:
        # Close client socket when done
        client_sock.close()
        print(f"========== End of thread id:{client_id} ==========")


# Function to start the server
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))     # Bind server socket
        s.listen(3)              # Accept up to 3 pending connections
        print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

        threads = []             # Store threads for clients

        while True:
            # Accept new client
            client_sock, client_addr = s.accept()
            print(f"[ACCEPTED] {client_addr}")

            # Create thread for each client
            t = threading.Thread(target=handle_client,
                                 args=(client_sock, client_addr, len(threads) + 1))
            threads.append(t)
            t.start()


# Run the server
if __name__ == "__main__":
    start_server()






     