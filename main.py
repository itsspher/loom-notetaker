from unittest import result
import kivy
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.widget import Widget 
from kivy.base import runTouchApp
from kivy.lang import Builder

# from tkinter import *
from tkinter import Tk
from tkinter import filedialog
from tkinter import messagebox

import os
import shutil

from scandir import match_direct, match_soft

# current: variable storing currently opened file path, to be accessed across functions
global current
current = False
global contents
contents = ""
global layouts
layouts = None


def update_opened_note():
    layouts.ids.file_open.text = current
    layouts.ids.text_input.text = contents


class FileChoose(Popup):
    load = ObjectProperty()


class SearchResult(Button):
    name = StringProperty('')
    directory = StringProperty('')
    file = None

    def __init__(self, name="", dir=""):
        super(Button, self).__init__()
        self.name = name
        self.directory = dir

    def click(self):
        print("Displaying", self.name)
        Tk().withdraw()
        path = self.directory
        if path:
            global current
            current = path
            file = open(path, 'r')
            global contents
            contents = file.read()
            update_opened_note()
            file.close()


class MyGridLayout(Widget):

    # PROPERTIES        ===============================================

    file_path = StringProperty("No file chosen")
    text_input = ObjectProperty()
    popup = ObjectProperty()

    # FILE OPERATIONS   ===============================================

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            self.ids.text_input.text = stream.read()
        self.popup.dismiss()
    

    def open(self):
        Tk().withdraw()
        path = filedialog.askopenfilename()
        self.file_path = path
        if path:
            global current
            current = path
            self.ids.file_open.text = "Editing: " + path #shows what file is currently open
            file = open(path, 'r')
            contents = file.read()
            file.close()
            self.ids.text_input.text = contents


    def delete(self):
        Tk().withdraw()
        self.ids.text_input.text = ""

        global current
        if os.path.isfile(current):
            os.remove(current)
            messagebox.showinfo("Delete", "File successfully deleted.")
            self.ids.file_open.text = "No Open File" 


    def saveAs(self):
        Tk().withdraw() # hide tkinter window
        path = filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("All Files","*.*"),("Text Documents","*.txt")])
        if path:
            file = open(path, 'w')
            file.write(self.ids.text_input.text)
            messagebox.showinfo("Save As", "File successfully saved.")

        global current
        current = path


    def new(self):
        # first clear contents
        self.ids.text_input.text = ""

        # reset current to FALSE so that save will trigger as saveA
        #current = False

        # functionally the same as saveAs
        self.saveAs()

        self.ids.file_open.text = "Editing: " + current #shows what file is currently open


    def save(self):
        # checks whether a previously saved file is currently open
        global current
        if current:
            file = open(current, 'w')
            file.write(self.ids.text_input.text)
            file.close()
            messagebox.showinfo("Save", "File successfully saved.")
        else:
            self.saveAs()
    

    def moveFile(self):
        Tk().withdraw()
        global current
        if current:
            moveHere = filedialog.askdirectory()
            shutil.move(current, moveHere)
            current = False
            self.ids.file_open.text = "No Open File"
            self.ids.text_input.text = ""
            messagebox.showinfo("Move", "File successfully moved.")
        else:
            messagebox.showinfo("Move", "Please open a file and try again.")


    # SEARCHING         ===============================================

    # searches using NAME of notes
    def search(self):

        SEARCH_MATCH_CASE = False

        search_string = self.ids.search_bar.text
        print("Search string:", search_string)

        # Toggle between matching case and not
        match = match_soft
        if SEARCH_MATCH_CASE:
            match = match_direct
        search_space = match(search_string)

        print(search_space)

        self.ids.search_matches.text = "" 
        matches_found = 0
        matches_found = len(search_space[0])

        # clear search queries
        self.ids.search_matches.clear_widgets()

        if matches_found == 0:
            self.ids.search_matches.add_widget(Label(text="No matches found"))
        else:
            for i in range(matches_found):
                name = search_space[0][i]
                dir = search_space[1][i]
                result = SearchResult(name, dir)
                self.ids.search_matches.add_widget(result)


    # ERROR INTERFACE   ===============================================

    # terminal interface to manually select what error to trigger
    def error_trigger(self):
        
        errors = ["Read-only Error", "Create File Failure"]
        print("Please select what error you wish to trigger:")

        for i in range(len(errors)):
            print('\t{0} {1}'.format(str(i), errors[i]))

        whichError = int(input("Enter the index of the error: "))
        
        if whichError in range(len(errors)):
            print("ERROR: {0}.\n".format(errors[whichError]))
        


class MyApp(App):

    def build(self):
        global layouts
        layouts = MyGridLayout()
        return layouts


if __name__ == "__main__":
    MyApp().run()
