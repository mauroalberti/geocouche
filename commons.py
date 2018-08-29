
import os


def open_help_page(self):

    import webbrowser
    local_url = os.path.dirname(os.path.realpath(__file__)) + os.sep + "help" + os.sep + "help_geological_angles.html"
    local_url = local_url.replace("\\", "/")
    if not webbrowser.open(local_url):
        self.warn("Error with browser.\nOpen manually help/help_geological_angles.html")