from textual.app import App, ComposeResult
from textual.containers import Center, VerticalScroll, ScrollableContainer
from textual.widgets import Header, Footer, Label, TabbedContent, TabPane, Markdown, Input, Button, DataTable
import sqlite3

from library import book_search_api

#Initial connection to database, creation upon initial running of program
conn = sqlite3.connect("Archive.db")
cursor = conn.cursor()

#SQL table to sort through entries, using ids from each to reduce search sizes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS book_list (
        id PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        pub_year INTEGER,
        ISBN INTEGER
    );
''')

# Main tab text and organization set-up
HOME = """
# ARCHIVE
Welcome to the Archive application! This is a tool that can be used to organize 
and sort through your owned media (books, movies, games, etc.) to help keep 
track of your collection.

Please use the tabs to navigate between menus. As well, the hotkeys listed below 
will also move between the tabs.

To exit, please press ctrl+c
"""

LIBRARY = """
# The Library
A collection of the books that you own, as well as the ability to add or remove any books from your collection.
"""

BOOK_SEARCH = [("Title", "Author", "Published", "ISBN10", "ISBN13")]

# Textual terminal app set-up and declaration. The structure is designed around a tabbed terminal, where each window of the terminal
# is a different archive section that can be utilized. Each tab is hotkeyed, which is displayed in the footer.
class Archive(App):

    # Footer key bindings for easier navigation around terminal
    BINDINGS = [
        ("h", "show_tab('home')", "Home"),
        ("l", "show_tab('library')", "Library"),
    ]

    def compose(self) -> ComposeResult:
        # Composing the app with tabbed content
        # Footer to show keys
        yield Footer()
        yield Header()
        book_api_table = DataTable(id="book_api_search_table")
        book_table = DataTable(id="book_personal_search_table")
        book_table.add_columns(*BOOK_SEARCH[0])
        book_table.zebra_stripes = True

        def on_mount(self) -> None:
            self.title = "Archive"

        # Adding tabbed content
        with TabbedContent(initial="home"): # Sets the home tab as the initial starting point

            # The home screen page, containing text as to how to navigate and exit
            with TabPane("Home", id="home"):
                yield Markdown(HOME)
            
            # The library tab, used to sort books
            with TabPane("Library", id="library"):
                yield Markdown(LIBRARY)

                # Sub tabs to search online for a book to add, or to search through your own collection
                with TabbedContent("Book Search", "Collection"):
                    with TabPane("Book Search", Label("Find a Book Through an Online Search")):
                        yield ScrollableContainer(
                            Input(placeholder="Title", type="text", id="book_title_api"),
                            Input(placeholder="Author", type="text", id="book_author_api"),
                            Input(placeholder="ISBN", type="text", id="book_isbn_api"),
                            Center(Button("Search", id="book_search_api")),
                            Center(Label("", id="book_api_status")),
                            book_api_table,
                            Center(Label("", id="book_api_search_error1")),
                            Center(Label("", id="book_api_search_error2"))
                            )
                            
                    with TabPane("Collection", Label("Search Through Your Personal Collection")):
                        yield Input(placeholder="Title", type="text", id="book_title_personal")
                        yield Input(placeholder="Author", type="text", id="book_author_personal")
                        yield Input(placeholder="ISBN", type="integer", id="book_isbn_personal")
                        with Center():
                            yield Button("Search", id="book_search_personal")
                        with Center():
                            yield Label("", id="book_personal_status")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "book_search_api":
            input_title_api = self.query_one("#book_title_api", Input)
            input_author_api = self.query_one("#book_author_api", Input)
            input_isbn_api = self.query_one("#book_isbn_api", Input)

            if input_title_api.value == "" and input_author_api.value == "" and input_isbn_api.value == "":
                self.query_one("#book_api_status", Label).update("Please input a minimum of a title, an author, or an ISBN number to search")
            else:
                self.update_book_search_api()
                self.query_one("#book_api_status", Label).update("Search results")
                self.query_one("#book_api_search_error1", Label).update("")
    
    def update_book_search_api(self) -> None:
        book_table = self.query_one("#book_api_search_table", DataTable)
        book_table.clear(columns=True)
        input_title_api = self.query_one("#book_title_api", Input)
        input_author_api = self.query_one("#book_author_api", Input)
        input_isbn_api = self.query_one("#book_isbn_api", Input)
        search_title = []
        search_author = []
        search_pub = []
        search_isbn10 = []
        search_isbn13 = []

        try:
            search_results = book_search_api(input_title_api.value, input_author_api.value, input_isbn_api.value)
            if search_results and "items" in search_results:
                for item in search_results["items"]:
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

            book_table.add_columns(*BOOK_SEARCH[0])
            book_table.add_rows(list(zip(search_title, search_author, search_pub, search_isbn10, search_isbn13))[0:])
            book_table.zebra_stripes = True
            book_table.cursor_type = "row"
        except Exception as e:
            self.query_one("#book_api_search_error1", Label).update(f"An unexpected error occured: {e}") 
            self.query_one("#book_api_search_error1", Label).update("There may be a missing value in the API search. Please be more specific.")

    # Navigation through the tabs
    def action_show_tab(self, tab: str) -> None:
        self.get_child_by_type(TabbedContent).active = tab

if __name__ == "__main__":
    app = Archive()
    app.run()