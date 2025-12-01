import requests
import sqlite3


# This script contains the functions to search for books through your collection or through Google Reads API

conn = sqlite3.connect("Archive.db")
cursor = conn.cursor()

# Initial API URL set up
APIurl = "https://www.googleapis.com/books/v1/volumes"

# Search online for books using the API based on inputed query data
# Defaults to empty strings
def book_search_api(title = "", author = "", isbn = ""):
    params = {}
    new_params = "q="

    # Create API URL based on inputs
    if len(title) != 0:
        params["intitle:"] = title
    if len(author) != 0:
        params["inauthor:"] = author
    if len(isbn) != 0:
        params["isbn:"] = isbn
    
    new_params += "+".join("{}{}".format(key,value) for key,value in params.items())

    r = requests.get(APIurl, params=new_params)
    return r.json()

def book_api_search_results(search_json):
    search_title = []
    search_author = []
    search_pub = []
    search_isbn10 = []
    search_isbn13 = []
    try:
        if search_json and "items" in search_json:
            for item in search_json["items"]:
                volume_info = item.get("volumeInfo")
                book_title = volume_info.get("title")
                book_authors = ", ".join(volume_info.get("authors"))
                book_published = volume_info.get("publishedDate")
                identifiers = volume_info.get("industryIdentifiers", [])
                for identifier in identifiers:
                    if identifier.get("type") == "ISBN_13":
                        search_isbn13.append(identifier.get("identifier"))
                    elif identifier.get("type") == "ISBN_10":
                        search_isbn10.append(identifier.get("identifier"))
                search_title.append(book_title)
                search_author.append(book_authors)
                search_pub.append(book_published)
        return list(zip(search_title, search_author, search_pub, search_isbn13, search_isbn10))
    except Exception as e:
        return e
