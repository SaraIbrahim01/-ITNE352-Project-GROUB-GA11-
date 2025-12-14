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

ALLOWED_COUNTRIES = {"au", "ca", "jp", "ae", "sa", "kr", "us", "ma"}
ALLOWED_LANGUAGES = {"ar", "en"}
ALLOWED_CATEGORIES = {"business", "general", "health", "science", "sports", "technology"}


def get_news_by_keyword(word):
    params = {"apiKey": API_KEY, "q": word, "language": "en"}
    return requests.get(HEADLINES_URL, params=params, timeout=15).json()


def get_news_by_category(cat):
    params = {"apiKey": API_KEY, "category": cat, "language": "en"}
    return requests.get(HEADLINES_URL, params=params, timeout=15).json()


def get_news_by_country(code):
    params = {"apiKey": API_KEY, "country": code}
    return requests.get(HEADLINES_URL, params=params, timeout=15).json()


def get_all_news():
    params = {"apiKey": API_KEY, "country": "us"}
    return requests.get(HEADLINES_URL, params=params, timeout=15).json()


def fetch_sources_by_category(cat):
    params = {"apiKey": API_KEY, "category": cat}
    return requests.get(SOURCES_URL, params=params, timeout=15).json()


def fetch_sources_by_country(code):
    params = {"apiKey": API_KEY, "country": code}
    return requests.get(SOURCES_URL, params=params, timeout=15).json()


def fetch_sources_by_language(lang):
    params = {"apiKey": API_KEY, "language": lang}
    return requests.get(SOURCES_URL, params=params, timeout=15).json()


def fetch_all_sources():
    params = {"apiKey": API_KEY}
    return requests.get(SOURCES_URL, params=params, timeout=15).json()


def safe_send(client_sock, text: str) -> bool:
    """Send text safely. Return False if client disconnected."""
    try:
        client_sock.sendall(text.encode("utf-8"))
        return True
    except (BrokenPipeError, ConnectionResetError, OSError):
        return False


def write_json_file(user, option_tag, data):
    file_name = f"{user}_{option_tag}_{GROUP_ID}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return file_name


def send_api_error_if_any(resp, client_sock):
    if not isinstance(resp, dict):
        safe_send(client_sock, "API Error: Invalid response.\n")
        return True
    if resp.get("status") == "error":
        safe_send(client_sock, f"API Error: {resp.get('message','Unknown error')}\n")
        return True
    return False


def split_publish_datetime(published_at: str):
    if not published_at:
        return "Unknown", "Unknown"
    if "T" in published_at:
        d, t = published_at.split("T", 1)
        return d, t.replace("Z", "")
    return published_at, "Unknown"


def show_article_details(art):
    source = (art.get("source") or {}).get("name", "Unknown")
    author = art.get("author") or "Unknown"
    title = art.get("title") or "No title"
    url = art.get("url") or "No URL"
    desc = art.get("description") or "No description"
    published = art.get("publishedAt") or ""

    pub_date, pub_time = split_publish_datetime(published)

    return (
        "\nARTICLE DETAILS:\n"
        f"Source: {source}\n"
        f"Author: {author}\n"
        f"Title: {title}\n"
        f"URL: {url}\n"
        f"Description: {desc}\n"
        f"Publish date: {pub_date}\n"
        f"Publish time: {pub_time}\n\n"
    )


def source_details(src):
    name = src.get("name", "Unknown")
    country = src.get("country", "Unknown")
    desc = src.get("description", "No description")
    url = src.get("url", "No URL")
    category = src.get("category", "Unknown")
    language = src.get("language", "Unknown")

    return (
        "\nSOURCE DETAILS:\n"
        f"Name: {name}\n"
        f"Country: {country}\n"
        f"Description: {desc}\n"
        f"URL: {url}\n"
        f"Category: {category}\n"
        f"Language: {language}\n\n"
    )


def format_articles_list(results):
    lines = []
    for i, art in enumerate(results):
        src = (art.get("source") or {}).get("name", "Unknown")
        author = art.get("author") or "Unknown"
        title = art.get("title") or "No title"
        lines.append(f"{i}) {src} | {author} | {title}")
    return "\n".join(lines) + "\n"


def format_sources_list(results):
    lines = []
    for i, src in enumerate(results):
        name = src.get("name", "Unknown")
        lines.append(f"{i}) {name}")
    return "\n".join(lines) + "\n"


def show_article_by_index(req, results, client_sock):
    try:
        idx = int(req)
    except:
        safe_send(client_sock, "Please enter a number or B.\n")
        return

    if idx < 0 or idx >= len(results):
        safe_send(client_sock, "Invalid index.\n")
        return

    if not safe_send(client_sock, show_article_details(results[idx])):
        return
    safe_send(client_sock, format_articles_list(results))


def show_source_by_index(req, results, client_sock):
    try:
        idx = int(req)
    except:
        safe_send(client_sock, "Please enter a number or B.\n")
        return

    if idx < 0 or idx >= len(results):
        safe_send(client_sock, "Invalid index.\n")
        return

    if not safe_send(client_sock, source_details(results[idx])):
        return
    safe_send(client_sock, format_sources_list(results))


def handle_client(client_sock, client_addr, client_id):
    user_name = "Unknown"
    try:
        print(f"\n========== Start of thread id:{client_id} ==========")

        rfile = client_sock.makefile("r", encoding="utf-8", newline="\n")

        user_name = (rfile.readline() or "").strip()
        if not user_name:
            user_name = f"Client{client_id}"

        print(f">>> New client: {user_name}")

        if not safe_send(client_sock, f"Welcome {user_name}! Connected.\n"):
            return

        current_menu = "main"
        view_state = "menu"
        current_results = []
        pending_option_tag = None

        while True:
            line = rfile.readline()
            if not line:
                print(f"<<< {user_name} disconnected")
                break

            request = line.strip()
            if not request:
                continue

            print(f"[REQUEST] requester={user_name} menu={current_menu} state={view_state} input={request}")

            if current_menu == "main":
                if request == "1":
                    current_menu = "headlines"
                    view_state = "menu"
                elif request == "2":
                    current_menu = "sources"
                    view_state = "menu"
                elif request == "3" or request.lower() == "quit":
                    print(f"[DISCONNECTED] {user_name} quit.")
                    break
                else:
                    if not safe_send(client_sock, "Invalid option.\n"):
                        break

            elif current_menu == "headlines":
                if view_state == "menu":
                    if request == "1":
                        pending_option_tag = "1.1"
                        view_state = "keyword_input"
                    elif request == "2":
                        pending_option_tag = "1.2"
                        view_state = "category_input"
                    elif request == "3":
                        pending_option_tag = "1.3"
                        view_state = "country_input"
                    elif request == "4":
                        pending_option_tag = "1.4"
                        resp = get_all_news()
                        write_json_file(user_name, pending_option_tag, resp)

                        if send_api_error_if_any(resp, client_sock):
                            view_state = "menu"
                            continue

                        current_results = resp.get("articles", [])[:15]
                        if not current_results:
                            if not safe_send(client_sock, "No headlines available.\n"):
                                break
                            view_state = "menu"
                        else:
                            if not safe_send(client_sock, format_articles_list(current_results)):
                                break
                            view_state = "select_article"
                    elif request == "5":
                        current_menu = "main"
                        view_state = "menu"
                    else:
                        if not safe_send(client_sock, "Invalid option.\n"):
                            break

                elif view_state == "keyword_input":
                    resp = get_news_by_keyword(request)
                    write_json_file(user_name, pending_option_tag or "1.1", resp)

                    if send_api_error_if_any(resp, client_sock):
                        view_state = "menu"
                        continue

                    current_results = resp.get("articles", [])[:15]
                    if not current_results:
                        if not safe_send(client_sock, "No results.\n"):
                            break
                        view_state = "menu"
                    else:
                        if not safe_send(client_sock, format_articles_list(current_results)):
                            break
                        view_state = "select_article"

                elif view_state == "category_input":
                    if request not in ALLOWED_CATEGORIES:
                        if not safe_send(client_sock, f"Invalid category. Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}\n"):
                            break
                        view_state = "menu"
                        continue

                    resp = get_news_by_category(request)
                    write_json_file(user_name, pending_option_tag or "1.2", resp)

                    if send_api_error_if_any(resp, client_sock):
                        view_state = "menu"
                        continue

                    current_results = resp.get("articles", [])[:15]
                    if not current_results:
                        if not safe_send(client_sock, "No results.\n"):
                            break
                        view_state = "menu"
                    else:
                        if not safe_send(client_sock, format_articles_list(current_results)):
                            break
                        view_state = "select_article"

                elif view_state == "country_input":
                    if request not in ALLOWED_COUNTRIES:
                        if not safe_send(client_sock, f"Invalid country. Allowed: {', '.join(sorted(ALLOWED_COUNTRIES))}\n"):
                            break
                        view_state = "menu"
                        continue

                    resp = get_news_by_country(request)
                    write_json_file(user_name, pending_option_tag or "1.3", resp)

                    if send_api_error_if_any(resp, client_sock):
                        view_state = "menu"
                        continue

                    current_results = resp.get("articles", [])[:15]
                    if not current_results:
                        if not safe_send(client_sock, "No results.\n"):
                            break
                        view_state = "menu"
                    else:
                        if not safe_send(client_sock, format_articles_list(current_results)):
                            break
                        view_state = "select_article"

                elif view_state == "select_article":
                    if request.upper() == "B":
                        view_state = "menu"
                    else:
                        show_article_by_index(request, current_results, client_sock)

            elif current_menu == "sources":
                if view_state == "menu":
                    if request == "1":
                        pending_option_tag = "2.1"
                        view_state = "src_category_input"
                    elif request == "2":
                        pending_option_tag = "2.2"
                        view_state = "src_country_input"
                    elif request == "3":
                        pending_option_tag = "2.3"
                        view_state = "src_language_input"
                    elif request == "4":
                        pending_option_tag = "2.4"
                        resp = fetch_all_sources()
                        write_json_file(user_name, pending_option_tag, resp)

                        if send_api_error_if_any(resp, client_sock):
                            view_state = "menu"
                            continue

                        current_results = resp.get("sources", [])[:15]
                        if not current_results:
                            if not safe_send(client_sock, "No sources.\n"):
                                break
                            view_state = "menu"
                        else:
                            if not safe_send(client_sock, format_sources_list(current_results)):
                                break
                            view_state = "select_source"
                    elif request == "5":
                        current_menu = "main"
                        view_state = "menu"
                    else:
                        if not safe_send(client_sock, "Invalid option.\n"):
                            break

                elif view_state == "src_category_input":
                    if request not in ALLOWED_CATEGORIES:
                        if not safe_send(client_sock, f"Invalid category. Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}\n"):
                            break
                        view_state = "menu"
                        continue

                    resp = fetch_sources_by_category(request)
                    write_json_file(user_name, pending_option_tag or "2.1", resp)

                    if send_api_error_if_any(resp, client_sock):
                        view_state = "menu"
                        continue

                    current_results = resp.get("sources", [])[:15]
                    if not current_results:
                        if not safe_send(client_sock, "No results.\n"):
                            break
                        view_state = "menu"
                    else:
                        if not safe_send(client_sock, format_sources_list(current_results)):
                            break
                        view_state = "select_source"

                elif view_state == "src_country_input":
                    if request not in ALLOWED_COUNTRIES:
                        if not safe_send(client_sock, f"Invalid country. Allowed: {', '.join(sorted(ALLOWED_COUNTRIES))}\n"):
                            break
                        view_state = "menu"
                        continue

                    resp = fetch_sources_by_country(request)
                    write_json_file(user_name, pending_option_tag or "2.2", resp)

                    if send_api_error_if_any(resp, client_sock):
                        view_state = "menu"
                        continue

                    current_results = resp.get("sources", [])[:15]
                    if not current_results:
                        if not safe_send(client_sock, "No results.\n"):
                            break
                        view_state = "menu"
                    else:
                        if not safe_send(client_sock, format_sources_list(current_results)):
                            break
                        view_state = "select_source"

                elif view_state == "src_language_input":
                    if request not in ALLOWED_LANGUAGES:
                        if not safe_send(client_sock, f"Invalid language. Allowed: {', '.join(sorted(ALLOWED_LANGUAGES))}\n"):
                            break
                        view_state = "menu"
                        continue

                    resp = fetch_sources_by_language(request)
                    write_json_file(user_name, pending_option_tag or "2.3", resp)

                    if send_api_error_if_any(resp, client_sock):
                        view_state = "menu"
                        continue

                    current_results = resp.get("sources", [])[:15]
                    if not current_results:
                        if not safe_send(client_sock, "No results.\n"):
                            break
                        view_state = "menu"
                    else:
                        if not safe_send(client_sock, format_sources_list(current_results)):
                            break
                        view_state = "select_source"

                elif view_state == "select_source":
                    if request.upper() == "B":
                        view_state = "menu"
                    else:
                        show_source_by_index(request, current_results, client_sock)

    finally:
        try:
            client_sock.close()
        except:
            pass
        print(f"========== End of thread id:{client_id} ==========")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(3)
        print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

        client_id = 0
        while True:
            client_sock, client_addr = s.accept()
            client_id += 1
            print(f"[ACCEPTED] {client_addr}")

            t = threading.Thread(target=handle_client, args=(client_sock, client_addr, client_id), daemon=True)
            t.start()


if __name__ == "__main__":
    start_server()






     