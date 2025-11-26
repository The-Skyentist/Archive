import requests

APIurl = "https://www.googleapis.com/books/v1/volumes"

def book_search(title = "", author = "", isbn = ""):
    params = {}
    new_params = "q="

    if len(title) != 0:
        params["intitle:"] = title
    if len(author) != 0:
        params["inauthor:"] = author
    if len(isbn) != 0:
        params["isbn:"] = isbn
    
    new_params += "+".join("{}{}".format(key,value) for key,value in params.items())

    print(new_params)
    r = requests.get(APIurl, params=new_params)
    print(r.url)

book_search("frankenstein","","123456789")