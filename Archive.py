from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widgets import Header, Footer, Label, TabbedContent, TabPane, Markdown, Input, Button, DataTable
import sqlite3

from library import book_search_api

#Initial connection to database, creation upon initial running of program
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

#SQL table to sort through entries, using ids from each to reduce search sizes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS book_list (
        id PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        pub_year INTEGER,
        ISBN INTEGER,
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
# Library Screen
A collection of the books that you own, as well as the ability to add or remove any books from your collection.
"""

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
                        yield Input(placeholder="Title", type="text", id="book_title_api")
                        yield Input(placeholder="Author", type="text", id="book_author_api")
                        yield Input(placeholder="ISBN", type="integer", id="book_isbn_api")
                        with Center():
                            yield Button("Search", id="book_search_api")
                            yield Button("New Search", id="book_api_reset")
                        with Center():
                            yield Label("", id="book_api_status")                        
                    with TabPane("Collection", Label("Search Through Your Personal Collection")):
                        yield Input(placeholder="Title", type="text", id="book_title_personal")
                        yield Input(placeholder="Author", type="text", id="book_author_personal")
                        yield Input(placeholder="ISBN", type="integer", id="book_isbn_personal")
                        with Center():
                            yield Button("Search", id="book_search_personal")
                            yield Button("New Search", id="book_personal_reset")
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
                book_search_api(input_title_api.value, input_author_api.value, input_isbn_api.value)
                self.query_one("#book_api_status", Label).update("Search results")

    # Navigation through the tabs
    def action_show_tab(self, tab: str) -> None:
        self.get_child_by_type(TabbedContent).active = tab

if __name__ == "__main__":
    app = Archive()
    app.run()