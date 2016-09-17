#!/usr/bin/kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

class kvLanguage(Widget):
    pass

class kvLanguageApp(App):
    def build(self):
        return kvLanguage()

if __name__ == '__main__':
    kvLanguageApp().run()