from textual.app import App
from textual.widgets import Static

class HelloTest(App):
    def compose(self):
        yield Static("Hello, this is a test")

if __name__ == "__main__":
    app = HelloTest()
    app.run()