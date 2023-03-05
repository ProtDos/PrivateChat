# KivyMD
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.toast import toast  # for sending toast messages

# Kivy
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.clock import mainthread
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty  # for chat screen, displaying speech bubbles
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

# Cryptography
import base64  # For encrypting messages
from cryptography.fernet import Fernet  # For encrypting messages
from cryptography.hazmat.backends import default_backend  # For encrypting messages
from cryptography.hazmat.primitives import hashes  # For encrypting messages
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # For encrypting messages
import rsa as rr
import rsa
import hashlib

# Voice
# import pyaudio
try:
    import sounddevice as sd
except:
    pass

# Other
import threading  # Threaded tasks
import socket  # To connect to the server
import string  # Generating strong keys
import os  # Clearing the terminal window
import uuid  # Generating unique IDs
from password_strength import PasswordPolicy  # Checking security of password
import secrets  # creating strong keys (real randomness)
import time  # sleep function
from plyer import filechooser, notification  # File Choosing to send them to others, sending notifications
import qrcode  # creating QR-Codes (for the keys)
from kivy.core.clipboard import Clipboard
import requests
from PIL import Image as IImage
import numpy as np

"""
- Encrypt Private Messaging
    - https://www.youtube.com/watch?v=U_Q1vqaJi34&t=1070s
    - use private and public key, maybe store in database (public key)
- Check if messages come when being offline

Done...
"""

""" CHANGELOG
- Change MD5 Hash algo to SHA256
"""

login = """
MDScreen:
    name: "login"
    username: username
    password: password
    pws1: pws1
    
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "main"
        MDLabel:
            text: "W e l c o m e !"
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Sign in to continue"
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)
        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .63}
            TextInput:
                id: username
                hint_text: "Username"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)

        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .5}
            TextInput:
                id: password
                hint_text: "Password"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
                password: True
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)
            MDIconButton:
                id: pws1
                icon: "eye"
                color: 0, 0, 0, 0.4
                text_color: 0, 0, 0, 0.4
                theme_text_color: "Custom"
                pos_hint: {"center_x": .85, "center_y": .5}
                on_release:
                    app.show_password()

        Button:
            text: "LOGIN"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .34}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]
            on_release:
                app.login(username.text, password.text)
                #root.manager.transition.direction = "left"
                #root.manager.current = "chat"
        MDTextButton:
            text: "Forgot Password?"
            pos_hint: {"center_x": .5, "center_y": .28}
            color: rgba(68, 78, 132, 255)
            font_size: "12sp"
            font_name: "BPoppins"
            on_release:
                root.manager.transition.direction = "left"
                root.manager.current = "password_reset"
        MDLabel:
            text: "Don't have an account?"
            font_name: "BPoppins"
            font_size: "11sp"
            pos_hint: {"center_x": .68, "center_y": .2}
            color: rgba(135, 133, 193, 255)
        MDTextButton:
            text: "Sign up"
            font_name: "BPoppins"
            font_size: "11sp"
            pos_hint: {"center_x": .75, "center_y": .2}
            color: rgba(135, 133, 193, 255)
            on_release:
                root.manager.transition.direction = "left"
                root.manager.current = "signup"
"""
home = """
#: import get_color_from_hex kivy.utils.get_color_from_hex
#: import webbrowser webbrowser

#: import TwoLineListItem kivymd.uix.list.TwoLineListItem
#: import Window kivy.core.window.Window

MDScreen:
    name: "home"
    username_icon: username_icon
    password_icon: password_icon
    text_input2: text_input2
    text_input3: text_input3
    welcome_name: welcome_name

    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1


        MDBottomAppBar:
            title: 'Bottom navigation'
            md_bg_color: .2, .2, .2, 1
            specific_text_color: 1, 1, 1, 1

        MDBottomNavigation:
            panel_color: 1, 1, 1, 1

            MDBottomNavigationItem:
                name: "home"
                text: "Home"
                icon: "home"

                MDLabel:
                    id: welcome_name
                    text: "Welcome"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .8}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                Button:
                    text: "Start chatting"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .65}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "chat_private"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [5]
                Button:
                    text: "Groups"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .55}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "group"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
                Button:
                    text: "Load"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .45}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        app.load_all()
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
                Button:
                    text: "My ID"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .15}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        app.show_id()
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

                MDIconButton:
                    icon: "logout"
                    pos_hint: {"center_x": .9, "center_y": .05}
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "main"


            MDBottomNavigationItem:
                name: "test"
                text: "Chats"
                icon: "chat"

                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .95}
                    user_font_size: "30sp"
                    theme_text_color: "Custom"
                    text_color: rgba(26, 24, 58, 255)
                    on_release:
                        root.manager.transition.direction = "right"
                        root.manager.current = "home"

                MDLabel:
                    text: "Chats"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .8}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                Button:
                    text: "Start chatting"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .65}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "chat_private"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [5]
                Button:
                    text: "Load chats"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .55}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "chat_load"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

            MDBottomNavigationItem:
                name: "test2"
                text: "Settings"
                icon: "account-settings"

                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .95}
                    user_font_size: "30sp"
                    theme_text_color: "Custom"
                    text_color: rgba(26, 24, 58, 255)
                    on_release:
                        root.manager.transition.direction = "right"
                        root.manager.current = "main"

                MDLabel:
                    text: "Settings"
                    font_name: "BPoppins"
                    font_size: "26sp"
                    pos_hint: {"center_x": .6, "center_y": .85}
                    color: rgba(0, 0, 59, 255)

                MDFloatLayout:
                    size_hint_y: .11
                    MDFloatLayout:
                        size_hint: .8, .75
                        pos_hint: {"center_x": .43, "center_y": 7}
                        TextInput:
                            id: text_input2
                            hint_text: "Set a new username"
                            size_hint: 1, None
                            pos_hint: {"center_x": .5, "center_y": .5}
                            font_size: "12sp"
                            height: self.minimum_height
                            multiline: False
                            cursor_color: 1, 170/255, 23/255, 1
                            cursor_width: "2sp"
                            background_color: 0, 0, 0, 0
                            padding: 15
                            font_name: "BPoppins"
                    MDIconButton:
                        id: username_icon
                        icon: "account-cog"
                        pos_hint: {"center_x": .91, "center_y": 7}
                        user_font_size: "12sp"
                        text_color: 1, 1, 1, 1
                        on_release:
                            app.change_username(text_input2.text)

                MDFloatLayout:
                    size_hint_y: .11
                    MDFloatLayout:
                        size_hint: .8, .75
                        pos_hint: {"center_x": .43, "center_y": 6}
                        TextInput:
                            id: text_input3
                            hint_text: "Set a new password"
                            size_hint: 1, None
                            pos_hint: {"center_x": .5, "center_y": .5}
                            font_size: "12sp"
                            height: self.minimum_height
                            multiline: False
                            cursor_color: 1, 170/255, 23/255, 1
                            cursor_width: "2sp"
                            background_color: 0, 0, 0, 0
                            padding: 15
                            font_name: "BPoppins"
                    MDIconButton:
                        id: password_icon
                        icon: "account-cog"
                        pos_hint: {"center_x": .91, "center_y": 6}
                        user_font_size: "12sp"
                        text_color: 1, 1, 1, 1
                        on_release:
                            app.change_password(text_input3.text)
                Button:
                    text: "Delete Everything"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .35}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(240, 40, 40, 255)
                    on_release:
                        app.delete_everything()
                    canvas.before:
                        Color:
                            rgb: rgba(240, 40, 40, 255)
                            # rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
                Button:
                    text: "Secret"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .25}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:                       
                        root.manager.transition.direction = "left"
                        root.manager.current = "home_secret"
                        # app.show_toaster("Not ready yet.")
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
            
            MDBottomNavigationItem:
                name: "call_bar"
                text: "Call"
                icon: "phone"
                
                MDLabel:
                    text: "Encrypted Call"
                    font_name: "BPoppins"
                    font_size: "26sp"
                    pos_hint: {"center_x": .6, "center_y": .85}
                    color: rgba(0, 0, 59, 255)
                
                Button:
                    text: "Call Someone"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .45}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "call"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100


            MDBottomNavigationItem:
                name: "test3"
                text: "Help"
                icon: "help-circle"

                MDLabel:
                    text: "Help"
                    font_name: "BPoppins"
                    font_size: "26sp"
                    pos_hint: {"center_x": .6, "center_y": .85}
                    color: rgba(0, 0, 59, 255)

                MDLabel:
                    text: "Found a bug or improvements?"
                    font_name: "BPoppins"
                    font_size: "11sp"
                    pos_hint: {"center_x": .68, "center_y": .75}
                    color: rgba(0, 0, 59, 255)
                MDTextButton:
                    text: "Contact Us"
                    font_name: "BPoppins"
                    font_size: "11sp"
                    pos_hint: {"center_x": .68, "center_y": .7}
                    color: rgba(135, 133, 193, 255)
                    on_release:
                        webbrowser.open("https://protdos.com/contact.html")

                MDLabel:
                    text: "Contact us"
                    font_name: "BPoppins"
                    font_size: "11sp"
                    pos_hint: {"center_x": .68, "center_y": .55}
                    color: rgba(0, 0, 59, 255)
                MDTextButton:
                    text: "Mail Us"
                    font_name: "BPoppins"
                    font_size: "11sp"
                    pos_hint: {"center_x": .68, "center_y": .5}
                    color: rgba(135, 133, 193, 255)
                    on_release:
                        webbrowser.open("mailto:rootcode@duck.com")
"""
chat_private = """
MDScreen:
    name: "chat_private"
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "home"
        MDLabel:
            text: "Chat"
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Start Chatting"
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)
        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .63}
            TextInput:
                id: name
                hint_text: "Recipient"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)

        Button:
            text: "Chat"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .34}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]
            on_release:
                app.create_chat(name.text)
"""
chat_sec = """
#:import Clipboard kivy.core.clipboard.Clipboard
<Command2>
    size_hint_y: None
    pos_hint: {"right": .98}
    height: self.texture_size[1]
    padding: 12, 10
    theme_text_color: "Custom"
    canvas.before:
        Color:
            rgb: rgba(52, 0, 234, 255)
        RoundedRectangle:
            size: self.width, self.height
            pos: self.pos
            radius: [23, 23, 0, 23]
            on_touch_down:
                app.message_click()
<Response2>
    size_hint_y: None
    pos_hint: {"x": .02}
    height: self.texture_size[1]
    padding: 12, 10
    theme_text_color: "Custom"
    #text_color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgb: (1, 1, 1, 1)
        RoundedRectangle:
            size: self.width, self.height
            pos: self.pos
            radius: [23, 23, 23, 0]
<AddImage>
    size_hint_y: None
    pos_hint: {"x": .02}
    height: 70
    theme_text_color: "Custom"
    
MDScreen:
    name: "chat_sec"
    kkk: kkk
    bot_name: bot_name
    chat_list: chat_list
    text_input: text_input

    MDFloatLayout:
        MDFloatLayout:
            md_bg_color: 245/255, 245/255, 245/255, 1
            size_hint_y: .11
            pos_hint: {"center_y": .95}
            MDIconButton:
                icon: "arrow-left"
                pos_hint: {"center_y": .5}
                user_font_size: "30sp"
                theme_text_color: "Custom"
                text_color: rgba(26, 24, 58, 255)
                on_release:
                    root.manager.transition.direction = "right"
                    root.manager.current = "home"
            MDIconButton:
                icon: "content-copy"
                pos_hint: {"center_x": .9, "center_y": .5}
                on_release:
                    Clipboard.copy(kkk.text)
                    app.show_qr_code2(kkk.text)

            MDLabel:
                text: ""
                id: bot_name
                pos_hint: {"center_y": .5}
                halign: "center"
                font_name: "BPoppins"
                font_size: "25sp"
                theme_text_color: "Custom"
                text_color: 53/255, 56/255, 60/255, 1
            MDLabel:
                text: ""
                id: kkk
                pos_hint: {"center_y": .5}
                halign: "center"
                font_name: "BPoppins"
                font_size: "0sp"
                theme_text_color: "Custom"
                text_color: 53/255, 56/255, 60/255, 1
                opacity: 0




        ScrollView:
            size_hint_y: .77
            pos_hint: {"x": 0, "y": .116}
            do_scroll_x: False
            do_scroll_y: True
            BoxLayout:
                id: chat_list
                orientation: "vertical"
                size: (root.width, root.height)
                height: self.minimum_height
                size_hint: None, None
                pso_hint: {"top": 10}
                cols: 1
                spacing: 5
        MDFloatLayout:
            md_bg_color: 245/255, 245/255, 245/255, 1
            size_hint_y: .11
            MDFloatLayout:
                size_hint: .7, .60
                pos_hint: {"center_x": .45, "center_y": .5}
                canvas:
                    Color:
                        rgb: (238/255, 238/255, 238/255, 1)
                    RoundedRectangle:
                        size: self.size
                        pos: self.pos
                        radius: [23, 23, 23, 23]
                TextInput:
                    id: text_input
                    hint_text: "Type something..."
                    size_hint: 1, None
                    pos_hint: {"center_x": .5, "center_y": .5}
                    font_size: "12sp"
                    height: self.minimum_height
                    multiline: False
                    cursor_color: 1, 170/255, 23/255, 1
                    cursor_width: "2sp"
                    foreground_color: 1, 170/255, 23/255, 1
                    background_color: 0, 0, 0, 0
                    padding: 15
                    font_name: "BPoppins"
            MDIconButton:
                icon: "send"
                pos_hint: {"center_x": .91, "center_y": .5}
                user_font_size: "18sp"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                #foreground_color: rgba(0, 0, 0, 1)
                #md_bg_color: rgba(52, 0, 231, 255)
                on_release:
                    app.send_message_private(text_input.text, kkk.text)
            #MDIconButton:
            #    icon: "file-upload"
            #    pos_hint: {"center_x": .8, "center_y": .5}
            #    user_font_size: "18sp"
            #    theme_text_color: "Custom"
            #    text_color: 0, 0, 0, 1
            #    #md_bg_color: rgba(52, 0, 231, 255)
            #    on_release:
            #        app.file_chooser(kkk.text)

"""
main = """
MDScreen:
    name: "main"
    MDFloatLayout:

        md_bg_color: 1, 1, 1, 1
        #Image:
        #     source: "logo.png"
        #    pos_hint: {"center_x": .19, "center_y": .95}
        Image:
            source: "front.png"
            size_hint: .8, .8
            pos_hint: {"center_x": .5, "center_y": .65}
        MDLabel:
            text: "PrivChat"
            font_name: "BPoppins"
            font_size: "23sp"
            pos_hint: {"center_y": .38}
            halign: "center"
            color: rgba(34, 34, 34, 255)
        MDLabel:
            text: "The most secure chat app available."
            font_name: "BPoppins"
            font_size: "13sp"
            size_hint_x: .85
            pos_hint: {"center_x": .5, "center_y": .3}
            halign: "center"
            color: rgba(127, 127, 127, 255)
        Button:
            text: "LOGIN"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .18}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            on_release:
                root.manager.transition.direction = "left"
                root.manager.current = "login"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]
        Button:
            text: "SIGNUP"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .09}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(52, 0, 231, 255)
            on_release:
                root.manager.transition.direction = "left"
                root.manager.current = "signup"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

"""
group_create = """
MDScreen:
    name: "group_create"
    name_: name_
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "home"
        MDLabel:
            text: "Group"
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Create a group"
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)
        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .63}
            TextInput:
                id: name_
                hint_text: "Group Name"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)

        Button:
            text: "Create"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .34}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]
            on_release:
                app.create_group(name_.text)


"""
group_join = """
MDScreen:
    name: "group_join"
    group_list: group_list
    ok: ok
    group_num: group_num
    butt: butt

    MDLabel:
        text: "Groups"
        font_name: "BPoppins"
        font_size: "26sp"
        pos_hint: {"center_x": .8, "center_y": .9}
        color: rgba(0, 0, 59, 255)

    MDIconButton:
        icon: "arrow-left"
        pos_hint: {"center_y": .95}
        user_font_size: "30sp"
        theme_text_color: "Custom"
        text_color: rgba(26, 24, 58, 255)
        on_release:
            root.manager.transition.direction = "right"
            root.manager.current = "home"

    MDLabel:
        id: ok
        pos_hint: {"center_x": .5, "center_y": .7}
        halign: "center"

    ScrollView:
        size_hint_y: .6
        pos_hint: {"x": 0, "y": .116}
        do_scroll_x: False
        do_scroll_y: True
        BoxLayout:
            id: group_list
            orientation: "vertical"
            size: (root.width, root.height)
            height: self.minimum_height
            size_hint: None, None
            pso_hint: {"top": 10}
            cols: 1
            spacing: 5
            size_hint_y: None
            pos_hint: {"x": .02}
            padding: 12, 10

    MDFloatLayout:
        md_bg_color: 245/255, 245/255, 245/255, 1
        size_hint_y: .11
        MDFloatLayout:
            size_hint: .7, .60
            pos_hint: {"center_x": .45, "center_y": .5}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [23, 23, 23, 23]
            TextInput:
                input_filter: "int"
                id: group_num
                hint_text: "Enter group number"
                size_hint: 1, None
                pos_hint: {"center_x": .5, "center_y": .5}
                font_size: "12sp"
                height: self.minimum_height
                multiline: False
                cursor_color: 1, 170/255, 23/255, 1
                cursor_width: "2sp"
                foreground_color: 1, 170/255, 23/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_name: "BPoppins"
        MDIconButton:
            id: butt
            icon: "send"
            pos_hint: {"center_x": .91, "center_y": .5}
            user_font_size: "18sp"
            theme_text_color: "Custom"
            text_color: 0, 0, 0, 1
            #foreground_color: rgba(0, 0, 0, 1)
            #md_bg_color: rgba(52, 0, 231, 255)
            on_release:
                app.join_group(group_num.text)



    Button:
        text: "New"
        size_hint: .3, .065
        pos_hint: {"center_x": .7, "center_y": .8}
        background_color: 0, 0, 0, 0
        front_name: "BPoppins"
        canvas.before:
            Color:
                rgb: rgba(52, 0, 231, 255)
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: [5]
        on_release:
            root.manager.transition.direction = "left"
            root.manager.current = "new_group_join"
    Button:
        text: "Load"
        size_hint: .3, .065
        pos_hint: {"center_x": .3, "center_y": .8}
        background_color: 0, 0, 0, 0
        front_name: "BPoppins"
        canvas.before:
            Color:
                rgb: rgba(52, 0, 231, 255)
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: [5]
        on_release:
            app.load_groups()
"""
group = """
#: import get_color_from_hex kivy.utils.get_color_from_hex

MDScreen:
    name: "group"
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1


        MDBottomAppBar:
            title: 'Bottom navigation'
            md_bg_color: .2, .2, .2, 1
            specific_text_color: 1, 1, 1, 1

        MDBottomNavigation:
            panel_color: 1, 1, 1, 1

            MDBottomNavigationItem:
                name: "home"
                text: "Home"
                icon: "home"

                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .95}
                    user_font_size: "30sp"
                    theme_text_color: "Custom"
                    text_color: rgba(26, 24, 58, 255)
                    on_release:
                        root.manager.transition.direction = "right"
                        root.manager.current = "home"

                MDLabel:
                    text: "Group Chat"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .8}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                Button:
                    text: "Join a Group"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .65}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "group_join"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [5]
                Button:
                    text: "Create a Group"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .55}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "group_create"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

                MDIconButton:
                    icon: "logout"
                    pos_hint: {"center_x": .9, "center_y": .05}
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "main"


            MDBottomNavigationItem:
                name: "test"
                text: "Chats"
                icon: "chat"

                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .95}
                    user_font_size: "30sp"
                    theme_text_color: "Custom"
                    text_color: rgba(26, 24, 58, 255)
                    on_release:
                        root.manager.transition.direction = "right"
                        root.manager.current = "main"

                MDLabel:
                    text: "Chats"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .8}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                Button:
                    text: "Start chatting"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .65}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "chat"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [5]
                Button:
                    text: "Create new chat"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .55}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "chat"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

            MDBottomNavigationItem:
                name: "test2"
                text: "Settings"
                icon: "account-settings"

                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .95}
                    user_font_size: "30sp"
                    theme_text_color: "Custom"
                    text_color: rgba(26, 24, 58, 255)
                    on_release:
                        root.manager.transition.direction = "right"
                        root.manager.current = "main"


            MDBottomNavigationItem:
                name: "test3"
                text: "Help"
                icon: "help-circle"

                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .95}
                    user_font_size: "30sp"
                    theme_text_color: "Custom"
                    text_color: rgba(26, 24, 58, 255)
                    on_release:
                        root.manager.transition.direction = "right"
                        root.manager.current = "main"

                MDLabel:
                    text: "Help Center"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .8}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                MDLabel:
                    text: "Help Center"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .8}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                MDLabel:
                    text: "Error?"
                    font_name: "BPoppins"
                    font_size: "15sp"
                    pos_hint: {"center_y": .7}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                MDLabel:
                    text: "Coming soon..."
                    font_name: "BPoppins"
                    font_size: "18sp"
                    pos_hint: {"center_x": .6, "center_y": .65}
                    color: rgba(135, 133, 193, 255)
                MDLabel:
                    text: "Feedback"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .6}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                MDLabel:
                    text: "Bugs"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .5}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)




"""
help_ = """#: import get_color_from_hex kivy.utils.get_color_from_hex

MDScreen:
    name: "help"
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1


        MDBottomAppBar:
            title: 'Bottom navigation'
            md_bg_color: .2, .2, .2, 1
            specific_text_color: 1, 1, 1, 1

        MDBottomNavigation:
            panel_color: 1, 1, 1, 1

            MDBottomNavigationItem:
                name: "home"
                text: "Home"
                icon: "home"

                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .95}
                    user_font_size: "30sp"
                    theme_text_color: "Custom"
                    text_color: rgba(26, 24, 58, 255)
                    on_release:
                        root.manager.transition.direction = "right"
                        root.manager.current = "main"

                MDLabel:
                    id: welcome_name
                    text: "Welcome ProtDos"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .8}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                Button:
                    text: "Start chatting"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .65}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "chat"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [5]
                Button:
                    text: "Create a Group"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .55}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "group"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
                Button:
                    text: "Join a Group"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .45}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "group"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
                Button:
                    text: "Settings"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .35}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "settings"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
                Button:
                    text: "Personal"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .25}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "personal"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

                MDIconButton:
                    icon: "logout"
                    pos_hint: {"center_x": .9, "center_y": .05}
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "main"


            MDBottomNavigationItem:
                name: "test"
                text: "Chats"
                icon: "chat"

                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .95}
                    user_font_size: "30sp"
                    theme_text_color: "Custom"
                    text_color: rgba(26, 24, 58, 255)
                    on_release:
                        root.manager.transition.direction = "right"
                        root.manager.current = "main"

                MDLabel:
                    text: "Chats"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .8}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                Button:
                    text: "Start chatting"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .65}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "chat"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [5]
                Button:
                    text: "Create new chat"
                    size_hint: .66, .065
                    pos_hint: {"center_x": .5, "center_y": .55}
                    background_color: 0, 0, 0, 0
                    front_name: "BPoppins"
                    color: rgba(52, 0, 231, 255)
                    on_release:
                        root.manager.transition.direction = "left"
                        root.manager.current = "chat"
                    canvas.before:
                        Color:
                            rgb: rgba(52, 0, 231, 255)
                        Line:
                            width: 1.2
                            rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

            MDBottomNavigationItem:
                name: "test2"
                text: "Settings"
                icon: "account-settings"

                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .95}
                    user_font_size: "30sp"
                    theme_text_color: "Custom"
                    text_color: rgba(26, 24, 58, 255)
                    on_release:
                        root.manager.transition.direction = "right"
                        root.manager.current = "main"


            MDBottomNavigationItem:
                name: "test3"
                text: "Help"
                icon: "help-circle"

                MDIconButton:
                    icon: "arrow-left"
                    pos_hint: {"center_y": .95}
                    user_font_size: "30sp"
                    theme_text_color: "Custom"
                    text_color: rgba(26, 24, 58, 255)
                    on_release:
                        root.manager.transition.direction = "right"
                        root.manager.current = "main"

                MDLabel:
                    text: "Help Center"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .8}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                MDLabel:
                    text: "Help Center"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .8}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                MDLabel:
                    text: "Error?"
                    font_name: "BPoppins"
                    font_size: "15sp"
                    pos_hint: {"center_y": .7}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                MDLabel:
                    text: "Coming soon..."
                    font_name: "BPoppins"
                    font_size: "18sp"
                    pos_hint: {"center_x": .6, "center_y": .65}
                    color: rgba(135, 133, 193, 255)
                MDLabel:
                    text: "Feedback"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .6}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)
                MDLabel:
                    text: "Bugs"
                    font_name: "BPoppins"
                    font_size: "23sp"
                    pos_hint: {"center_y": .5}
                    halign: "center"
                    color: rgba(34, 34, 34, 255)



"""
new_group_join = """
MDScreen:
    name: "new_group_join"
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "home"
        MDLabel:
            text: "Group"
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Join a group"
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)
        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .63}
            TextInput:
                id: name
                hint_text: "Group Key"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)

        Button:
            text: "Join"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .34}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]
            on_release:
                app.join_new_group(name.text)


"""
password_reset = """
MDScreen:
    name: "password_reset"
    username: username
    password: password
    password2: password

    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "main"
        MDLabel:
            text: "Reset!"
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "The only way to use the app, is to create a new account. All your data you have is lost."
            font_name: "BPoppins"
            font_size: "17sp"
            pos_hint: {"center_x": .55, "center_y": .74}
            color: rgba(135, 133, 193, 255)

        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .60}
            TextInput:
                id: username
                hint_text: "Username"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)

        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .48}
            TextInput:
                id: password
                hint_text: "Password"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
                password: True
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)

        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .36}
            TextInput:
                id: password2
                hint_text: "Retype Password"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
                password: True
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)
        Button:
            text: "SIGN UP"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .22}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]
            on_release:
                app.sign_up(username.text, password.text, password2.text)
        MDLabel:
            text: "Already have an account?"
            font_name: "BPoppins"
            font_size: "11sp"
            pos_hint: {"center_x": .68, "center_y": .15}
            color: rgba(135, 133, 193, 255)
        MDTextButton:
            text: "Login"
            font_name: "BPoppins"
            font_size: "11sp"
            pos_hint: {"center_x": .79, "center_y": .15}
            color: rgba(135, 133, 193, 255)
            on_release:
                root.manager.transition.direction = "left"
                root.manager.current = "login"

"""
signup = """
#: import webbrowser webbrowser

MDScreen:
    name: "signup"
    username: username
    password: password
    password2: password2
    pws2: pws2
    pws1: pws1
    check_tos: check_tos
    
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "main"
        MDLabel:
            text: "H i !"
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Create a new account"
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)

        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .68}
            TextInput:
                id: username
                hint_text: "Username"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)

        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .56}
            TextInput:
                id: password
                hint_text: "Password"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
                password: True
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)
            MDIconButton:
                id: pws1
                icon: "eye"
                color: 0, 0, 0, 0.4
                text_color: 0, 0, 0, 0.4
                theme_text_color: "Custom"
                pos_hint: {"center_x": .85, "center_y": .5}
                on_release:
                    app.show_password_sign()

        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .44}
            TextInput:
                id: password2
                hint_text: "Retype Password"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
                password: True
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)
            MDIconButton:
                id: pws2
                icon: "eye"
                color: 0, 0, 0, 0.4
                text_color: 0, 0, 0, 0.4
                theme_text_color: "Custom"
                pos_hint: {"center_x": .85, "center_y": .44}
                on_release:
                    app.show_password_sign2()
        
        MDCheckbox:
            id: check_tos
            size_hint: None, None
            size: "48dp", "48dp"
            pos_hint: {"center_x": .15, "center_y": .37}
            on_active: app.accept_tos(*args)
            
        MDFloatLayout:
            MDLabel:
                font_name: "MPoppins"
                text: "I accept"
                font_size: "12sp"
                color: rgba(0, 0, 59, 255)
                foreground_color: rgba(0, 0, 59, 255)
                pos_hint: {"center_x": .7, "center_y": .37}
            MDTextButton:
                text: "ToS"
                font_name: "MPoppins"
                font_size: "12sp"
                color: rgba(0, 0, 238, 255)
                foreground_color: rgba(0, 0, 238, 255)
                pos_hint: {"center_x": .41, "center_y": .37}
                on_release:
                    webbrowser.open("https://protdos.com/terms-of-service.html")
        
        Button:
            text: "SIGN UP"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .30}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]
            on_release:
                app.sign_up(username.text, password.text, password2.text)
        MDTextButton:
            text: "Forgot Password?"
            pos_hint: {"center_x": .5, "center_y": .24}
            color: rgba(68, 78, 132, 255)
            font_size: "12sp"
            font_name: "BPoppins"
        MDLabel:
            text: "Already have an account?"
            font_name: "BPoppins"
            font_size: "11sp"
            pos_hint: {"center_x": .68, "center_y": .16}
            color: rgba(135, 133, 193, 255)
        MDTextButton:
            text: "Login"
            font_name: "BPoppins"
            font_size: "11sp"
            pos_hint: {"center_x": .79, "center_y": .16}
            color: rgba(135, 133, 193, 255)
            on_release:
                root.manager.transition.direction = "left"
                root.manager.current = "login"

"""
show_id = """
MDScreen:
    name: "show_id"
    img: img

    MDFloatLayout:
        MDFloatLayout:
            md_bg_color: 245/255, 245/255, 245/255, 1
            size_hint_y: .11
            pos_hint: {"center_y": .95}
            MDIconButton:
                icon: "arrow-left"
                pos_hint: {"center_y": .5}
                user_font_size: "30sp"
                theme_text_color: "Custom"
                text_color: rgba(26, 24, 58, 255)
                on_release:
                    root.manager.transition.direction = "right"
                    root.manager.current = "home"
        MDLabel:
            text: "Your Personal ID"
            font_name: "BPoppins"
            font_size: "23sp"
            pos_hint: {"center_y": .8}
            halign: "center"
            color: rgba(34, 34, 34, 255)
        MDLabel:
            text: "Let others scan it to contact you. Your ID is also copied to your clipboard."
            font_name: "BPoppins"
            font_size: "13sp"
            size_hint_x: .85
            pos_hint: {"center_x": .5, "center_y": .3}
            halign: "center"
            color: rgba(127, 127, 127, 255)
        Image:
            id: img
            source: "qr_code_id.png"
            size_hint: (None, None)
            size: 200, 200
            pos_hint: {"center_y": .55, "center_x": .5}
"""
show_id2 = """
MDScreen:
    name: "show_qr"
    img: img

    MDFloatLayout:
        MDFloatLayout:
            md_bg_color: 245/255, 245/255, 245/255, 1
            size_hint_y: .11
            pos_hint: {"center_y": .95}
            MDIconButton:
                icon: "arrow-left"
                pos_hint: {"center_y": .5}
                user_font_size: "30sp"
                theme_text_color: "Custom"
                text_color: rgba(26, 24, 58, 255)
                on_release:
                    root.manager.transition.direction = "right"
                    root.manager.current = "chat"
        MDLabel:
            text: "Your QR-Code"
            font_name: "BPoppins"
            font_size: "23sp"
            pos_hint: {"center_y": .8}
            halign: "center"
            color: rgba(34, 34, 34, 255)
        MDLabel:
            text: "Let others scan it to get the key. The key is also copied to your clipboard."
            font_name: "BPoppins"
            font_size: "13sp"
            size_hint_x: .85
            pos_hint: {"center_x": .5, "center_y": .3}
            halign: "center"
            color: rgba(127, 127, 127, 255)
        Image:
            id: img
            source: "qr_code.png"
            size_hint: (None, None)
            size: 200, 200
            pos_hint: {"center_y": .55, "center_x": .5}
"""
show_qr2 = """
MDScreen:
    name: "show_qr2"
    img: img

    MDFloatLayout:
        MDFloatLayout:
            md_bg_color: 245/255, 245/255, 245/255, 1
            size_hint_y: .11
            pos_hint: {"center_y": .95}
            MDIconButton:
                icon: "arrow-left"
                pos_hint: {"center_y": .5}
                user_font_size: "30sp"
                theme_text_color: "Custom"
                text_color: rgba(26, 24, 58, 255)
                on_release:
                    root.manager.transition.direction = "right"
                    root.manager.current = "chat_sec"
        MDLabel:
            text: "Your QR-Code"
            font_name: "BPoppins"
            font_size: "23sp"
            pos_hint: {"center_y": .8}
            halign: "center"
            color: rgba(34, 34, 34, 255)
        MDLabel:
            text: "Let others scan it to get the key. The key is also copied to your clipboard."
            font_name: "BPoppins"
            font_size: "13sp"
            size_hint_x: .85
            pos_hint: {"center_x": .5, "center_y": .3}
            halign: "center"
            color: rgba(127, 127, 127, 255)
        Image:
            id: img
            source: "qr_code.png"
            size_hint: (None, None)
            size: 200, 200
            pos_hint: {"center_y": .55, "center_x": .5}
"""
chat_new_private = """
MDScreen:
    name: "chat_new_private"
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "home"
        MDLabel:
            text: "Chat"
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Join a private chat"
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)
        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .63}
            TextInput:
                id: name
                hint_text: "Recipient"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)

        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .53}
            TextInput:
                id: key
                hint_text: "Key"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)

        Button:
            text: "Chat"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .34}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]
            on_release:
                app.join_chat(name.text, key.text)


"""
chat_load = """
MDScreen:
    name: "chat_load"
    group_list: group_list
    ok: ok
    group_num: group_num
    butt: butt

    MDLabel:
        text: "Groups"
        font_name: "BPoppins"
        font_size: "26sp"
        pos_hint: {"center_x": .8, "center_y": .9}
        color: rgba(0, 0, 59, 255)

    MDIconButton:
        icon: "arrow-left"
        pos_hint: {"center_y": .95}
        user_font_size: "30sp"
        theme_text_color: "Custom"
        text_color: rgba(26, 24, 58, 255)
        on_release:
            root.manager.transition.direction = "right"
            root.manager.current = "home"

    MDLabel:
        id: ok
        pos_hint: {"center_x": .5, "center_y": .7}
        halign: "center"

    ScrollView:
        size_hint_y: .6
        pos_hint: {"x": 0, "y": .116}
        do_scroll_x: False
        do_scroll_y: True
        BoxLayout:
            id: group_list
            orientation: "vertical"
            size: (root.width, root.height)
            height: self.minimum_height
            size_hint: None, None
            pso_hint: {"top": 10}
            cols: 1
            spacing: 5
            size_hint_y: None
            pos_hint: {"x": .02}
            padding: 12, 10

    MDFloatLayout:
        md_bg_color: 245/255, 245/255, 245/255, 1
        size_hint_y: .11
        MDFloatLayout:
            size_hint: .7, .60
            pos_hint: {"center_x": .45, "center_y": .5}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [23, 23, 23, 23]
            TextInput:
                input_filter: "int"
                id: group_num
                hint_text: "Enter group number"
                size_hint: 1, None
                pos_hint: {"center_x": .5, "center_y": .5}
                font_size: "12sp"
                height: self.minimum_height
                multiline: False
                cursor_color: 1, 170/255, 23/255, 1
                cursor_width: "2sp"
                foreground_color: 1, 170/255, 23/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_name: "BPoppins"
        MDIconButton:
            id: butt
            icon: "send"
            pos_hint: {"center_x": .91, "center_y": .5}
            user_font_size: "18sp"
            theme_text_color: "Custom"
            text_color: 0, 0, 0, 1
            #foreground_color: rgba(0, 0, 0, 1)
            #md_bg_color: rgba(52, 0, 231, 255)
            on_release:
                app.join_group(group_num.text)



    Button:
        text: "New"
        size_hint: .3, .065
        pos_hint: {"center_x": .7, "center_y": .8}
        background_color: 0, 0, 0, 0
        front_name: "BPoppins"
        canvas.before:
            Color:
                rgb: rgba(52, 0, 231, 255)
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: [5]
        on_release:
            root.manager.transition.direction = "left"
            root.manager.current = "new_group_join"
    Button:
        text: "Load"
        size_hint: .3, .065
        pos_hint: {"center_x": .3, "center_y": .8}
        background_color: 0, 0, 0, 0
        front_name: "BPoppins"
        canvas.before:
            Color:
                rgb: rgba(52, 0, 231, 255)
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: [5]
        on_release:
            app.load_groups()
"""
chat = """
#:import Clipboard kivy.core.clipboard.Clipboard
<Command>
    size_hint_y: None
    pos_hint: {"right": .98}
    height: self.texture_size[1]
    padding: 12, 10
    theme_text_color: "Custom"
    text_color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgb: rgba(52, 0, 234, 255)
        RoundedRectangle:
            size: self.width, self.height
            pos: self.pos
            radius: [23, 23, 0, 23]
            on_touch_down:
                app.message_click()
<Response>
    size_hint_y: None
    pos_hint: {"x": .02}
    #height: self.texture_size[1]
    padding: 12, 10
    canvas.before:
        Color:
            rgb: (1, 1, 1, 1)
        RoundedRectangle:
            size: self.width, self.height
            pos: self.pos
            radius: [23, 23, 23, 0]
    BoxLayout:
        orientation: 'vertical'
        padding: 0
        Label:
            text: root.fro
            font_size: 40
            color: (0, 0, 1, 1)
            halign: 'left'
            size_hint_x: .22
        MDLabel:
            text: root.text
            font_size: 50
            halign: "center"
<AddImage>
    size_hint_y: None
    pos_hint: {"x": -.3}
    height: 600
    
<AddImageCommand>
    size_hint_y: None
    pos_hint: {"right": 1.2}
    height: 600
    
<AddFile>
    size_hint_y: None
    pos_hint: {"x": .02}
    # height: self.texture_size[1]
    padding: 12, 10
    canvas.before:
        Color:
            rgb: (1, 1, 1, 1)
        RoundedRectangle:
            size: self.width, self.height
            pos: self.pos
            radius: [23, 23, 23, 0]
    MDBoxLayout:
        orientation: 'vertical'
        adaptive_height: True
        MDBoxLayout:
            MDLabel:
                id: llabel
                text: root.file_source
                font_size: 12
                color: (0, 0, 1, 1)
                halign: 'left'
                size_hint_x: .22
            MDIconButton:
                icon: "download"
                on_release:
                    app.download(llabel.text)
                    
<AddFileCommand>
    size_hint_y: None
    pos_hint: {"right": .98}
    padding: 12, 10
    theme_text_color: "Custom"
    
    canvas.before:
        Color:
            rgb: rgba(52, 0, 234, 255)
        RoundedRectangle:
            size: self.width, self.height
            pos: self.pos
            radius: [23, 23, 0, 23]
            
    MDBoxLayout:
        orientation: 'vertical'
        adaptive_height: True
        size_hint: None, None
        MDBoxLayout:
            MDLabel:
                id: llabel
                text: root.file_source
                font_size: 12
                color: (0, 0, 1, 1)
                halign: 'right'
                size_hint_x: .22
            MDIconButton:
                icon: "download"
                on_release:
                    app.download(llabel.text)
    
MDScreen:
    name: "chat"
    kkk: kkk
    bot_name: bot_name
    chat_list: chat_list
    text_input: text_input

    MDFloatLayout:
        MDFloatLayout:
            md_bg_color: 245/255, 245/255, 245/255, 1
            size_hint_y: .11
            pos_hint: {"center_y": .95}
            MDIconButton:
                icon: "arrow-left"
                pos_hint: {"center_y": .5}
                user_font_size: "30sp"
                theme_text_color: "Custom"
                text_color: rgba(26, 24, 58, 255)
                on_release:
                    root.manager.transition.direction = "right"
                    root.manager.current = "home"
            MDIconButton:
                icon: "content-copy"
                pos_hint: {"center_x": .9, "center_y": .5}
                on_release:
                    Clipboard.copy(kkk.text)
                    app.show_qr_code(kkk.text)

            MDLabel:
                text: ""
                id: bot_name
                pos_hint: {"center_y": .5}
                halign: "center"
                font_name: "BPoppins"
                font_size: "25sp"
                theme_text_color: "Custom"
                text_color: 53/255, 56/255, 60/255, 1
            MDLabel:
                text: ""
                id: kkk
                pos_hint: {"center_y": .5}
                halign: "center"
                font_name: "BPoppins"
                font_size: "0sp"
                theme_text_color: "Custom"
                text_color: 53/255, 56/255, 60/255, 1
                opacity: 0


        ScrollView:
            size_hint_y: .77
            pos_hint: {"x": 0, "y": .116}
            do_scroll_x: False
            do_scroll_y: True
            BoxLayout:
                id: chat_list
                orientation: "vertical"
                size: (root.width, root.height)
                height: self.minimum_height
                size_hint: None, None
                pso_hint: {"top": 10}
                cols: 1
                spacing: 5
        MDFloatLayout:
            md_bg_color: 245/255, 245/255, 245/255, 1
            size_hint_y: .11
            MDFloatLayout:
                size_hint: .7, .60
                pos_hint: {"center_x": .45, "center_y": .5}
                canvas:
                    Color:
                        rgb: (238/255, 238/255, 238/255, 1)
                    RoundedRectangle:
                        size: self.size
                        pos: self.pos
                        radius: [23, 23, 23, 23]
                TextInput:
                    id: text_input
                    hint_text: "Type something..."
                    size_hint: 1, None
                    pos_hint: {"center_x": .5, "center_y": .5}
                    font_size: "12sp"
                    height: self.minimum_height
                    multiline: False
                    cursor_color: 1, 170/255, 23/255, 1
                    cursor_width: "2sp"
                    foreground_color: 1, 170/255, 23/255, 1
                    background_color: 0, 0, 0, 0
                    padding: 15
                    font_name: "BPoppins"
            MDIconButton:
                icon: "send"
                pos_hint: {"center_x": .91, "center_y": .5}
                user_font_size: "18sp"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                #foreground_color: rgba(0, 0, 0, 1)
                #md_bg_color: rgba(52, 0, 231, 255)
                on_release:
                    app.send_message_aaa(text_input.text, kkk.text)
            MDIconButton:
                icon: "file-upload"
                pos_hint: {"center_x": .8, "center_y": .5}
                user_font_size: "18sp"
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                #md_bg_color: rgba(52, 0, 231, 255)
                on_release:
                    app.file_chooser(kkk.text)

"""
bad = """
MDScreen:
    name: "bad"
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                root.manager.transition.direction = "left"
                root.manager.current = "main"
        MDLabel:
            text: "Ooops..."
            font_name: "BPoppins"
            font_size: "23sp"
            pos_hint: {"center_y": .8}
            halign: "center"
            color: rgba(34, 34, 34, 255)
        MDLabel:
            text: "The credentials you entered are not valid."
            font_name: "BPoppins"
            font_size: "13sp"
            size_hint_x: .85
            pos_hint: {"center_x": .5, "center_y": .7}
            halign: "center"
            color: rgba(127, 127, 127, 255)
        Button:
            text: "Go back."
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .3}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            on_release:
                root.manager.transition.direction = "left"
                root.manager.current = "login"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]


"""
all_load = """
<LoadRes>
    size_hint_y: None
    pos_hint: {"x": .02}
    #height: self.texture_size[1]
    padding: 12, 10
    canvas.before:
        Color:
            rgb: (1, 1, 1, 1)
        RoundedRectangle:
            size: self.width, self.height
            pos: self.pos
            radius: [23, 23, 23, 0]
    BoxLayout:
        orientation: 'vertical'
        padding: 0
        Label:
            text: root.fro
            font_size: 12
            color: (0, 0, 1, 1)
            halign: 'left'
            size_hint_x: .22
        MDLabel:
            text: root.text
            font_size: 12
            halign: "center"
MDScreen:
    name: "all_load"
    group_list: group_list
    butt: butt
    group_num: group_num

    MDLabel:
        text: "ENCOCHAT"
        font_name: "BPoppins"
        font_size: "26sp"
        pos_hint: {"center_x": .8, "center_y": .9}
        color: rgba(0, 0, 59, 255)

    MDIconButton:
        icon: "arrow-left"
        pos_hint: {"center_y": .95}
        user_font_size: "30sp"
        theme_text_color: "Custom"
        text_color: rgba(26, 24, 58, 255)
        on_release:
            root.manager.transition.direction = "right"
            root.manager.current = "home"

    ScrollView:
        size_hint_y: .6
        pos_hint: {"x": 0, "y": .116}
        do_scroll_x: False
        do_scroll_y: True
        BoxLayout:
            id: group_list
            orientation: "vertical"
            size: (root.width, root.height)
            height: self.minimum_height
            size_hint: None, None
            pso_hint: {"top": 10}
            cols: 1
            spacing: 5
            size_hint_y: None
            pos_hint: {"x": .02}
            padding: 12, 10

    MDFloatLayout:
        md_bg_color: 245/255, 245/255, 245/255, 1
        size_hint_y: .11
        MDFloatLayout:
            size_hint: .7, .60
            pos_hint: {"center_x": .45, "center_y": .5}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [23, 23, 23, 23]
            TextInput:
                input_filter: "int"
                id: group_num
                hint_text: "Enter group number"
                size_hint: 1, None
                pos_hint: {"center_x": .5, "center_y": .5}
                font_size: "12sp"
                height: self.minimum_height
                multiline: False
                cursor_color: 1, 170/255, 23/255, 1
                cursor_width: "2sp"
                foreground_color: 1, 170/255, 23/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_name: "BPoppins"
        MDIconButton:
            id: butt
            icon: "send"
            pos_hint: {"center_x": .91, "center_y": .5}
            user_font_size: "18sp"
            theme_text_color: "Custom"
            text_color: 0, 0, 0, 1
            #foreground_color: rgba(0, 0, 0, 1)
            #md_bg_color: rgba(52, 0, 231, 255)
            on_release:
                app.chat_start_with(group_num.text)
"""
progress_bar = """
MDScreen:
    name: "progress_bar"
    progress: progress
    
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                app.stop_key_gen()
                # root.manager.transition.direction = "right"
                # root.manager.current = "main"
        MDLabel:
            text: "Generating..."
            font_name: "BPoppins"
            font_size: "24sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Your keys are being generated."
            font_name: "BPoppins"
            font_size: "16sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)
            
    # MDFloatLayout:
        # md_bg_color: 1, 1, 1, 1
        MDProgressBar:
            id: progress
            value: 0
            size_hint: .8, None
            pos_hint: {"center_x": .5, "center_y": .3}
"""

call = """
MDScreen:
    name: "call"
    icon: icon
    name_: name_

    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "home"

        MDLabel:
            text: "Calling"
            font_size: "26sp"
            font_name: "BPoppins"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Enter the recipient ID"
            font_size: "18sp"
            font_name: "BPoppins"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)

        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .63}
            TextInput:
                id: name_
                font_name: "MPoppins"
                hint_text: "Recipient ID"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)

        MDIconButton:
            id: icon
            icon: "phone"
            pos_hint: {"center_x": .5, "center_y": .2}
            theme_text_color: "Custom"
            text_color: rgba(255, 255, 255, 255)
            # md_bg_color: 255, 0, 0, 255
            md_bg_color: rgba(0, 206, 0, 255)
            on_release:
                app.call(name_.text)
"""
hangup = """
MDScreen:
    name: "hangup"
    caller_id: caller_id

    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1

        MDLabel:
            text: "Telephone"
            font_size: "26sp"
            font_name: "BPoppins"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            id: caller_id
            text: ""
            font_size: "17sp"
            font_name: "BPoppins"
            pos_hint: {"center_x": .6, "center_y": .75}
            color: rgba(0, 0, 59, 255)

        MDIconButton:
            id: icon
            icon: "phone-hangup"
            pos_hint: {"center_x": .5, "center_y": .2}
            theme_text_color: "Custom"
            text_color: rgba(255, 255, 255, 255)
            md_bg_color: 255, 0, 0, 255
            on_release:
                app.hangup()
"""

home_secret = """
MDScreen:
    name: "home_secret"
    
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "home"
        MDLabel:
            text: "Your Secret Key"
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Transfer or receive your secret key."
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)

        Button:
            text: "Send"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .34}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]
            on_release:
                # app.transfer()
                root.manager.transition.direction = "left"
                root.manager.current = "transfer"
                
        Button:
            text: "Receive"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .24}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]
            on_release:
                app.receive_sec()
                # root.manager.transition.direction = "left"
                # root.manager.current = "receive"      
"""
receive = """
MDScreen:
    name: "receive"
    my_key: my_key
    
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                app.exit_receiving()
                # root.manager.transition.direction = "right"
                # root.manager.current = "home"
        MDLabel:
            text: "Receiving..."
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Receive your private key."
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)
        
        MDLabel:
            text: "Your IP:"
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .5}
            color: rgba(0, 0, 0, 255)
            
        MDLabel:
            id: my_key
            text: ""
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .4}
            color: rgba(0, 0, 0, 255)

        
"""
transfer = """
MDScreen:
    name: "transfer"
    ip: ip
    
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "home"
        MDLabel:
            text: "Transfering."
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Enter the ip to transfer."
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)
            
        MDFloatLayout:
            size_hint: .7, .07
            pos_hint: {"center_x": .5, "center_y": .63}
            TextInput:
                id: ip
                hint_text: "IP-Address"
                font_name: "MPoppins"
                size_hint_y: .75
                pos_hint: {"center_x": .43, "center_y": .5}
                background_color: 1, 1, 1, 0
                foreground_color: rgba(0, 0, 59, 255)
                cursor_color: rgba(0, 0, 59, 255)
                font_size: "14sp"
                cursor_width: "2sp"
                multiline: False
            MDFloatLayout:
                pos_hint: {"center_x": .45, "center_y": 0}
                size_hint_y: .03
                md_bg_color: rgba(178, 178, 178, 255)

        Button:
            text: "Start Transfer"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .34}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5]
            on_release:
                app.transfer(ip.text)

"""


from kivy.utils import platform
# from PIL import Image
if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    # request_permissions([Permission.MICROPHONE])
    # request_permissions([Permission.RECORD_AUDIO])
    request_permissions([Permission.INTERNET])
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

Window.size = (310, 580)

Window.keyboard_anim_args = {"d": .2, "t": "in_out_expo"}
Window.softinput_mode = "below_target"

######################### BASIC VARIABLES #########################
group_key = ""
user = ""

current_private_key = b""
current_chat_with = ""

is_it_my_turn = False

accepted = False

received_secret = False
sent_secret = False

# 2.tcp.eu.ngrok.io:13117
# HOST = "5.tcp.eu.ngrok.io"
# PORT = 15921  # The port used by the server
try:
    HOST, PORT = requests.get("https://api.protdos.com").text.split(":")
    PORT = int(PORT)
    print("Using host, port:", HOST, PORT)
except:
    HOST, PORT = None, None

HOST, PORT = "localhost", 5000


######################### Chat #########################
class Command(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "BPoppins"
    font_size = 50


class Response(BoxLayout):
    text = StringProperty()
    fro = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "BPoppins"
    font_size = 50


class Command2(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "BPoppins"
    font_size = 50


class Response2(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "BPoppins"
    font_size = 50


class LoadRes(BoxLayout):
    text = StringProperty()
    fro = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "BPoppins"
    font_size = 12


class AddImage(Image):
    source = StringProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.clicked()

    def clicked(self):
        try:
            print('Image clicked:', self.source)
            IImage.open(self.source).save(f"/sdcard/{self.source}")
        except Exception as e:
            print("Error wtf:", e)
            toast("Couldn't save image.")
        # os.startfile(self.source)


class AddImageCommand(Image):
    source = StringProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.clicked()

    def clicked(self):
        try:
            print('Image clicked:', self.source)
            IImage.open(self.source).save(f"/sdcard/{self.source}")
        except Exception as e:
            print("Error wtf:", e)
            toast("Couldn't save image.")
        # os.startfile(self.source)


class AddFile(BoxLayout):
    file_source = StringProperty()
    font_name = "BPoppins"
    font_size = 12


class AddFileCommand(BoxLayout):
    file_source = StringProperty()
    font_name = "BPoppins"
    font_size = 12


######################### Encryption #########################
def gen(length):
    try:
        al = string.ascii_uppercase + string.ascii_lowercase + string.digits + "^!§$%&/()=?*+#'-_.:;{[]}"  # creating a list of nearly every char
        """
        This code is outdated, because generating a random key isn't truly possible with the random module:
        - https://python.readthedocs.io/en/stable/library/random.html
        - https://www.youtube.com/watch?v=Nm8NF9i9vsQ
        bb = []  # init list
        for i in range(length):  # creating a random password based on var length
            bb.append(random.choice(al))
        return "".join(bb)
        """
        # A better solution is this:
        key_sequences = []
        for _ in range(length):
            key_sequences.append(secrets.choice(al))
        return "".join(key_sequences)
    except Exception as e:
        print("Error19:", e)


def strength_test(p):
    try:
        policy = PasswordPolicy.from_names(
            strength=0.5  # need a password that scores at least 0.5 with its strength
        )
        out = policy.test(p)
        print(len(out))
        return [True if len(out) == 0 else False]  # returning if password is good or not
    except Exception as e:
        print("Error20:", e)


def hash_pwd(password):
    try:
        salt = "%Up=gJDD8dwL^5+W4pgyprt*sd4QEKTM4nfkD$ZW&Zb_?j^wQUGS6kK?2VkfYy7zu?hnN%a9YU!wduhwnUbKpUe*g*Y#aT$=M2KsA6gMFpU+q!!Ha6HN6_&F3DCL@-gweA47FQyq9wu*yd&By%p-dKPGucfjs2-26He-rPZjLEvBn$a-NFeDHD-UP9A23@5@EtZ5+LmeBS@ZUHW9HDy9U@!3BM2^U5nrq+wUjesgEX^SvDgf8Qs8$kjzEacUGx@r"
        dataBase_password = password + salt
        hashed = hashlib.sha256(dataBase_password.encode())
        return hashed.hexdigest()
    except Exception as e:
        print("Error21:", e)


class Encrypt:
    def __init__(self, message_, key):
        self.message = message_
        self.key = key

    def encrypt(self):
        password_provided = self.key
        password = password_provided.encode()
        salt = b'salt_'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        msg = self.message.encode()
        f = Fernet(key)
        msg = f.encrypt(msg)
        return msg


class Decrypt:
    def __init__(self, message_, key, verbose=True):
        self.message = message_
        self.key = key
        self.verbose = verbose

    def decrypt(self):
        try:
            self.key = self.key.encode()
            salt = b'salt_'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.key))
            self.message = self.message.encode()
            f = Fernet(key)
            decoded = str(f.decrypt(self.message).decode())
            return decoded
        except:
            pass


class Encrypt_File:
    def __init__(self, message_, key):
        self.message = message_
        self.key = key

    def encrypt(self):
        password_provided = self.key
        password = password_provided.encode()
        salt = b'salt_'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=1000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        msg = self.message.encode()
        f = Fernet(key)
        msg = f.encrypt(msg)
        return msg


class Decrypt_File:
    def __init__(self, message_, key, verbose=True):
        self.message = message_
        self.key = key
        self.verbose = verbose

    def decrypt(self):
        try:
            self.key = self.key.encode()
            salt = b'salt_'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=1000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.key))
            self.message = self.message.encode()
            f = Fernet(key)
            decoded = str(f.decrypt(self.message).decode())
            return decoded
        except:
            pass


def encode_file(file_path, key):
    with open(file_path, "rb") as image_file:
        return Encrypt(message_=base64.b64encode(image_file.read()).decode(), key=key).encrypt()


def decode_file(enc_string, name, key):
    with open(name, "wb") as image_file:
        a = base64.b64decode(Decrypt(message_=enc_string.decode(), key=key).decrypt())
        image_file.write(a)
        return a


######################### Main #########################
class ChatApp(MDApp):
    i = 0
    key_genned = False

    started_g = False

    # For voice
    hanged = False
    call_initiated = False
    call_started = False
    threads = []

    audio = None
    FORMAT = None
    CHANNELS = None
    RATE = None
    CHUNK = None
    stream = None
    streamOut = None

    username = None
    password = None
    id = None
    gggggg = None
    rooms = None
    mf_key_group_bla = None
    super_dubba_key = None

    aaa = None
    l = None

    public_key = None
    private_key = None

    screen_manager = None

    sock = None

    sound = None
    BLOCK_SIZE = None

    receiving = False

    client_socket = None

    stop_genning = False

    def build(self):
        try:
            """
            # set up PyAudio
            self.audio = pyaudio.PyAudio()
            self.FORMAT = pyaudio.paInt16
            self.CHANNELS = 1
            self.RATE = 44100
            self.CHUNK = 1024

            # set up the audio stream
            self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True,
                                          frames_per_buffer=self.CHUNK)

            self.streamOut = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                             rate=self.RATE, output=True, input_device_index=0,
                                             frames_per_buffer=self.CHUNK)
            """
            self.CHANNELS = 1
            self.BLOCK_SIZE = 1024
            self.sound = SoundLoader.load('dial.wav')

            self.username = ""
            self.receiving = False
            self.password = ""
            self.id = ""
            self.gggggg = ""
            self.rooms = []
            self.mf_key_group_bla = ""
            self.super_dubba_key = ""

            self.aaa = None
            self.l = []

            self.public_key = None
            self.private_key = None

            self.screen_manager = ScreenManager()

            self.screen_manager.add_widget(Builder.load_string(login))
            self.screen_manager.add_widget(Builder.load_string(progress_bar))
            self.screen_manager.add_widget(Builder.load_string(home))
            self.screen_manager.add_widget(Builder.load_string(chat_private))
            self.screen_manager.add_widget(Builder.load_string(chat_sec))
            self.screen_manager.add_widget(Builder.load_string(main))
            self.screen_manager.add_widget(Builder.load_string(group_create))
            self.screen_manager.add_widget(Builder.load_string(group_join))
            self.screen_manager.add_widget(Builder.load_string(group))
            self.screen_manager.add_widget(Builder.load_string(password_reset))
            self.screen_manager.add_widget(Builder.load_string(chat_new_private))
            self.screen_manager.add_widget(Builder.load_string(signup))
            self.screen_manager.add_widget(Builder.load_string(help_))
            self.screen_manager.add_widget(Builder.load_string(chat_load))
            self.screen_manager.add_widget(Builder.load_string(bad))
            self.screen_manager.add_widget(Builder.load_string(new_group_join))
            self.screen_manager.add_widget(Builder.load_string(show_id2))
            self.screen_manager.add_widget(Builder.load_string(show_qr2))
            self.screen_manager.add_widget(Builder.load_string(show_id))
            self.screen_manager.add_widget(Builder.load_string(chat))
            self.screen_manager.add_widget(Builder.load_string(all_load))

            self.screen_manager.add_widget(Builder.load_string(call))
            self.screen_manager.add_widget(Builder.load_string(hangup))

            self.screen_manager.add_widget(Builder.load_string(home_secret))
            self.screen_manager.add_widget(Builder.load_string(transfer))
            self.screen_manager.add_widget(Builder.load_string(receive))

            return self.screen_manager
        except Exception as e:
            print("Error21:", e)

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
        except Exception as e:
            print("Error22:", e)
            self.screen_manager.current_screen = "main"
            self.show_toaster("Couldn't connect to server. Check connection. ")

    def sign_up(self, username, password, password2):
        try:
            global user
            self.screen_manager.get_screen("home").welcome_name.text = f"Welcome {username}"
            if password != password2:
                self.show_toaster("Password's do not match.")
                return
            if not strength_test(password)[0]:
                self.show_toaster("Password isn't strong enough.")
                self.screen_manager.get_screen("signup").password.text = ""
                self.screen_manager.get_screen("signup").password2.text = ""
                self.screen_manager.current = "signup"
                return
            if not accepted:
                self.show_toaster("You need to accept our ToS.")
                return
            uid = str(uuid.uuid4())
            self.connect()
            self.sock.send(f"USER_EXISTS:{username}".encode())
            if self.sock.recv(1024) == b"exists":
                self.show_toaster("Username taken.")
                self.screen_manager.get_screen("signup").username.text = ""
                return
            else:
                print("okay")
            print("Generating.")
            # self.stop_genning = False
            # self.do_smt()
            # time.sleep(2)
            # print("aa")
            # threading.Thread(target=self.gen, args=(username, password, uid,)).start()
            threading.Thread(target=self.okok, args=(username, password, uid,)).start()

        except:
            pass

    @mainthread
    def okok(self, username, password, uid):
        public, private = rsa.newkeys(1024)  # 2048
        self.public = public
        self.private = private
        self.public_key = public
        self.private_key = private
        self.connect()
        self.sock.send(f"SIGNUP:::{username}:::{hash_pwd(password)}:::{uid}".encode())
        time.sleep(0.5)
        print("aaa")
        self.sock.send(self.public_key.save_pkcs1())
        r = self.sock.recv(1024).decode()
        if r == "error":
            self.show_toaster("Username taken. Try again.")
            self.screen_manager.get_screen("signup").username.text = ""
            return
        elif r == "errorv2":
            self.show_toaster("ID already used - internal error. Try again later.")
            return
        else:
            pass
        enc_priv = Encrypt(message_=self.private_key.save_pkcs1().decode(), key=password).encrypt().decode()
        with open("private_key.txt", "w") as file:
            file.write(enc_priv)
        # with open("private_key.txt", "w") as file:
        #     file.write(private.save_pkcs1().decode())  # encrypt private key
        with open("public_key.txt", "w") as file:
            file.write(self.public_key.save_pkcs1().decode())
        # self.public_key = public  # not needed
        # self.private_key = private
        self.id = uid
        self.username = username
        self.password = password
        self.super_dubba_key = self.password
        self.screen_manager.current = "home"
        self.screen_manager.get_screen("signup").username.text = ""
        self.screen_manager.get_screen("signup").password.text = ""
        self.screen_manager.get_screen("signup").password2.text = ""

        self.show_toaster("Account created!")

    def login(self, username, password):
        try:
            self.connect()
            global user
            self.screen_manager.get_screen("home").welcome_name.text = f"Welcome {username}"
            try:
                """
                with open("data/username.txt", "r") as file:
                    usr = file.read()
                with open("data/auth.txt", "r") as file:
                    pp = file.read()
                with open("data/id.txt", "r") as file:
                    ii = file.read()
                if usr != username:
                    self.screen_manager.current = "bad"
                    return
                pp2 = Decrypt(message_=pp, key=password).decrypt()
                if pp2 == password:
                    self.username = username
                    user = usr
                    self.password = password
                    self.id = ii
                    self.super_dubba_key = self.password
                    self.screen_manager.current = "home"
                    self.show_toaster("Logged in!")
                else:
                    self.screen_manager.current = "bad"
                """
                self.sock.send(f"LOGIN:::{username}:::{hash_pwd(password)}".encode())
                r = self.sock.recv(1024).decode()
                # print(r)
                if r == "error":
                    self.show_toaster("Invalid username")
                    self.screen_manager.get_screen("login").username.text = ""
                    self.screen_manager.get_screen("login").password.text = ""
                elif r == "errorv2":
                    self.show_toaster("Invalid password")
                    self.screen_manager.get_screen("login").password.text = ""
                else:
                    # with open("private_key.txt", "rb") as file:
                    #     self.private_key = rr.PrivateKey.load_pkcs1(file.read())
                    with open("private_key.txt", "r") as file:
                        a = file.read()
                        dec_priv = Decrypt(message_=a, key=password).decrypt().encode()
                        print(dec_priv)
                        if dec_priv is None:
                            self.show_toaster("Private key couldn't be decrypted.")
                            return
                        self.private_key = rr.PrivateKey.load_pkcs1(dec_priv)
                    self.username = username
                    self.password = password
                    self.super_dubba_key = password
                    self.screen_manager.current = "home"
                    _, idd = r.split(":")
                    self.id = idd
                    self.screen_manager.get_screen("login").username.text = ""
                    self.screen_manager.get_screen("login").password.text = ""
                    self.show_toaster("Logged in!")
            except Exception as e:
                print("Errorv2:", e)
                self.screen_manager.get_screen("login").username.text = ""
                self.screen_manager.get_screen("login").password.text = ""
                self.show_toaster("Error logging in! Please try again.")
                self.screen_manager.current = "login"
        except Exception as e:
            print("Error24", e)
            self.screen_manager.current_screen = "home"
            self.screen_manager.get_screen("login").username.text = ""
            self.screen_manager.get_screen("login").password.text = ""
            self.show_toaster("Error logging in! Please try again.")

    def show_qr_code(self, key):
        try:
            qr = qrcode.make(key)
            qr.save("qr_code.png")

            self.screen_manager.get_screen("show_qr").img.reload()

            self.screen_manager.current = "show_qr"
        except:
            self.screen_manager.current_screen = "login"
            self.show_toaster("Error! Please sign in again.")

    def show_qr_code2(self, key):
        try:
            qr = qrcode.make(key)
            qr.save("qr_code.png")

            self.screen_manager.get_screen("show_qr2").img.reload()

            self.screen_manager.current = "show_qr2"
        except:
            self.screen_manager.current_screen = "login"
            self.show_toaster("Error! Please sign in again.")

    def change_username(self, username):
        try:
            self.connect()
            try:
                self.screen_manager.get_screen("home").text_input2.text = ""
                self.screen_manager.get_screen("home").welcome_name.text = f"Welcome {self.username}"
                if username != "":
                    self.screen_manager.get_screen("home").username_icon.icon = "check"
                    time.sleep(.5)
                    self.screen_manager.get_screen("home").username_icon.icon = "account-cog"

                    self.connect()
                    self.sock.send(f"CHANGE_USERNAME:{self.username}:{self.password}:{username}".encode())
                    r = self.sock.recv(1024).decode()
                    if r == "success":
                        self.screen_manager.current = "login"
                        self.show_toaster("Username has been changed")
                    else:
                        self.show_toaster("Error changing username.")
                else:
                    self.show_toaster("Please enter an username.")
            except Exception as e:
                print("Error2:", e)
                self.show_toaster("Error changing username.")
        except Exception as e:
            print("Error3:", e)
            self.show_toaster("Error changing username.")

    def change_password(self, new):
        try:
            self.connect()
            self.screen_manager.get_screen("home").text_input3.text = ""

            """
            with open("data/auth.txt", "w") as file:
                file.write(Encrypt(message_=new, key=new).encrypt().decode())
            """
            self.connect()
            self.sock.send(f"CHANGE_PASSWORD:{self.password}:{new}:{self.username}".encode())
            r = self.sock.recv(1024).decode()
            if r == "success":

                with open("groups.csv", "r") as file:
                    encrypted_keys = file.read().split("\n")

                for item in encrypted_keys:
                    if item == "key" or item == "" or item == '':
                        encrypted_keys.remove(item)

                print(f"Found {len(encrypted_keys)} key(s) in groups.csv")
                print(encrypted_keys)

                with open("private_key.txt", "r") as file:
                    a = file.read()
                    dec_priv = Decrypt(message_=a, key=self.super_dubba_key).decrypt().encode()
                    print(dec_priv)
                    if dec_priv is None:
                        self.show_toaster("Private key couldn't be decrypted.")
                        return
                    private_key = rr.PrivateKey.load_pkcs1(dec_priv)
                enc_priv = Encrypt(message_=private_key.save_pkcs1().decode(), key=new).encrypt().decode()
                with open("private_key.txt", "w") as file:
                    file.write(enc_priv)

                with open("groups.csv", "w") as f:
                    f.write("key\n")
                    for enc_key in encrypted_keys:
                        # print(enc_key)
                        dec_key = Decrypt(message_=enc_key, key=self.super_dubba_key).decrypt()
                        # print(dec_key)
                        enc_key2 = Encrypt(message_=dec_key, key=new).encrypt().decode()
                        # print(enc_key2)
                        f.write(enc_key2 + "\n")
                with open("private_chats.csv", "w") as f:
                    for enc_key in encrypted_keys:
                        # print(enc_key)
                        dec_key = Decrypt(message_=enc_key, key=self.super_dubba_key).decrypt()
                        # print(dec_key)
                        enc_key2 = Encrypt(message_=dec_key, key=new).encrypt().decode()
                        # print(enc_key2)
                        f.write(enc_key2 + "\n")

                self.password = new
                self.super_dubba_key = new

                self.screen_manager.get_screen("home").password_icon.icon = "check"
                time.sleep(.5)
                self.screen_manager.get_screen("home").password_icon.icon = "account-cog"

                self.screen_manager.current_screen = "login"

                self.show_toaster("Password has been changed.")
            else:
                self.show_toaster("Error changing password.")
        except Exception as e:
            print("Error4:", e)
            self.show_toaster("Error changing password.")

    def create_chat(self, rec):
        try:
            global current_private_key, current_chat_with, is_it_my_turn
            is_it_my_turn = False
            personal = self.username + "#" + self.id

            self.connect()
            self.sock.send(f"GET_PUBLIC:{rec}".encode())
            public_key = self.sock.recv(1024)
            print("Public key of rec:", public_key)
            if public_key != "error":
                public = rr.PublicKey.load_pkcs1(public_key)
                print("Loaded key of rec:", public)
                self.aaa = public

                self.connect()
                self.sock.close()
                self.connect()

                self.sock.send(f"GET_USERNAME:{rec}".encode())
                name = self.sock.recv(1024).decode()
                if name == "error":
                    self.screen_manager.current = "home"
                    self.show_toaster("Invalid key.")
                    return

                self.connect()
                self.sock.close()
                self.connect()

                self.sock.send("PRIV:".encode())
                self.sock.send(personal.encode())
                """
                open(f"2\\{rec}.txt", 'w').close()
                key = gen(100)
                current_private_key = key
                current_chat_with = rec
                """
                try:
                    if rec not in open("private_chats.csv", "r").read():
                        with open("private_chats.csv", "a") as rec_file:
                            # rec_file.write(rec + "\n")
                            rec_file.write(Encrypt(message_=rec, key=self.super_dubba_key).encrypt().decode() + "\n")
                    open("private_chats.csv", "r").close()
                except:
                    open("private_chats.csv", "w").close()
                    with open("private_chats.csv", "a") as rec_file:
                        rec_file.write(Encrypt(message_=rec, key=self.super_dubba_key).encrypt().decode() + "\n")
                        # rec_file.write(rec + "\n")
                    open("private_chats.csv", "r").close()
                open(f"{rec}.txt", "w").close()

                current_private_key = public_key
                current_chat_with = rec

                # name = rec.split("#")[0]

                self.screen_manager.get_screen("chat_sec").chat_list.clear_widgets()
                self.screen_manager.get_screen("chat_sec").bot_name.text = name
                # self.screen_manager.get_screen("chat_sec").kkk.text = key

                threading.Thread(target=self.receive_messages_private, args=(public,)).start()

                self.screen_manager.current = "chat_sec"

                # self.show_toaster("Created!")
            else:
                self.show_toaster("Invalid recipient.")
        except Exception as e:
            print("Error5:", e)
            self.show_toaster("Couldn't create chat.")

    @mainthread
    def add(self, message):
        try:
            global size, halign, value
            if message != "":
                value = message
                if len(value) < 6:
                    size = .22
                    halign = "center"
                elif len(value) < 6:
                    size = .22
                    halign = "center"
                elif len(value) < 11:
                    size = .32
                    halign = "center"
                elif len(value) < 16:
                    size = .45
                    halign = "center"
                elif len(value) < 21:
                    size = .58
                    halign = "center"
                elif len(value) < 26:
                    size = .71
                    halign = "center"
                else:
                    size = .7
                    halign = "left"
            self.screen_manager.get_screen("chat_sec").chat_list.add_widget(Response2(text=message, size_hint_x=size+.3, halign=halign))
        except Exception as e:
            print("Error6:", e)
            pass

    def receive_messages_private(self, _):
        print("Personal private key:", self.private_key)
        try:
            with open(f"{current_chat_with}.txt", "r") as ii:
                aa = ii.read().split("\n")
            for lo in aa:
                if lo != "\n" and lo != "":
                    self.add(lo)
            open(f"{current_chat_with}.txt", "w").close()
        except Exception as e:
            open(f"{current_chat_with}.txt", "w").close()
            print("Error7:", e)
            pass
        while True:
            try:
                print("Chat with:", current_chat_with)
                message = self.sock.recv(1024)
                print(message)
                message = message.decode()
                print("Message received:", message)
                if message:
                    if message == "NICK":
                        self.sock.send(self.username.encode())
                    elif message.split("#")[1].startswith(current_chat_with):
                        m = self.sock.recv(1024)
                        print("Shorted message:", m)
                        print("Decrypted:", rr.decrypt(m, self.private_key))
                        m = rr.decrypt(m, self.private_key).decode()
                        # m = m[2:]
                        # m = m[:-1]
                        # print(m)
                        # print(rr.decrypt(m.encode(), private).decode())
                        # m = Decrypt(message_=m, key=key).decrypt()
                        self.add(m)
                    elif message.startswith(f"INCOMING:{self.username}#{self.id}"):
                        print("OOOOOKAY")
                        m = self.sock.recv(1024)
                        m = rr.decrypt(m, self.private_key).decode()
                        self.add(m)
                    else:
                        try:
                            sender, mess = message.split("---")
                            print("Decrypted message:", rr.decrypt(mess, self.private_key).decode())
                            with open(f"{sender}.txt", "a") as file:
                                file.write(mess + "\n")
                            self.notify(f"New message from {sender}", mess)
                        except:
                            print("Invalid message received.")
                            self.add(message)
                else:
                    break
            except Exception as e:
                print("Errorv3:", e)
                continue

    def load_groups(self):
        try:
            self.screen_manager.get_screen("group_join").group_list.clear_widgets()
            try:
                with open("groups.csv") as file:  # getting group key data
                    data = file.read().split("\n")
            except:
                if not os.path.isfile("groups.csv"):
                    a = open("groups.csv", "w")
                    a.write("key\n")
                    a.close()
                data = []
            c = 0
            my_bitch_rooms = [""]  # list of rooms
            try:
                for i in range(1, len(data)):
                    try:
                        if data[i] == "" or data[i] == "\n":
                            pass
                        else:
                            current_line = Decrypt(message_=data[i], key=self.super_dubba_key,
                                                   verbose=False).decrypt()  # decrypting every group name/key
                            print(current_line)
                            if current_line is not None:
                                my_bitch_rooms.append(current_line)
                                c += 1
                    except:
                        c -= 1
                        pass

            except Exception as e:
                print("Error8:", e)
                pass

            print(c)
            print(my_bitch_rooms)

            if c > 0:
                self.screen_manager.get_screen("group_join").group_num.disabled = False
                self.screen_manager.get_screen("group_join").butt.disabled = False
                self.screen_manager.get_screen("group_join").butt.hint_text = "Enter group number"
                self.rooms = my_bitch_rooms
                for i, item in enumerate(my_bitch_rooms):
                    if item != "" and item != None:
                        # print("1")
                        item = item.split("|")[0]
                        self.screen_manager.get_screen("group_join").group_list.add_widget(
                            Response(text=f"{i})-{item}", size_hint_x=.75))
            else:
                # print("2")
                self.screen_manager.get_screen("group_join").ok.text = "No groups available."
                self.screen_manager.get_screen("group_join").group_num.disabled = True
                self.screen_manager.get_screen("group_join").butt.disabled = True
                self.screen_manager.get_screen("group_join").butt.hint_text = "Not available"
        except Exception as e:
            print("Error9:", e)
            self.show_toaster("Error occured while showing groups.")

    def join_group(self, group_id):
        try:
            if group_id != "":
                group_id = int(group_id)
                if self.super_dubba_key != "":
                    self.screen_manager.get_screen("chat").chat_list.clear_widgets()
                    global group_key, sock, is_it_my_turn
                    is_it_my_turn = True

                    key = self.rooms[group_id]
                    name = key.split("|")[0]
                    group_id = key.split("|")[2]
                    self.screen_manager.get_screen("chat").kkk.text = key
                    self.screen_manager.get_screen("chat").bot_name.text = name
                    group_key = key
                    self.connect()
                    self.sock.send(("ID::::::" + "|||" + self.username + "|||" + group_id).encode())
                    threading.Thread(target=self.receive_messages).start()
                    self.screen_manager.current = "chat"
                else:
                    self.screen_manager.current = "login"
        except Exception as e:
            print("Error10:", e)
            self.show_toaster("Please load the groups first.")

    def join_new_group(self, key):
        if key != "":
            if self.super_dubba_key != "":
                self.screen_manager.get_screen("chat").chat_list.clear_widgets()
                global group_key, sock, is_it_my_turn
                is_it_my_turn = True

                name = key.split("|")[0]
                group_id = key.split("|")[2]
                self.screen_manager.get_screen("chat").kkk.text = key
                self.screen_manager.get_screen("chat").bot_name.text = name
                group_key = key
                with open("groups.csv", "r") as file:
                    aa = file.read().split("\n")
                enc_key = Encrypt(message_=key, key=self.super_dubba_key).encrypt().decode()
                if enc_key not in aa:
                    with open("groups.csv", "a") as file:
                        file.write(f"{enc_key}\n")

                self.connect()
                self.sock.send(("ID::::::" + "|||" + self.username + "|||" + group_id).encode())
                threading.Thread(target=self.receive_messages).start()
                self.screen_manager.current = "chat"
            else:
                self.screen_manager.current = "login"

    def create_group(self, name):
        try:
            if name != "":
                self.screen_manager.get_screen("group_create").name_.text = ""

                global group_key, sock, is_it_my_turn
                is_it_my_turn = True
                key = gen(100)
                group_id = str(uuid.uuid4())
                key = name + "|" + key + "|" + group_id
                group_key = key
                # print(key)
                self.screen_manager.get_screen("chat").kkk.text = key
                self.screen_manager.get_screen("chat").bot_name.text = name
                # self.screen_manager.get_screen("chat").key.text = key
                with open("groups.csv", "a") as file:
                    encc = Encrypt(message_=key, key=self.super_dubba_key).encrypt().decode()
                    # print(encc)
                    file.write(f"{encc}\n")

                self.connect()

                self.sock.send(("ID::::::" + "|||" + self.username + "|||" + group_id).encode())
                # sock.send(f"ID::::::{group_id}".encode())

                self.screen_manager.get_screen("chat").chat_list.clear_widgets()
                self.screen_manager.get_screen("chat").bot_name.text = name
                # self.screen_manager.get_screen("chat_sec").kkk.text = key

                threading.Thread(target=self.receive_messages).start()

                self.screen_manager.current = "chat"
        except Exception as e:
            print("Error11:", e)
            self.show_toaster("Couldn't create group.")

    def load_all(self):
        self.screen_manager.current = "all_load"
        print("okay")
        self.screen_manager.get_screen("all_load").group_list.clear_widgets()
        with open("private_chats.csv") as priv:
            a = priv.read().split("\n")
        self.l = []
        for item in a:
            if item != "":
                try:
                    item = Decrypt(message_=item, key=self.super_dubba_key).decrypt()
                    if item not in self.l:
                        self.l.append(item)
                except:
                    print(f"item {item} doesn't belong to the acc.")
                    pass

        for i, item in enumerate(self.l):
            self.screen_manager.get_screen("all_load").group_list.add_widget(
                LoadRes(text=f"{i+1})-{item}", size_hint_x=.75))

    def chat_start_with(self, nnum):
        rec = self.l[int(nnum)-1]
        self.create_chat(rec)

    def show_password(self):
        if self.screen_manager.get_screen("login").pws1.icon == "eye":
            self.screen_manager.get_screen("login").password.password = False
            self.screen_manager.get_screen("login").pws1.icon = "eye-off"
        else:
            self.screen_manager.get_screen("login").password.password = True
            self.screen_manager.get_screen("login").pws1.icon = "eye"

    def show_password_sign(self):
        if self.screen_manager.get_screen("signup").pws1.icon == "eye":
            self.screen_manager.get_screen("signup").password.password = False
            self.screen_manager.get_screen("signup").pws1.icon = "eye-off"
        else:
            self.screen_manager.get_screen("signup").password.password = True
            self.screen_manager.get_screen("signup").pws1.icon = "eye"

    def show_password_sign2(self):
        if self.screen_manager.get_screen("signup").pws2.icon == "eye":
            self.screen_manager.get_screen("signup").password2.password = False
            self.screen_manager.get_screen("signup").pws2.icon = "eye-off"
        else:
            self.screen_manager.get_screen("signup").password2.password = True
            self.screen_manager.get_screen("signup").pws2.icon = "eye"

    @mainthread
    def send_message_aaa(self, message, _):
        try:
            self.sock.send('{}: {}'.format(user, Encrypt(message_=message, key=group_key).encrypt().decode()).encode())
            global size, halign, value
            if message != "":
                value = message
                if len(value) < 6:
                    size = .22
                    halign = "center"
                elif len(value) < 6:
                    size = .22
                    halign = "center"
                elif len(value) < 11:
                    size = .32
                    halign = "center"
                elif len(value) < 16:
                    size = .45
                    halign = "center"
                elif len(value) < 21:
                    size = .58
                    halign = "center"
                elif len(value) < 26:
                    size = .71
                    halign = "center"
                else:
                    size = .7
                    halign = "left"

                self.screen_manager.get_screen("chat").chat_list.add_widget(
                    Command(text=message, size_hint_x=size+.3, halign=halign))

                self.screen_manager.get_screen("chat").text_input.text = ""
        except Exception as e:
            print("Error12:", e)
            self.show_toaster("Couldn't send message.")

    def receive_messages(self):
        while True:
            try:
                message = self.sock.recv(1024).decode()
                print(message)
                try:
                    sender = message.split(": ")[0]
                    message = Decrypt(message_=message.split(": ")[1], key=group_key).decrypt()
                    print(message)
                except:
                    sender = None
                    pass
                print("Message:", message)
                if message is not None:
                    if message:
                        if message == "NICK":
                            self.sock.send(user.encode())
                        elif message == "FILE_INCOMING":
                            # filename = Decrypt(message_=self.sock.recv(1024).decode(), key=group_key).decrypt()
                            filename = self.sock.recv(1024).decode()

                            print("FIlemane:", filename)

                            sender = self.sock.recv(1024).decode()

                            print("Sender:", sender)

                            al = []

                            while True:
                                more_data = self.sock.recv(1024).decode()
                                if more_data.endswith(":"):
                                    more_data = more_data[:-7]
                                    al.append(more_data)
                                    break
                                else:
                                    al.append(more_data)

                            data = "".join(al)
                            print("data:", data)
                            # k = str(uuid.uuid4()) + filename
                            kk = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
                            # more3_data = decode_file(data.encode(), kk, group_key)
                            more3_data = decode_file(data.encode(), kk, group_key)
                            print("More3_data:", more3_data)
                            # print(more3_data)

                            # print("kk:", kk)

                            print("okay0")

                            try:
                                os.startfile(filename)
                            except:
                                # Couldn't open file
                                pass
                            # self.add2(filename, fro=sender)
                            self.add_file(filename, sender)
                            print("okay2")
                        elif message == "IMAGE_INCOMING":
                            name, sender = self.sock.recv(1024).split(b"<<MARKER>>")
                            # name = self.sock.recv(1024)
                            print("image coming.")
                            print("aaaa", name)
                            # k = f"{uuid.uuid4()}-{name}"

                            kk = os.path.join(os.path.dirname(os.path.abspath(__file__)), name.decode())
                            print("kkk:", kk)
                            al_data = []
                            while True:
                                data = self.sock.recv(1024)
                                if not data or data == b":ENDED:":
                                    break
                                al_data.append(data.decode())
                            dat = "".join(al_data)
                            print("cat:", dat)
                            print("okay received image")

                            dec = decode_file(dat.encode(), kk, group_key)
                            print(dec)

                            self.add_img(img_src=kk)

                        else:
                            self.add2(message, fro=sender)
                            print("Message:", message)
                    else:
                        self.screen_manager.current_screen = "home"
                        self.show_toaster("Server restarting...")
                        break
            except Exception as e:
                print("Error13:", e)
                if "[WinError 10054]" in e:
                    self.screen_manager.current = "main"
                    self.show_toaster("Server went offline.")
                    break
                continue

    @mainthread
    def add_file(self, path, fro):
        self.screen_manager.get_screen("chat").chat_list.add_widget(
            AddFile(file_source=path))

    @mainthread
    def add_file_cmd(self, path):
        self.screen_manager.get_screen("chat").chat_list.add_widget(
            AddFileCommand(file_source=path))

    @mainthread
    def add2(self, message, fro):
        try:
            global size, halign, value
            if message != "":
                value = message
                if len(value) < 6:
                    size = .22
                    halign = "center"
                elif len(value) < 6:
                    size = .22
                    halign = "center"
                elif len(value) < 11:
                    size = .32
                    halign = "center"
                elif len(value) < 16:
                    size = .45
                    halign = "center"
                elif len(value) < 21:
                    size = .58
                    halign = "center"
                elif len(value) < 26:
                    size = .71
                    halign = "center"
                else:
                    size = .7
                    halign = "left"
            self.screen_manager.get_screen("chat").chat_list.add_widget(
                Response(text=message, size_hint_x=size+.3, halign=halign))
        except Exception as e:
            print("Error14:", e)
            pass

    @mainthread
    def add_img(self, img_src):
        try:
            print(img_src)
            self.screen_manager.get_screen("chat").chat_list.add_widget(
                AddImage(source=img_src))
        except Exception as e:
            print("Error15:", e)
            pass

    @mainthread
    def add_img_cmd(self, img_src):
        try:
            print(img_src)
            self.screen_manager.get_screen("chat").chat_list.add_widget(
                AddImageCommand(source=img_src))
        except Exception as e:
            print("Error88:", e)
            pass

    @mainthread
    def send_message_private(self, message, _):
        print("Public key of partner loaded:", self.aaa)
        # sock.send(("/pm " + current_chat_with + " " + Encrypt(message_=message, key=key).encrypt().decode()).encode())
        enc = rr.encrypt(message.encode(), self.aaa)
        print("Encrypted message:", enc)
        self.sock.send(f"/pm {current_chat_with}".encode())
        print("First sent")
        self.sock.send(enc)
        print("Second sent")
        # sock.send(("/pm " + current_chat_with + " " + message).encode())
        # sock.send(f"/pm {current_chat_with} {rr.encrypt(message.encode(), key)}".encode())

        global size, halign, value
        if message != "":
            value = message
            if len(value) < 6:
                size = .22
                halign = "center"
            elif len(value) < 6:
                size = .22
                halign = "center"
            elif len(value) < 11:
                size = .32
                halign = "center"
            elif len(value) < 16:
                size = .45
                halign = "center"
            elif len(value) < 21:
                size = .58
                halign = "center"
            elif len(value) < 26:
                size = .71
                halign = "center"
            else:
                size = .7
                halign = "left"

        self.screen_manager.get_screen("chat_sec").chat_list.add_widget(
            Command2(text=message, size_hint_x=size+.3, halign=halign))

        self.screen_manager.get_screen("chat_sec").text_input.text = ""

    def file_chooser(self, key):
        try:
            self.mf_key_group_bla = key
            print("key", key)
            filechooser.open_file(on_selection=self.selected)
        except:
            pass

    def selected(self, selection):
        try:
            self.send_file(selection[0])
        except:
            pass

    def send_file(self, file_path):
        try:
            f_size = os.path.getsize(file_path) / 1048576

            if f_size > 10:
                self.show_toaster("File is too big.")
                print("File is too big.")
            else:
                filename = str(os.path.basename(file_path))

                allowed = ["pdf", "txt", "jpg", "jpeg", "png", "docx", "bat", "exe", "apk"]
                img = ["jpg", "jpeg", "png"]

                if filename.split(".")[-1] not in allowed:
                    self.show_toaster("File-ending not allowed.")
                    return

                if filename.split(".")[-1] not in img:

                    self.sock.send("FILE:::::".encode())

                    print("FILENAME:", filename)
                    time.sleep(.5)
                    print("aaa")

                    # self.sock.send(f"{Encrypt(message_=filename, key=group_key).encrypt().decode()}".encode())
                    self.sock.send(filename.encode())

                    time.sleep(.5)
                    print("aaa")

                    self.sock.send(self.username.encode())

                    time.sleep(.5)
                    print("aaa")

                    content = encode_file(file_path, group_key)
                    print(content)
                    self.sock.send(content)

                    time.sleep(1)

                    self.sock.send("DONE:".encode())

                    # self.screen_manager.get_screen("chat").chat_list.add_widget(
                    #    Command(text=filename, size_hint_x=.75, halign="center"))
                    self.add_file_cmd(filename)
                else:
                    self.sock.send("IMAGE:::::".encode())

                    time.sleep(1)
                    print("aaa")

                    print("FILENAME:", filename)
                    # self.sock.send(f"{Encrypt(message_=filename, key=group_key).encrypt().decode()}".encode())
                    self.sock.send(filename.encode())

                    time.sleep(1)
                    print("aaas")

                    self.sock.send(self.username.encode())

                    time.sleep(1)
                    print("aaass")

                    # with open(file_path, 'rb') as f:
                    #    img_data = f.read()
                    img_data = encode_file(file_path, group_key)
                    self.sock.sendall(img_data)

                    time.sleep(.5)
                    self.sock.sendall(b":ENDED:")

                    self.add_img_cmd(file_path)
                    # self.screen_manager.get_screen("chat").chat_list.add_widget(
                    #    Command(text=filename, size_hint_x=.75, halign="center"))

        except Exception as e:
            print("Error16:", e)
            self.show_toaster("Couldn't send file.")

    def delete_everything(self):
        try:
            self.show_toaster("Your data will now be deleted.")
            self.connect()
            self.sock.send(f"DELETE_ALL:{self.username}:{hash_pwd(self.password)}".encode())
            r = self.sock.recv(1024).decode()
            if r == "success":
                """
                print("[i] Deleting groups.csv")
                with open("data/groups.csv", "a") as aa:
                    for i in range(100):
                        aa.write(str(gen(20)) + "\n")
                with open("groups.csv", "w") as aaa:
                    aaa.write("")
                os.remove("groups.csv")
                
                print("[i] Deleting public_key.txt")
                with open("data/groups.csv", "a") as aa:
                    for i in range(100):
                        aa.write(str(gen(20)) + "\n")
                with open("public_key.txt", "w") as aaa:
                    aaa.write("")
                os.remove("public_key.txt")
                
                print("[i] Deleting private_key.txt")
                with open("private_key.txt", "a") as aa:
                    for i in range(100):
                        aa.write(str(gen(20)) + "\n")
                with open("private_key.txt", "w") as aaa:
                    aaa.write("")
                os.remove("private_key.txt")
                """
                try:
                    pass
                    # os.remove(os.path.basename(__file__))
                except:
                    pass
                self.screen_manager.current = "signup"
            else:
                self.show_toaster("Error deleting data.")

        except Exception as e:
            print("Error17:", e)
            pass
        return

    def show_toaster(self, message):
        toast(message)

    def notify(self, title, message):
        notification.notify(
            title=title,
            message=message,
            timeout=10,
            app_name='Encochat'
        )

    def show_id(self):
        try:
            # pc.copy(self.id)
            Clipboard.copy(self.id)
            qr = qrcode.make(self.id)
            qr.save("qr_code_id.png")

            self.screen_manager.get_screen("show_id").img.reload()

            self.screen_manager.current = "show_id"
        except Exception as e:
            print("Error18:", e)
            pass

    def download(self, file_source):
        print('File clicked:', file_source)
        try:
            with open(file_source) as file:
                content = file.read()
            with open(os.path.join(primary_external_storage_path(), "Downloads"), "w") as write_file:
                write_file.write(content)
            toast("File saved to Downloads.")
        except Exception:
            toast("Couldn't save file.")

    def accept_tos(self, _, value_):
        global accepted
        if value_:
            accepted = True
        else:
            accepted = False

    def show_secret(self):
        try:
            with open("private_key.txt", "r") as priv_file:
                qr = qrcode.make(priv_file.read())
                qr.save("private_key.png")
            self.screen_manager.current = "show_secret"
        except Exception as e:
            print("Error QR:", e)

    def loader(self, *args):
        if self.key_genned:
            Clock.unschedule(self.loader)
        else:
            try:
                self.i += 1
                self.screen_manager.get_screen("progress_bar").progress.value = self.i
                self.started_g = True
            except:
                Clock.unschedule(self.loader)

    def do_smt(self):
        self.screen_manager.current = "progress_bar"
        Clock.schedule_interval(self.loader, 0.4)  # 3

    def gen(self, username, password, uid):
        print("n")
        while not self.started_g:
            pass
        print("bb")
        public, private = rsa.newkeys(4096)


        print("finished")

        if not self.stop_genning:
            self.key_genned = True
            self.public_key = public
            self.private_key = private
        # self.screen_manager.current = "home"
            self.okok(username, password, uid)

    def connect_voice(self, recipient):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 5000))
        self.client_socket.send(self.username.encode())
        print("aaa")
        time.sleep(.5)
        self.client_socket.send(recipient.encode())

    """
    def record(self):
        while not self.hanged:
            try:
                data = self.stream.read(self.CHUNK)
                self.client_socket.send(data)
            except Exception as e:
                print(e)
                break
        print("cbroken")

    def receive_voice(self):
        self.client_socket.settimeout(5)  # waiting for other user to pick up
        while not self.hanged:
            try:
                # read audio data from the microphone
                data = self.client_socket.recv(1024)
                self.client_socket.settimeout(1)
                try:
                    self.sound.stop()
                except:
                    pass
                if not data:
                    break
                print(data)
                self.streamOut.write(data)
                self.call_started = True
            except Exception as e:
                print(e)
                break
        self.hangup()
        print("a", self.client_socket.gettimeout())
        if self.call_started:
            print("Recpipient ended call.")
            # toast("Recipient ended call.")
        else:
            print("Couldn't connect.")
            # toast("Normal end.")
        print("bbroken")
    """

    def record(self):
        with sd.InputStream(channels=self.CHANNELS, blocksize=self.BLOCK_SIZE) as stream:
            print('start recording')
            while not self.hanged:
                try:
                    data, overflowed = stream.read(self.BLOCK_SIZE)
                    if overflowed:
                        print('Input stream overflowed!')
                    self.client_socket.sendall(data)
                except Exception as e:
                    print(e)
                    break
            stream.close()
        print("cbroken")

    def receive_voice(self):
        with sd.OutputStream(channels=self.CHANNELS, blocksize=self.BLOCK_SIZE) as stream:
            print('start playing')
            self.client_socket.settimeout(5)
            while not self.hanged:
                try:
                    data = self.client_socket.recv(self.BLOCK_SIZE)
                    if not data:
                        break
                    self.client_socket.settimeout(1)
                    try:
                        self.sound.stop()
                    except:
                        pass
                    self.call_started = True
                    stream.write(np.frombuffer(data, dtype=np.float32))
                except Exception as e:
                    print(e)
                    break
            stream.stop()
        self.hangup()
        print("a", self.client_socket.gettimeout())
        if self.call_started:
            print("Recpipient ended call.")
            # toast("Recipient ended call.")
        else:
            print("Couldn't connect.")
            # toast("Normal end.")
        print("bbroken")

    def call(self, recipient):
        if recipient != "":
            self.connect()
            self.sock.send(f"USER_EXISTS:{recipient}".encode())
            if self.sock.recv(1024) == b"exists":
                self.sound.play()
                self.hanged = False
                self.call_initiated = True
                self.connect_voice(recipient)
                print(recipient)
                a = threading.Thread(target=self.record)
                b = threading.Thread(target=self.receive_voice)
                self.threads.append(a)
                self.threads.append(b)
                a.start()
                b.start()
                self.screen_manager.get_screen("call").name_.text = ""
                self.screen_manager.get_screen("hangup").caller_id.text = recipient
                self.screen_manager.current = "hangup"
            else:
                toast("Invalid.")
        else:
            toast("Invalid.")

    @mainthread
    def hangup(self):
        self.client_socket.close()
        print("im here")
        try:
            self.sound.stop()
        except:
            pass
        self.hanged = True
        self.call_started = False
        self.call_initiated = False
        self.screen_manager.current = "call"
        for item in self.threads:
            try:
                item.join()
            except:
                pass
        print("okay")

    def receive_sec(self):
        self.screen_manager.current = "receive"
        self.receiving = True
        self.screen_manager.get_screen("receive").my_key.text = self.get_local_ip()
        # self.start_server()
        threading.Thread(target=self.start_server).start()

    def start_server(self):
        print("starte")
        sec = open("private_key.txt", "rb")
        data = sec.read()
        sec.close()

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("localhost", 8989))
        server.listen()

        while self.receiving:
            client, addr = server.accept()
            print(client)
            client.send(data)
            server.close()

            self.show_toaster("Private key received. Please login again.")
            self.screen_manager.current = "login"

            break
        server.close()

    def transfer(self, ip):
        print(ip)
        self.send_private(ip)

    def send_private(self, ip_addr):
        try:
            sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_client.connect((ip_addr, 8989))

            priv = sock_client.recv(1024)
            sock_client.close()
            with open("private_key.txt", "wb") as priv_file:
                priv_file.write(priv)
        except:
            self.show_toaster("Invalid server.")

    def get_local_ip(self):
        return socket.gethostbyname(socket.gethostname())

    def exit_receiving(self):
        self.receiving = False
        self.screen_manager.current = "home"

    def stop_key_gen(self):
        self.stop_genning = True
        try:
            Clock.unschedule(self.loader)
        except:
            pass
        self.screen_manager.get_screen("signup").username.text = ""
        self.screen_manager.get_screen("signup").password.text = ""
        self.screen_manager.get_screen("signup").password2.text = ""
        self.screen_manager.current = "signup"
        self.show_toaster("Stopped.")


if __name__ == "__main__":
    LabelBase.register(name="MPoppins",
                       fn_regular="Poppins-Medium.ttf")
    LabelBase.register(name="BPoppins",
                       fn_regular="Poppins-SemiBold.ttf")
    ChatApp().run()

