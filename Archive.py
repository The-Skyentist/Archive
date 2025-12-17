from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, Container
from textual.screen import ModalScreen
from textual.reactive import reactive
from textual.widgets import Header, Footer, Label, TabbedContent, TabPane, Markdown, Input, Button, DataTable
from textual import on
import sqlite3

from library import book_search_api, book_api_search_results

#Initial connection to database, creation upon initial running of program
conn = sqlite3.connect("Archive.db")
cursor = conn.cursor()

#SQL table to sort through entries, using ids from each to reduce search sizes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS book_list (
        id PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        pub_year TEXT,
        ISBN13 TEXT,
        ISBN10 TEXT
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

BOOK_SEARCH = [("Title", "Author", "Published", "ISBN13", "ISBN10")]

class Add_Screen(ModalScreen):

    CSS = """
    Add_Screen {
        align: center middle;
    }

    Add_Screen > Container {
        width: auto;
        height: auto;
        border: thick $background 80%;
        background: $surface;
    }

    Add_Screen > Container > Label {
        width: 100%;
        content-align-horizontal: center;
        margin-top: 1;
    }

    Add_Screen > Container > Horizontal {
        width: auto;
        height: auto;
    }

    Add_Screen > Container > Horizontal > Button {
        margin: 2 4;
    }
    """
    def __init__(self, book):
        self.book = book
        super().__init__()
    

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Add book to your collection?")
            yield Label(f"{self.book}", id = "book_info")
            with Horizontal():
                yield Button("Yes", id = "add_api_book")
                yield Button("No", id = "cancel_api_book")

    @on(Button.Pressed, "#add_api_book")
    def add_api_book(self) -> None:
        self.query_one("#book_info", Label).update("Test Successful")

    @on(Button.Pressed, "#cancel_api_book")
    def cancel_api_book(self) -> None:
        self.app.pop_screen()

# Textual terminal app set-up and declaration. The structure is designed around a tabbed terminal, where each window of the terminal
# is a different archive section that can be utilized. Each tab is hotkeyed, which is displayed in the footer.
class Archive(App):

    # Footer key bindings for easier navigation around terminal
    BINDINGS = [
        ("h", "show_tab('home')", "Home"),
        ("l", "show_tab('library')", "Library"),
        ("a", "add_book", "Add Book")
    ]

    CSS = """
    TabbedContent, DataTable {
        height: 1fr
    }
    """
    book_row_info = reactive("")

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
        with TabbedContent(initial = "home", id = "archive"): # Sets the home tab as the initial starting point
            
            # The home screen page, containing text as to how to navigate and exit
            with TabPane("Home", id="home"):
                yield Markdown(HOME)
            
            # The library tab, used to sort books
            with TabPane("Library", id="library"):
                yield Markdown(LIBRARY)

                # Sub tabs to search online for a book to add, or to search through your own collection
                with TabbedContent("Book Search", "Collection"):
                    with TabPane("Book Search", Label("Find a Book Through an Online Search"), id = "apibook_tab"):
                        yield Input(placeholder="Title", type="text", id="book_title_api")
                        yield Input(placeholder="Author", type="text", id="book_author_api")
                        yield Input(placeholder="ISBN", type="text", id="book_isbn_api")
                        yield Center(Button("Search", id="book_search_api"))
                        yield Center(Label("", id="book_api_status"))
                        yield Center(Label("", id="book_api_search_error"))
                        yield book_api_table
                            
                    with TabPane("Collection", Label("Search Through Your Personal Collection"), id = "personalbook_tab"):
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
            self.query_one("#book_api_search_error", Label).update("") 

            if input_title_api.value == "" and input_author_api.value == "" and input_isbn_api.value == "":
                self.query_one("#book_api_status", Label).update("Please input a minimum of a title, an author, or an ISBN number to search")
            else:
                self.update_book_search_api()
                self.query_one("#book_api_status", Label).update("Search results")
    
    def update_book_search_api(self) -> None:
        book_table = self.query_one("#book_api_search_table", DataTable)
        book_table.clear(columns=True)
        input_title_api = self.query_one("#book_title_api", Input)
        input_author_api = self.query_one("#book_author_api", Input)
        input_isbn_api = self.query_one("#book_isbn_api", Input)
        search_input = book_search_api(input_title_api.value, input_author_api.value, input_isbn_api.value)
        search_results = book_api_search_results(search_input)
        if type(search_results) == TypeError:
            self.query_one("#book_api_status", Label).update(f"An unexpected error occured: {search_results}") 
            self.query_one("#book_api_search_error2", Label).update("There may be a missing value in the API search. Please be more specific.")
        else:
            book_table.add_columns(*BOOK_SEARCH[0])
            book_table.add_rows(search_results[0:])
            book_table.zebra_stripes = True
            book_table.cursor_type = "row"

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one("#book_api_search_table", DataTable)
        self.book_row_info = table.get_row(event.row_key)
    
    # Navigation through the tabs
    def action_show_tab(self, tab: str) -> None:
        self.get_child_by_type(TabbedContent).active = tab
    
    def action_add_book(self) -> None:
        if self.book_row_info == "":
            self.push_screen(Add_Screen("Please select a book to add."))
        else:
            self.push_screen(Add_Screen(self.book_row_info))
        
if __name__ == "__main__":
    app = Archive()
    app.run()