import requests
# This script contains the functions to search for books through your collection or through Google Reads API

# Initial API URL set up
APIurl = "https://www.googleapis.com/books/v1/volumes"

# Search online for books using the API based on inputed query data
# Defaults to empty strings
def book_search(title = "", author = "", isbn = ""):
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
    results = r.json()