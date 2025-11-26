from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, TabbedContent, TabPane, Markdown
import sqlite3

#Initial connection to database, creation upon initial running of program
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

#SQL tables to sort through entries, using ids from each to reduce search sizes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY,
        type TEXT NOT NULL
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        pub_year INTEGER,
        genre TEXT,
        ISBN INTEGER,
        FOREIGN KEY (genre)
        REFERENCES genres(type)
    );
''')

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
This is a test of the library screen
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
                    yield TabPane("Book Search", Label("Find Book"))
                    yield TabPane("Collection", Label("Search Through Personal Collection"))

    # Navigation through the tabs
    def action_show_tab(self, tab: str) -> None:
        self.get_child_by_type(TabbedContent).active = tab

if __name__ == "__main__":
    app = Archive()
    app.run()