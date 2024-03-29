import json
import re

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

# QR-Scanning
import numpy
import cv2
from pyzbar.pyzbar import decode

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
import subprocess
import tempfile

# Request Perms
from kivy.utils import platform

from jnius import autoclass

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
    switch: switch

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

                MDSwitch:
                    id: switch
                    pos_hint: {"center_x": .8, "center_y": .45}
                    width: dp(45) 
                    on_touch_down:
                        app.secure_check()


                MDLabel:
                    text: "Secure Mode?"
                    font_name: "MPoppins"
                    pos_hint: {"center_x": .7, "center_y": .45}
                    font_size: "14sp"

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
                        app.show_toaster("This feature isn't supported yet")
                        # root.manager.transition.direction = "left"
                        # root.manager.current = "call"
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
    name__: name__
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
                id: name__
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
            MDIconButton:
                icon: "qrcode-scan"
                color: 0, 0, 0, 0.4
                text_color: 0, 0, 0, 0.4
                theme_text_color: "Custom"
                pos_hint: {"center_x": 1, "center_y": .5}
                on_release:
                    # root.manager.transition.direction = "left"
                    # root.manager.current = "qr-scan"
                    app.start_qr()
        # qrcode-scan

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
                app.create_chat(name__.text)
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
                    app.sock.close()
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
                app.create_group_symmetrical(name_.text)


"""
group_create_asy = """
MDScreen:
    name: "group_create_asy"
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
                app.create_group_asymmetrical(name_.text)


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
                        # root.manager.current = "group_create"
                        root.manager.current = "con"
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
    name_: name_
    switch: switch

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
                id: name_
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
            MDIconButton:
                icon: "qrcode-scan"
                color: 0, 0, 0, 0.4
                text_color: 0, 0, 0, 0.4
                theme_text_color: "Custom"
                pos_hint: {"center_x": 1, "center_y": .5}
                on_release:
                    # root.manager.transition.direction = "left"
                    # root.manager.current = "qr-scan"
                    app.start_qr_group()

        MDSwitch:
            id: switch
            pos_hint: {"center_x": .8, "center_y": .45}
            width: dp(45)  

        MDLabel:
            text: "Asymmetrical?"
            font_name: "MPoppins"
            pos_hint: {"center_x": .7, "center_y": .45}
            font_size: "14sp"


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
                app.join_new_group(name_.text, switch.active)


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
            size: 400, 400
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
        Button:
            text: "Settings"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .1}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(52, 0, 231, 255)
            on_release:
                root.manager.transition.direction = "left"
                root.manager.current = "group_settings"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
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
        Button:
            text: "Settings"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .1}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(52, 0, 231, 255)
            on_release:
                app.show_toaster("Not implemented yet")
                # root.manager.transition.direction = "left"
                # root.manager.current = "group_settings"
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

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
    # BoxLayout:
    #     orientation: 'vertical'
    #     padding: 0
    #     Label:
    #         text: root.fro
    #         font_size: 40
    #         color: (0, 0, 1, 1)
    #         halign: 'left'
    #         size_hint_x: .22
    #     MDLabel:
    #       text: root.text
    #       font_size: 50
    #       halign: "center"
<AddImage>
    size_hint_y: None
    pos_hint: {"x": -.3}
    height: 600

<AddImageCommand>
    size_hint_y: None
    pos_hint: {"right": 1.2}
    height: 600

<AddFile>
    # size_hint_y: None
    # pos_hint: {"x": .02}
    # height: self.texture_size[1]
    # padding: 12, 10

    size_hint_y: None
    pos_hint: {"x": .02}
    padding: 12, 10
    theme_text_color: "Custom"

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
                halign: 'right'
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
        orientation: 'horizontal'
        adaptive_height: True
        # size_hint: None, None
        MDBoxLayout:
            MDLabel:
                id: llabel
                text: root.file_source
                font_size: 12
                color: 1, 1, 1, 1
                halign: 'right'
                size_hint_x: .22
            MDIconButton:
                icon: "download"
                on_release:
                    app.download(llabel.text)
<AddAudio>
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

<AddAudioCommand>
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
        # size_hint: None, None
        MDBoxLayout:
            MDLabel:
                text: "Play Audio"
                font_size: 12
                color: (0, 0, 1, 1)
                font_name: "BPoppins"
            MDIconButton:
                id: play_pause
                icon: "play-circle-outline"  # pause-circle-outline
                on_release:
                    root.play(root.file_source)
<newJoin>
    size_hint_y: None
    padding: 12, 10
    theme_text_color: "Custom"
    text_color: 142, 142, 142, 0.77
    halign: "center"
    valign: "center"

<newLeave>
    size_hint_y: None
    padding: 12, 10
    theme_text_color: "Custom"
    text_color: 142, 142, 142, 0.77
    halign: "center"
    valign: "center"

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
                    # app.stop_group_thread()
                    app.sock.close()
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
        pos_hint: {"center_x": .95, "center_y": .9}
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
                hint_text: "Enter chat number"
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
    warning: warning

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
            font_size: "14sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)

    # MDFloatLayout:
        # md_bg_color: 1, 1, 1, 1
        MDProgressBar:
            id: progress
            value: 0
            size_hint: .8, None
            pos_hint: {"center_x": .5, "center_y": .3}

        MDLabel:
            id: warning
            text: "This is taking longer than expected."
            font_name: "MPoppins"
            font_size: "16sp"
            opacity: 0
            pos_hint: {"center_x": .6, "center_y": .22}
            color: rgba(135, 133, 193, 255)
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
            pos_hint: {"center_x": .6, "center_y": .75}
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

qr_scan__ = """
MDScreen:
    name: "qr-scan"
    camera: camera

    MDIconButton:
        icon: "arrow-left"
        pos_hint: {"center_y": .95}
        user_font_size: "30sp"
        theme_text_color: "Custom"
        text_color: rgba(26, 24, 58, 255)
        on_release:
            app.stop_qr()
            # root.manager.transition.direction = "right"
            # root.manager.current = "home"

    BoxLayout:
        orientation: 'vertical'
        Camera:
            id: camera
            resolution: (640, 480)
            play: False
            canvas.before:
                PushMatrix
                Rotate:
                    angle: -90
                    origin: self.center
            canvas.after:
                PopMatrix
        Button:
            text: 'Capture'
            size_hint_y: None
            height: '48dp'
            on_press: app.capture()
"""
qr_scan = """
MDScreen:
    name: "qr-scan"
    camera: camera

    BoxLayout:
        orientation: 'vertical'

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)            
            on_release:
                app.stop_qr()
                # root.manager.transition.direction = "right"
                # root.manager.current = "home"

        Camera:
            id: camera
            # resolution: (640, 480)
            allow_stretch: True
            keep_ratio: True
            play: False
            canvas.before:
                PushMatrix
                Rotate:
                    angle: -90
                    origin: self.center
            canvas.after:
                PopMatrix


        Button:
            text: 'Capture'
            size_hint_y: None
            height: '48dp'
            on_press: app.capture()
"""

qr_scan_group = """
MDScreen:
    name: "qr-scan-group"
    camera: camera

    BoxLayout:
        orientation: 'vertical'

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)            
            on_release:
                app.stop_qr_group()
                # root.manager.transition.direction = "right"
                # root.manager.current = "home"

        Camera:
            id: camera
            # resolution: (640, 480)
            allow_stretch: True
            keep_ratio: True
            play: False
            canvas.before:
                PushMatrix
                Rotate:
                    angle: -90
                    origin: self.center
            canvas.after:
                PopMatrix


        Button:
            text: 'Capture'
            size_hint_y: None
            height: '48dp'
            on_press: app.capture_group()
"""

group_settings = """
MDScreen:
    name: "group_settings"

    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1
        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_y": .95}
            user_font_size: "30sp"
            theme_text_color: "Custom"
            text_color: rgba(26, 24, 58, 255)
            on_release:
                app.go_back_group()
                # root.manager.transition.direction = "right"
                # root.manager.current = "chat"
        MDLabel:
            text: "Group Settings"
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Only works if you are admin."
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)

        MDFloatLayout:
            size_hint_y: .11
            MDFloatLayout:
                size_hint: .8, .75
                pos_hint: {"center_x": .43, "center_y": 6}
                TextInput:
                    id: text_input3
                    hint_text: "Rename"
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
                icon: "square-edit-outline"
                pos_hint: {"center_x": .91, "center_y": 6}
                user_font_size: "12sp"
                text_color: 1, 1, 1, 1
                on_release:
                    app.rename_group(text_input3.text)
        Button:
            text: "Delete Group"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .35}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(240, 40, 40, 255)
            on_release:
                app.delete_group()
            canvas.before:
                Color:
                    rgb: rgba(240, 40, 40, 255)
                    # rgb: rgba(52, 0, 231, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

"""

popup_update = """
MDScreen:
    name: "popup_update"

    MDFloatLayout:
        MDFloatLayout:
            # md_bg_color: 245/255, 245/255, 245/255, 1
            size_hint_y: .11
            pos_hint: {"center_y": .95}
            MDIconButton:
                icon: "close"
                pos_hint: {"center_y": .5, "center_x": .9}
                user_font_size: "30sp"
                theme_text_color: "Custom"
                text_color: rgba(26, 24, 58, 255)
                on_release:
                    root.manager.transition.direction = "right"
                    root.manager.current = "login"
        MDLabel:
            text: "Update Available"
            font_name: "BPoppins"
            font_size: "23sp"
            pos_hint: {"center_y": .9}
            halign: "center"
            color: rgba(34, 34, 34, 255)
        MDLabel:
            text: "Please update to the new version."
            font_name: "BPoppins"
            font_size: "13sp"
            size_hint_x: .85
            pos_hint: {"center_x": .5, "center_y": .8}
            halign: "center"
            color: rgba(127, 127, 127, 255)
        Button:
            text: "Update Now"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .2}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(52, 0, 231, 255)
            on_release:
                app.download_update()
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
        Button:
            text: "Skip"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .1}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(240, 40, 40, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "login"
            canvas.before:
                Color:
                    rgb: rgba(240, 40, 40, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

"""
popup_warning = """
MDScreen:
    name: "popup_warning"

    MDFloatLayout:
        MDFloatLayout:
            # md_bg_color: 245/255, 245/255, 245/255, 1
            size_hint_y: .11
            pos_hint: {"center_y": .95}
            MDIconButton:
                icon: "close"
                pos_hint: {"center_y": .5, "center_x": .9}
                user_font_size: "30sp"
                theme_text_color: "Custom"
                text_color: rgba(26, 24, 58, 255)
                on_release:
                    root.manager.transition.direction = "right"
                    root.manager.current = "login"
        MDLabel:
            text: "Update Available"
            font_name: "BPoppins"
            font_size: "23sp"
            pos_hint: {"center_y": .9}
            halign: "center"
            color: rgba(34, 34, 34, 255)
        MDLabel:
            text: "Please update to the new version."
            font_name: "BPoppins"
            font_size: "13sp"
            size_hint_x: .85
            pos_hint: {"center_x": .5, "center_y": .8}
            halign: "center"
            color: rgba(127, 127, 127, 255)
        Button:
            text: "Update Now"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .2}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(52, 0, 231, 255)
            on_release:
                app.download_update()
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
        Button:
            text: "Skip"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .1}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(240, 40, 40, 255)
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "login"
            canvas.before:
                Color:
                    rgb: rgba(240, 40, 40, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
"""

con = """
MDScreen:
    name: "con"
    slider: slider
    btn: btn
    llabel: llabel

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
            text: "Choose mode"
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Please choose type of group."
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)

        Slider:
            id: slider
            min: 25
            max: 100
            step: 1
            orientation: 'horizontal'   
            pos_hint: {"center_x": .5, "center_y": .35}
            size_hint_x: 0.7
            opacity: 0

            cursor_image: "abc.png"

        Button:
            text: "Asymmetrical"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .6}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(52, 0, 231, 255)
            on_release:
                # app.show_toaster("Not implemented yet")
                app.create_group_asymmetrical("None")
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

        Button:
            text: "Symmetrical"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .5}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(52, 0, 231, 255)
            on_release:
                llabel.opacity = 1
                slider.opacity = 1
                btn.opacity = 1
                # app.create_group_symmetrical("None", slider.value)
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

        MDLabel:
            id: llabel
            text: "Choose key size:"
            front_name: "BPoppins"
            pos_hint: {"center_x": .6, "center_y": .4}
            font_size: "18sp"
            color: rgba(135, 133, 193, 255)
            opacity: 0

        Button:
            id: btn
            opacity: 0
            text: "Continue"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .22}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(52, 0, 231, 255)
            on_release:
                app.create_group_symmetrical("None", slider.value)
            canvas.before:
                Color:
                    rgb: rgba(52, 0, 231, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100

"""

chat_asy = """
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
    # BoxLayout:
    #     orientation: 'vertical'
    #     padding: 0
    #     Label:
    #         text: root.fro
    #         font_size: 40
    #         color: (0, 0, 1, 1)
    #         halign: 'left'
    #         size_hint_x: .22
    #     MDLabel:
    #         text: root.text
    #         font_size: 50
    #         halign: "center"
<AddImage>
    size_hint_y: None
    pos_hint: {"x": -.3}
    height: 600

<AddImageCommand>
    size_hint_y: None
    pos_hint: {"right": 1.2}
    height: 600

<AddFile>
    # size_hint_y: None
    # pos_hint: {"x": .02}
    # height: self.texture_size[1]
    # padding: 12, 10

    size_hint_y: None
    pos_hint: {"x": .02}
    padding: 12, 10
    theme_text_color: "Custom"

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
                halign: 'right'
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
        orientation: 'horizontal'
        adaptive_height: True
        # size_hint: None, None
        MDBoxLayout:
            MDLabel:
                id: llabel
                text: root.file_source
                font_size: 12
                color: 1, 1, 1, 1
                halign: 'right'
                size_hint_x: .22
            MDIconButton:
                icon: "download"
                on_release:
                    app.download(llabel.text)
<AddAudio>
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

<AddAudioCommand>
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
        # size_hint: None, None
        MDBoxLayout:
            MDLabel:
                text: "Play Audio"
                font_size: 12
                color: (0, 0, 1, 1)
                font_name: "BPoppins"
            MDIconButton:
                id: play_pause
                icon: "play-circle-outline"  # pause-circle-outline
                on_release:
                    root.play(root.file_source)
<newJoin>
    size_hint_y: None
    padding: 12, 10
    theme_text_color: "Custom"
    text_color: 142, 142, 142, 0.77
    halign: "center"
    valign: "center"

<newLeave>
    size_hint_y: None
    padding: 12, 10
    theme_text_color: "Custom"
    text_color: 142, 142, 142, 0.77
    halign: "center"
    valign: "center"

MDScreen:
    name: "chat_asy"
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
                    app.sock.close()
                    root.manager.transition.direction = "right"
                    root.manager.current = "home"
            MDIconButton:
                icon: "content-copy"
                pos_hint: {"center_x": .9, "center_y": .5}
                on_release:
                    app.show_settings_asy()

            MDLabel:
                text: ""
                id: bot_name
                pos_hint: {"center_y": .5}
                halign: "center"
                font_name: "BPoppins"
                font_size: "25sp"
                theme_text_color: "Custom"
                text_color: 53/255, 56/255, 60/255, 1

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
                    app.send_message_asy(text_input.text)
"""

pinn_old = """
MDScreen:
    name: "pinn"
    Popup:
        title: "Enter PIN"
        size_hint: None, None
        # size: 400, 200
        size: root.size
    
        BoxLayout:
            orientation: "vertical"
            padding: 20
    
            Label:
                text: "Please enter your PIN:"
                
    
            TextInput:
                id: pin_input
                input_type: "number"
                
                password: True
    
            Button:
                text: "Submit"
                
                on_release: app.authenticate_pin(pin_input.text)
"""


pinn = """
MDScreen:
    name: "pinn"
    
    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1

        MDLabel:
            text: "Enter your PIN."
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .9}
            color: rgba(0, 0, 59, 255)
                        
    GridLayout:
        cols: 3
        spacing: 5
        padding: 20
        
        size_hint: 1, 1
        pos_hint: {'center_x': 0.5, 'center_y': 0.1}
        
        # pos_hint: {"center_y": .5}
        
        MDIconButton:
            icon: 'numeric-1-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(1)
            
        
        MDIconButton:
            icon: 'numeric-2-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(2)
            
        
        MDIconButton:
            icon: 'numeric-3-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(3)
            
        
        MDIconButton:
            icon: 'numeric-4-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(4)
            
        
        MDIconButton:
            icon: 'numeric-5-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(5)
            
        
        MDIconButton:
            icon: 'numeric-6-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(6)
            
        
        MDIconButton:
            icon: 'numeric-7-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(7)
            
        
        MDIconButton:
            icon: 'numeric-8-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(8)
            
             
        MDIconButton:
            icon: 'numeric-9-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(9)
            
        
        MDIconButton:
            icon: 'slash-forward'
            disabled: True
            size_hint_x: 0.33
            # opacity: 0
            
        
        MDIconButton:
            icon: 'numeric-0-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(0)
            
        
        MDIconButton:
            icon: 'slash-forward'
            disabled: True
            size_hint_x: 0.33
            # opacity: 0
    
    Button:
        text: "Continue"
        size_hint: .66, .065
        pos_hint: {"center_x": .5, "center_y": .1}
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
            app.authenticate_pin()
"""
pinn_create = """
MDScreen:
    name: "pinn_create"

    MDFloatLayout:
        md_bg_color: 1, 1, 1, 1

        MDLabel:
            text: "Create your PIN."
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .9}
            color: rgba(0, 0, 59, 255)

    GridLayout:
        cols: 3
        spacing: 5
        padding: 20

        size_hint: 1, 1
        pos_hint: {'center_x': 0.5, 'center_y': 0.1}

        # pos_hint: {"center_y": .5}

        MDIconButton:
            icon: 'numeric-1-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(1)


        MDIconButton:
            icon: 'numeric-2-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(2)


        MDIconButton:
            icon: 'numeric-3-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(3)


        MDIconButton:
            icon: 'numeric-4-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(4)


        MDIconButton:
            icon: 'numeric-5-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(5)


        MDIconButton:
            icon: 'numeric-6-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(6)


        MDIconButton:
            icon: 'numeric-7-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(7)


        MDIconButton:
            icon: 'numeric-8-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(8)


        MDIconButton:
            icon: 'numeric-9-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(9)


        MDIconButton:
            icon: 'slash-forward'
            disabled: True
            size_hint_x: 0.33
            # opacity: 0


        MDIconButton:
            icon: 'numeric-0-circle-outline'
            size_hint_x: 0.33
            on_release:
                app.pin_list.append(0)


        MDIconButton:
            icon: 'slash-forward'
            disabled: True
            size_hint_x: 0.33
            # opacity: 0

    Button:
        text: "Finish"
        size_hint: .66, .065
        pos_hint: {"center_x": .5, "center_y": .1}
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
            app.create_pin()
"""

warning = """
MDScreen:
    name: "warning"

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
            text: "Warning!"
            font_name: "BPoppins"
            font_size: "26sp"
            pos_hint: {"center_x": .6, "center_y": .85}
            color: rgba(0, 0, 59, 255)

        MDLabel:
            text: "Signing Error."
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .79}
            color: rgba(135, 133, 193, 255)
        
        MDLabel:
            text: "The message just send may"
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .69}
            color: rgba(135, 133, 193, 255)
        MDLabel:
            text: "has been tampered."
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .65}
            color: rgba(135, 133, 193, 255)
        
        MDLabel:
            text: "Proceed with caution."
            font_name: "BPoppins"
            font_size: "18sp"
            pos_hint: {"center_x": .6, "center_y": .59}
            color: rgba(135, 133, 193, 255)

        Button:
            text: "Proceed"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .34}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(240, 40, 40, 255)
            on_release:
                app.screen_manager.current = "chat_sec"
            canvas.before:
                Color:
                    rgb: rgba(240, 40, 40, 255)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100
        
        Button:
            text: "End Convo"
            size_hint: .66, .065
            pos_hint: {"center_x": .5, "center_y": .24}
            background_color: 0, 0, 0, 0
            front_name: "BPoppins"
            color: rgba(173,255,47,255)
            on_release:
                app.screen_manager.current = "chat_sec"
            canvas.before:
                Color:
                    rgb: rgba(173,255,47,1)
                Line:
                    width: 1.2
                    rounded_rectangle: self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100             

"""

# TODO: Encrypted Calling

# socket.setdefaulttimeout(5)

# from PIL import Image

Window.keyboard_anim_args = {"d": .2, "t": "in_out_expo"}
Window.softinput_mode = "below_target"

# print(f"Using pq_ntru version {pq_ntru.__version__}")

######################### BASIC VARIABLES #########################
group_key = ""
user = ""

current_private_key = b""
current_chat_with = ""

is_it_my_turn = False

accepted = False

received_secret = False
sent_secret = False

with open('config.json') as f:
    js = json.load(f)

# 2.tcp.eu.ngrok.io:13117
# HOST = "5.tcp.eu.ngrok.io"
# PORT = 15921  # The port used by the server
try:
    HOST, PORT = requests.get("https://api.protdos.com").text.split(":")
    PORT = int(PORT)
    print("Using host, port:", HOST, PORT)
except:
    HOST, PORT = None, None

if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    from android.runnable import run_on_ui_thread
    from android import mActivity as mA

    request_permissions([Permission.INTERNET, Permission.INSTALL_PACKAGES])
else:
    Window.size = (310, 580)
    HOST, PORT = "localhost", 5001


def connect_again():
    global HOST, PORT
    try:
        HOST, PORT = requests.get("https://api.protdos.com").text.split(":")
        PORT = int(PORT)
        return True
    except:
        return False


######################### Chat #########################
class Command(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "BPoppins"
    font_size = 50


class Response(MDLabel):
    text = StringProperty()
    # fro = StringProperty()
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


class AddAudio(BoxLayout):
    file_source = StringProperty()
    font_name = "BPoppins"
    font_size = 12


class AddAudioCommand(BoxLayout):
    file_source = StringProperty()
    font_name = "BPoppins"
    font_size = 12

    def play(self, path):
        print("playing", path)
        SoundLoader.load(path).play()


class newJoin(MDLabel):
    text = StringProperty()


class newLeave(MDLabel):
    text = StringProperty()


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
        policy = PasswordPolicy()
        out = policy.password(p).strength()
        print(out)
        return [True if out > 0.35 else False]  # returning if password is good or not
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


def hashCrackWordlist(userHash):
    h = hashlib.sha256

    with open("Wordlist.txt", "rb") as infile:
        for line in infile:
            try:
                line = line.strip()
                lineHash = h(line).hexdigest()

                if str(lineHash) == str(userHash.lower()):
                    return line.decode()
            except:
                pass

        return None


def is_uuid4(stri):
    pattern = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[8|9aAbB][a-f0-9]{3}-[a-f0-9]{12}$')
    if pattern.match(stri):
        try:
            uuid.UUID(stri)
            return True
        except ValueError:
            pass
    return False


######################### Main #########################
class ChatApp(MDApp):
    sock = None
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
    public = None
    private = None
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

    sound = None
    BLOCK_SIZE = None

    receiving = False

    client_socket = None

    stop_genning = False

    group_chat_started = False
    group_asy_chat_started = False

    group_name = None

    download_url = None

    current_public_keys_group = []

    key_length = 100

    screenshot_dir = ""

    previous_screenshot_count = 0

    mess_list = []
    mess_list_group = []
    mess_list_asy = []

    errors = 0
    pin_list = []

    is_authed = False

    """  Flag Secure
    @run_on_ui_thread
    def on_start(self):
        LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
        window = mA.getWindow()
        params = window.getAttributes()
        params.setDecorFitsSystemWindows = False
        params.layoutInDisplayCutoutMode = LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
        window.setAttributes(params)
        window.setFlags(LayoutParams.FLAG_SECURE, LayoutParams.FLAG_SECURE)
        try:
            window.addFlags(LayoutParams.FLAG_SECURE)
        except:
            print("aaaa")
    """

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
            # self.check_for_updates()
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

            # threading.Thread(target=self.check_for_updates).start()

            try:
                Window.set_icon("logo.png")
            except:
                print("Couldn't set icon.")

            self.screen_manager = ScreenManager()

            self.screen_manager.add_widget(Builder.load_string(signup))
            self.screen_manager.add_widget(Builder.load_string(pinn))
            self.screen_manager.add_widget(Builder.load_string(login))
            self.screen_manager.add_widget(Builder.load_string(progress_bar))
            self.screen_manager.add_widget(Builder.load_string(home))
            self.screen_manager.add_widget(Builder.load_string(chat_private))
            self.screen_manager.add_widget(Builder.load_string(chat_sec))
            self.screen_manager.add_widget(Builder.load_string(main))
            self.screen_manager.add_widget(Builder.load_string(group_create))
            self.screen_manager.add_widget(Builder.load_string(group_join))
            self.screen_manager.add_widget(Builder.load_string(group))
            self.screen_manager.add_widget(Builder.load_string(warning))
            self.screen_manager.add_widget(Builder.load_string(pinn_create))
            self.screen_manager.add_widget(Builder.load_string(password_reset))
            self.screen_manager.add_widget(Builder.load_string(chat_new_private))
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

            self.screen_manager.add_widget(Builder.load_string(qr_scan))

            self.screen_manager.add_widget(Builder.load_string(group_settings))

            self.screen_manager.add_widget(Builder.load_string(popup_update))
            self.screen_manager.add_widget(Builder.load_string(popup_warning))

            self.screen_manager.add_widget(Builder.load_string(con))

            self.screen_manager.add_widget(Builder.load_string(chat_asy))
            self.screen_manager.add_widget(Builder.load_string(group_create_asy))

            self.screen_manager.add_widget(Builder.load_string(qr_scan_group))

            # Clock.schedule_once(self.check_for_updates, 0)
            Clock.schedule_once(self.check_unauthorized_access, 0)
            Clock.schedule_once(self.check_stay, 0)
            # Clock.schedule_once(self.check_pin, 0)

            threading.Thread(target=self.send_working_private).start()
            threading.Thread(target=self.send_working_asy).start()
            threading.Thread(target=self.send_working_group).start()
            # threading.Thread(target=self.check_stay).start()
            # threading.Thread(target=self.check_pin).start()

            return self.screen_manager
        except Exception as e:
            print("Error21:", e)

    def on_start(self):
        try:
            if platform == 'android':
                self.screenshot_dir = '/sdcard/Pictures/Screenshots'
            else:
                self.screenshot_dir = os.path.join(os.path.expanduser('~'), 'Pictures', 'Screenshots')
            self.previous_screenshot_count = len(os.listdir(self.screenshot_dir))
            Clock.schedule_interval(self.check_screenshots, 1)
        except:
            print("v1 failed")
            try:
                self.screenshot_dir = "/storage/emulated/0/DCIM/Screenshots/"
                self.previous_screenshot_count = len(os.listdir(self.screenshot_dir))
                Clock.schedule_interval(self.check_screenshots, 1)
            except:
                print("v2 failed.")

    def check_stay(self, *args):
        if os.path.isfile("stay_sign_in.txt"):
            self.username, self.password = open("stay_sign_in.txt", "r").read().split("\n")

            self.connect()
            self.sock.send(f"LOGIN:::{self.username}:::{hash_pwd(self.password)}".encode())
            r = self.sock.recv(1024).decode()
            # print(r)
            if r == "error":
                self.show_toaster("Invalid username")
                self.screen_manager.get_screen("login").username.text = ""
                self.screen_manager.get_screen("login").password.text = ""
                return
            elif r == "errorv2":
                self.show_toaster("Invalid password")
                self.screen_manager.get_screen("login").password.text = ""
                return
            else:
                if self.username != "Google":
                    with open(f"private_key_{self.username}.txt", "r") as file:
                        a = file.read()
                        dec_priv = Decrypt(message_=a, key=self.password).decrypt().encode()
                        # print(dec_priv)
                        if dec_priv is None:
                            self.show_toaster("Private key couldn't be decrypted.")
                            return
                        self.private_key = rr.PrivateKey.load_pkcs1(dec_priv)
                else:
                    self.public_key = rr.PublicKey.load_pkcs1(
                        b'-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDzSvum\nujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR3WDH\nxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/QQIC\nnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krroi6PiRF3hVvEiTLXh\nNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC8yjz\nV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQAB\n-----END RSA PUBLIC KEY-----\n')
                    self.private_key = rr.PrivateKey.load_pkcs1(
                        b'-----BEGIN RSA PRIVATE KEY-----\nMIIEqQIBAAKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDz\nSvumujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR\n3WDHxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/\nQQICnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krroi6PiRF3hVvEi\nTLXhNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC\n8yjzV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQABAoIBACKRh5SKEdNFxgdX\ncqWp6G0AeNWD9TX7e0ow5T+qsKB8ixkbJIb7fbtawRMp6IwAukhTXcinTD2dK2mC\nkJbWKksNwoUjqZgBZApeTBU/vP+H1STbdWCgOfzfHdYLlvEks6t8vsGcssri5SPv\nMb1Mk8XCgjfU5ZZ26ekuVV0VJLoMAeTQT9GSQBPeLLI38YQsLvWWLBiGP+zbAC9E\nH7JhnLf6yZzcWUrt8F8uFclydM1Zl/Jzvtf2v7DXZBapr7goykgJt+dfOqG6L3mN\n7K7HIKPMdWT/j2TiS9bjEik7NQV/CkqltNE+SiXJqddDqHJZklHSSKERUgNoc+s1\nvKPS1XUCgYkAutyUZcFY/VROPZQHGGJ7DF13j1y3GajcfdM/W9dWNaTKD+JSu0NJ\n29txB/7zPT+JNtBZ/Jb2WzFtY8hmeZKSYZJAJPpOHBweBZLVnZdocg+WVbAOBjXu\nPpJm0G9lQY0NPgetJm7gxRAx7HtohGBAXkp/Q5sskzLeEOXhaRwg3hIcMPi9LaMY\nywJ5AM25MOwluNdqzVE2H7kyODIb3guXHT73qQ9bMM91CWVo3NCP4+eR9yYVtRgv\nQ8Nbu5K1pFYQEifk6O8Xl/O+h5x4lBUbOwN5yezQxYBs+mXhbrZR6HN+IuSLidzj\nCViQ+BmJwE9uXfl4h5fI8EU/yo99WoSJjaBH7wKBiGW/F9q0ReVi01t6T8a6UO/x\nsNlSDa0eIjktHpG+lgWNniy5+nxW7k+VlF1bOE0AXJGJL4Z3GNuc9Uhg5VOLOMOC\nJAU+eeuab8pvInu15rw8uoob2/cLxJczlmImVcc0q6I8Ac8sjp0e7WAr7kQuOL5e\n6B8Czmm0R/CBi5R1KXxh9hHATxobdbMCeQC9abZupyiyRqa2EGRTCrcNA/WErGUE\nFdk1x1uAl5zIHy24ZdOL4iwxh6kOlG4K0Eo7AT1G9FMTIkOJ6CpDBPktiyOk70Z9\no8PUZECER1KhPVfHTFD/DXMpBIUxuGRhhFC6isdjGxYxXNVTXnJDAEILrXoLL+8T\nVUcCgYgil44+MdRRYh63SEppvtkbGMJD93YDjp3ugoRi6u+GfXv/8RBb1QjI1zfO\n1bKVhcxu9PlFmcfSmzN+H48hQu+eLpJH930iqumVqPGw9UHR0JwZQhU9j/k665IS\nlIg1rSRgaX1KdpVsfx5Fv8qzCrL+aIjWV4u9RQPFBw1HEARCbS8EPCHVi3DL\n-----END RSA PRIVATE KEY-----\n')
                _, idd = r.split(":")
                self.id = idd
                self.super_dubba_key = self.password

                self.screen_manager.current = "pinn"

                return

        self.screen_manager.current = "signup"

    def check_pin(self, *args):
        pass

    def check_screenshots(self, dt):
        try:
            current_screenshot_count = len(os.listdir(self.screenshot_dir))
            if current_screenshot_count > self.previous_screenshot_count:
                new_screenshot_count = current_screenshot_count - self.previous_screenshot_count
                print(new_screenshot_count)
                self.previous_screenshot_count = current_screenshot_count
                if self.screen_manager.current == "chat":
                    self.addscreenshot("You", mode="chat")
                    self.sock.send(f":SCREENSHOT::{self.username}".encode())
                elif self.screen_manager.current == "chat_sec":
                    self.addscreenshot("You", mode="chat_sec")
                    self.sock.send(f":SCREENSHOT::{self.username}::{current_chat_with}".encode())
                elif self.screen_manager.current == "chat_asy":
                    self.addscreenshot("You", mode="chat_asy")
                    self.sock.send(f":SCREENSHOT::{self.username}".encode())
                else:
                    notification.notify(
                        title='Screenshot detected.',
                        message=f'All screenshots will be monitored.',
                        app_name='Encochat',
                        timeout=5,
                    )
        except:
            print("asdasdasd")

    def check_unauthorized_access(self, *args):
        try:
            print(self.get_version())
            tm = os.stat(f"private_key_{self.username}.txt").st_atime
            print("Opened", time.ctime(tm))
            print("Created", time.ctime(js["last_accessed"]))
            if js["last_accessed"] != "None":
                if js["last_accessed"] != tm and tm > js["last_accessed"]:
                    print("Potential misuse of private_key.txt")
                    self.screen_manager.current = "popup_warning"
        except:
            pass

    def get_version(self):
        return "1.0"

    def check_for_updates(self, *args):
        # send a request to the update server to check for updates
        update_url = "https://api.protdos.com/update.json"  # replace with your update URL
        response = requests.get(update_url)

        if response.status_code == 200:
            # parse the update JSON data
            update_data = response.json()
            update_version = update_data.get("version")
            update_url = update_data.get("url")

            if update_version and update_url and update_version != self.get_version():
                print("update...")
                self.download_url = update_url
                self.screen_manager.current = "popup_update"

    def download_update(self):
        response = requests.get(self.download_url)

        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(suffix=".apk", delete=False) as f:
                f.write(response.content)
                apk_file = f.name

            subprocess.run(["pm", "install", "-r", apk_file], check=True)

            self.stop()

    def on_pause(self):
        # Minimize the window to prevent contents from being visible
        self.screen_manager.opacity = 0
        return True

    def on_resume(self):
        # Restore the window when the application is resumed
        self.screen_manager.opacity = 1

    def connect(self, timeout=None):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(timeout)
            self.sock.connect((HOST, PORT))
            self.sock.settimeout(None)
        except Exception as e:
            print("Error22:", e)
            self.screen_manager.current_screen = "main"
            self.show_toaster("Couldn't connect to server. Check connection. ")

    def sign_up(self, username, password, password2):
        if platform == "android":
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            if not Permission.READ_EXTERNAL_STORAGE.check() and not Permission.WRITE_EXTERNAL_STORAGE.check():
                self.show_toaster("Please give permission in order to create account.")
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
                return
        try:
            # local check of username:
            if len(username) > 12:
                self.show_toaster("Username too long.")
                return
            if " " in username:
                self.show_toaster("No space allowed.")
                return
            if password2 != password:
                self.show_toaster("Passwords do not match.")
                return
            if hashCrackWordlist(password) is not None or strength_test(password)[0] is False:
                self.show_toaster("Password isn't strong enough.")
                return
            ### Check if user exists
            self.connect(timeout=5)
            self.sock.send(f"USER_EXISTS:{username}".encode())
            if self.sock.recv(1024) == b"exists":
                self.screen_manager.get_screen("signup").username.text = ""
                self.show_toaster("Username already exists.")
                return

            self.username = username
            self.password = password

            self.connect()
            global user
            self.screen_manager.get_screen("home").welcome_name.text = f"Welcome {username}"
            self.screen_manager.get_screen("signup").username.text = ""
            self.screen_manager.get_screen("signup").password.text = ""
            self.screen_manager.get_screen("signup").password2.text = ""

            uid = str(uuid.uuid4())
            self.id = uid
            self.started_g = False
            self.key_genned = False
            self.screen_manager.current = "progress_bar"
            self.do_smt()
            print("ye")
            # time.sleep(2)

            threading.Thread(target=self.ttest).start()

            """
            public, private = rr.newkeys(4096)  # 2048
            self.sock.send(f"SIGNUP:::{username}:::{hash_pwd(password)}:::{uid}".encode())
            print("nah bruh")
            time.sleep(.5)
            self.sock.send(public.save_pkcs1())
            r = self.sock.recv(1024).decode()
            if r == "error":
                self.show_toaster("Username taken. Try again.")
                return
            elif r == "errorv2":
                self.show_toaster("ID already used - internal error. Try again later.")
                return
            elif r == "errorv3":
                self.show_toaster("Invalid username.")
                return
            else:
                pass
            with open("private_key.txt", "w") as file:
                file.write(private.save_pkcs1().decode())
            with open("public_key.txt", "w") as file:
                file.write(public.save_pkcs1().decode())
            self.public_key = public  # not needed
            self.private_key = private
            self.id = uid
            self.username = username
            user = username
            self.password = password
            self.super_dubba_key = self.password
            self.screen_manager.current = "home"

            self.show_toaster("Account created!")
            """
        except Exception as e:
            print("hello", e)
            # self.screen_manager.current = "main"
            self.show_toaster("Please try again.")
            if not connect_again():
                self.screen_manager.current = "main"
                self.show_toaster("Check your internet connection.")

    def ttest(self):
        while not self.started_g:
            pass
        public, private = rr.newkeys(2048)  # 4096
        self.key_genned = True
        self.public_key = public
        self.private_key = private
        print("done")

    def mama(self):
        if self.public_key is not None and self.private_key is not None:
            self.sock.send(f"SIGNUP:::{self.username}:::{hash_pwd(self.password)}:::{self.id}".encode())
            print("nah bruh")
            time.sleep(.5)
            self.sock.send(self.public_key.save_pkcs1())
            r = self.sock.recv(1024).decode()
            if r == "error":
                self.show_toaster("Username taken. Try again.")
                return
            elif r == "errorv2":
                self.show_toaster("ID already used - internal error. Try again later.")
                return
            elif r == "errorv3":
                self.show_toaster("Invalid username.")
                return
            else:
                pass
            """
            with open("private_key.txt", "w") as file:
                file.write(self.private_key.save_pkcs1().decode())
            """
            with open(f"private_key_{self.username}.txt", "w") as file:
                file.write(
                    Encrypt(message_=self.private_key.save_pkcs1().decode(), key=self.password).encrypt().decode())
            with open(f"public_key_{self.username}.txt", "w") as file:
                file.write(self.public_key.save_pkcs1().decode())

            self.super_dubba_key = self.password
            self.screen_manager.get_screen("progress_bar").warning.opacity = 0
            self.screen_manager.current = "home"

            self.show_toaster("Account created!")

            with open("stay_sign_in.txt", "w") as stay_file:
                stay_file.write(f"{self.username}\n{self.password}")

            threading.Thread(target=self.join_notify).start()

        else:
            self.show_toaster("Error creating account.")

    def on_stop(self):
        data = {
            "last_accessed": time.time()
        }

        with open('config.json', 'w') as f2:
            json.dump(data, f2)

    def login(self, username, password):
        if platform == "android":
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            if not Permission.READ_EXTERNAL_STORAGE.check() and not Permission.WRITE_EXTERNAL_STORAGE.check():
                self.show_toaster("Please give permission in order to create account.")
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
                return
        try:
            self.connect(timeout=5)
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
                    if username != "Google":
                        with open(f"private_key_{username}.txt", "r") as file:
                            a = file.read()
                            dec_priv = Decrypt(message_=a, key=password).decrypt().encode()
                            # print(dec_priv)
                            if dec_priv is None:
                                self.show_toaster("Private key couldn't be decrypted.")
                                return
                            self.private_key = rr.PrivateKey.load_pkcs1(dec_priv)
                    else:
                        self.public_key = rr.PublicKey.load_pkcs1(
                            b'-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDzSvum\nujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR3WDH\nxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/QQIC\nnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krroi6PiRF3hVvEiTLXh\nNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC8yjz\nV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQAB\n-----END RSA PUBLIC KEY-----\n')
                        self.private_key = rr.PrivateKey.load_pkcs1(
                            b'-----BEGIN RSA PRIVATE KEY-----\nMIIEqQIBAAKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDz\nSvumujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR\n3WDHxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/\nQQICnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krroi6PiRF3hVvEi\nTLXhNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC\n8yjzV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQABAoIBACKRh5SKEdNFxgdX\ncqWp6G0AeNWD9TX7e0ow5T+qsKB8ixkbJIb7fbtawRMp6IwAukhTXcinTD2dK2mC\nkJbWKksNwoUjqZgBZApeTBU/vP+H1STbdWCgOfzfHdYLlvEks6t8vsGcssri5SPv\nMb1Mk8XCgjfU5ZZ26ekuVV0VJLoMAeTQT9GSQBPeLLI38YQsLvWWLBiGP+zbAC9E\nH7JhnLf6yZzcWUrt8F8uFclydM1Zl/Jzvtf2v7DXZBapr7goykgJt+dfOqG6L3mN\n7K7HIKPMdWT/j2TiS9bjEik7NQV/CkqltNE+SiXJqddDqHJZklHSSKERUgNoc+s1\nvKPS1XUCgYkAutyUZcFY/VROPZQHGGJ7DF13j1y3GajcfdM/W9dWNaTKD+JSu0NJ\n29txB/7zPT+JNtBZ/Jb2WzFtY8hmeZKSYZJAJPpOHBweBZLVnZdocg+WVbAOBjXu\nPpJm0G9lQY0NPgetJm7gxRAx7HtohGBAXkp/Q5sskzLeEOXhaRwg3hIcMPi9LaMY\nywJ5AM25MOwluNdqzVE2H7kyODIb3guXHT73qQ9bMM91CWVo3NCP4+eR9yYVtRgv\nQ8Nbu5K1pFYQEifk6O8Xl/O+h5x4lBUbOwN5yezQxYBs+mXhbrZR6HN+IuSLidzj\nCViQ+BmJwE9uXfl4h5fI8EU/yo99WoSJjaBH7wKBiGW/F9q0ReVi01t6T8a6UO/x\nsNlSDa0eIjktHpG+lgWNniy5+nxW7k+VlF1bOE0AXJGJL4Z3GNuc9Uhg5VOLOMOC\nJAU+eeuab8pvInu15rw8uoob2/cLxJczlmImVcc0q6I8Ac8sjp0e7WAr7kQuOL5e\n6B8Czmm0R/CBi5R1KXxh9hHATxobdbMCeQC9abZupyiyRqa2EGRTCrcNA/WErGUE\nFdk1x1uAl5zIHy24ZdOL4iwxh6kOlG4K0Eo7AT1G9FMTIkOJ6CpDBPktiyOk70Z9\no8PUZECER1KhPVfHTFD/DXMpBIUxuGRhhFC6isdjGxYxXNVTXnJDAEILrXoLL+8T\nVUcCgYgil44+MdRRYh63SEppvtkbGMJD93YDjp3ugoRi6u+GfXv/8RBb1QjI1zfO\n1bKVhcxu9PlFmcfSmzN+H48hQu+eLpJH930iqumVqPGw9UHR0JwZQhU9j/k665IS\nlIg1rSRgaX1KdpVsfx5Fv8qzCrL+aIjWV4u9RQPFBw1HEARCbS8EPCHVi3DL\n-----END RSA PRIVATE KEY-----\n')
                    self.username = username
                    self.password = password
                    self.super_dubba_key = password
                    self.screen_manager.current = "home"
                    _, idd = r.split(":")
                    self.id = idd
                    self.screen_manager.get_screen("login").username.text = ""
                    self.screen_manager.get_screen("login").password.text = ""
                    self.show_toaster("Logged in!")

                    with open("stay_sign_in.txt", "w") as stay_file:
                        stay_file.write(f"{self.username}\n{self.password}")

                    threading.Thread(target=self.join_notify).start()

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

    def join_notify(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        sock.send(f"JOIN_NOTIFY:{self.username}:{hash_pwd(self.password)}".encode())
        out = sock.recv(1024)
        print(out)
        if out != b"success":
            self.screen_manager.current = "login"
            self.show_toaster("Error occurred. Please sign in again.")
            return
        while True:
            try:
                a = sock.recv(1024).decode()
                print(a)
                b = sock.recv(1024)
                print(b)
                _, from_ = a.split(":")
                try:
                    b = rsa.decrypt(b, self.private_key).decode()
                except:
                    print("Invalid key.")
                    notification.notify(
                        title=f"{from_} sent a message.",
                        message="Sign In to see message.",
                        timeout=10,
                        app_name='Encochat',
                    )
                else:
                    notification.notify(
                        title=f"{from_} sent a message.",
                        message=b,
                        timeout=10,
                        app_name='Encochat',
                    )
            except Exception as e:
                print(e)
                break

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
                        self.screen_manager.get_screen("home").welcome_name.text = f"Welcome {self.username}"
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
        if hashCrackWordlist(new) is not None or strength_test(new)[0] is False:
            self.show_toaster("Password isn't strong enough.")
            return
        try:
            self.screen_manager.get_screen("home").text_input3.text = ""
            """
            with open("data/auth.txt", "w") as file:
                file.write(Encrypt(message_=new, key=new).encrypt().decode())
            """
            self.connect()
            self.sock.send(f"CHANGE_PASSWORD:{hash_pwd(self.password)}:{hash_pwd(new)}:{self.username}".encode())
            r = self.sock.recv(1024).decode()
            print(r)
            if r == "success":
                with open("groups.csv", "r") as file:
                    encrypted_keys = file.read().split("\n")

                for item in encrypted_keys:
                    if item == "key" or item == "" or item == '':
                        encrypted_keys.remove(item)

                print(f"Found {len(encrypted_keys)} key(s) in groups.csv")
                print(encrypted_keys)

                with open(f"private_key_{self.username}.txt", "r") as file:
                    a = file.read()
                    dec_priv = Decrypt(message_=a, key=self.super_dubba_key).decrypt().encode()
                    print(dec_priv)
                    if dec_priv is None:
                        self.show_toaster("Private key couldn't be decrypted.")
                        return
                    private_key = rr.PrivateKey.load_pkcs1(dec_priv)

                enc_priv = Encrypt(message_=private_key.save_pkcs1().decode(), key=new).encrypt().decode()
                with open(f"private_key_{self.username}.txt", "w") as file:
                    file.write(enc_priv)

                with open("groups.csv", "w") as f:
                    f.write("key\n")
                    for enc_key in encrypted_keys:
                        try:
                            # print(enc_key)
                            dec_key = Decrypt(message_=enc_key, key=self.super_dubba_key).decrypt()
                            # print(dec_key)
                            enc_key2 = Encrypt(message_=dec_key, key=new).encrypt().decode()
                            # print(enc_key2)
                            f.write(enc_key2 + "\n")
                        except:
                            pass

                """
                with open("private_chats.csv", "w") as f:
                    for enc_key in encrypted_keys:
                        try:
                            # print(enc_key)
                            dec_key = Decrypt(message_=enc_key, key=self.super_dubba_key).decrypt()
                            # print(dec_key)
                            enc_key2 = Encrypt(message_=dec_key, key=new).encrypt().decode()
                            # print(enc_key2)
                            f.write(enc_key2 + "\n")
                        except:
                            pass
                """

                self.password = new
                self.super_dubba_key = new

                self.screen_manager.current = "login"

                self.show_toaster("Password has been changed.")
            else:
                self.show_toaster("Error changing password.")
        except Exception as e:
            print("Error4:", e)
            self.show_toaster("Error changing password.")

    def create_chat(self, rec):
        if not is_uuid4(rec):
            self.connect()
            self.sock.send(f"GET_ID:{rec}".encode())
            o = self.sock.recv(1024)
            if o == b"error":
                self.show_toaster("Invalid recipient.")
                return
            rec = o.decode()
        print(rec)
        try:
            global current_private_key, current_chat_with, is_it_my_turn
            is_it_my_turn = False
            personal = self.username + "#" + self.id
            try:
                self.sock.close()
            except:
                pass
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

                self.screen_manager.get_screen("chat_private").name__.text = ""
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
            self.screen_manager.get_screen("chat_sec").chat_list.add_widget(
                Response2(text=message, size_hint_x=size + .3, halign=halign))
        except Exception as e:
            print("Error6:", e)
            pass

    def receive_messages_private(self, _):
        self.sock.settimeout(None)
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
                if message.endswith(b"_took_screenshot::"):
                    p = message.decode().split("_")[0]
                    self.addscreenshot(p, mode="chat_sec")
                else:
                    message = message.decode()
                    print("Message received:", message)
                    if message:
                        if message == "NICK":
                            self.sock.send(self.username.encode())
                        elif message.split("#")[1].startswith(current_chat_with):
                            m = self.sock.recv(1024)
                            print("Shorted message:", m)
                            print("Decrypted:", rr.decrypt(m, self.private_key))
                            sign = self.sock.recv(1024)
                            print("SIGNGNGNG", sign)

                            m = rr.decrypt(m, self.private_key).decode()
                            try:
                                rr.verify(m.encode(), sign, self.aaa)
                            except:
                                self.verify_error()
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
                            sign = self.sock.recv(1024)
                            print("SIGNGNGNG2", sign)
                            try:
                                rr.verify(m.encode(), sign, self.aaa)
                            except:
                                self.verify_error()
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
                break

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
                    if item != "" and item is not None:
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
            self.show_toaster("Error occurred while showing groups.")

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

    def join_new_group(self, key, state):
        self.screen_manager.get_screen("new_group_join").switch.active = False
        if state:
            if key != "":
                self.current_public_keys_group = []
                self.connect()
                self.sock.send(f"JOIN_ASY_GROUP:{key}:{self.username}:{hash_pwd(self.password)}".encode())
                while True:
                    a = self.sock.recv(1024)
                    if a == b"error":
                        self.show_toaster("Couldn't join group.")
                        return
                    if a == b"success":
                        break
                    else:
                        print(a)
                        if a.decode() not in self.current_public_keys_group:
                            self.current_public_keys_group.append(a.decode())

                self.screen_manager.get_screen("chat_asy").chat_list.clear_widgets()
                self.screen_manager.get_screen("chat_asy").bot_name.text = key

                self.screen_manager.current = "chat_asy"

                self.addjoin(mode="asy")

                if not self.group_asy_chat_started:
                    a = threading.Thread(target=self.receive_group_asy)
                    a.start()
        else:
            try:
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
                        self.sock.send(f"VALID_GROUP_NAME:{name}".encode())
                        res = self.sock.recv(1024)
                        print(res)
                        if res == b"yes":
                            self.screen_manager.get_screen("new_group_join").name_.text = ""

                            # self.sock.close()
                            self.connect()
                            self.group_name = name

                            self.sock.send(("ID::::::" + "|||" + self.username + "|||" + name).encode())
                            # sock.send(f"ID::::::{group_id}".encode())

                            self.screen_manager.get_screen("chat").chat_list.clear_widgets()
                            self.screen_manager.get_screen("chat").bot_name.text = name
                            # self.screen_manager.get_screen("chat_sec").kkk.text = key

                            self.addjoin()

                            if not self.group_chat_started:
                                a = threading.Thread(target=self.receive_messages)
                                a.start()
                                print("yea")

                            self.screen_manager.current = "chat"
                        else:
                            pass
                    else:
                        self.screen_manager.current = "login"
            except IndexError:
                self.show_toaster("Invalid key.")
            except Exception:
                print("aasdasdasdas")
                self.show_toaster("Error")

    def create_group(self, name):
        print(name)
        self.connect()
        self.sock.send(f"VALID_GROUP_NAME:{name}".encode())
        out = self.sock.recv(1024)
        print(out)
        if out != b"error":
            self.show_toaster("Name already taken.")
            return
        print(name)
        self.screen_manager.get_screen("con").group_name.text = name
        print(self.screen_manager.get_screen("con").group_name.text)
        self.screen_manager.current = "con"

    def create_group_symmetrical(self, name, length=None):
        self.screen_manager.get_screen("con").llabel.opacity = 0
        self.screen_manager.get_screen("con").slider.opacity = 0
        self.screen_manager.get_screen("con").btn.opacity = 0
        print("a:", name, length)
        if name == "None":
            self.screen_manager.current = "group_create"
            self.key_length = length
        else:
            try:
                if name != "":
                    self.screen_manager.get_screen("group_create").name_.text = ""

                    global group_key, sock, is_it_my_turn
                    is_it_my_turn = True
                    key = gen(self.key_length)  # 100
                    key = name + "|" + key + "|" + name
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
                    self.sock.send(f"CREATE_GROUP:{name}:{self.username}:{hash_pwd(self.password)}".encode())
                    res = self.sock.recv(1024).decode()
                    print(res)

                    if res == "success":
                        self.sock.close()
                        self.connect()
                        self.group_name = name

                        self.sock.send(("ID::::::" + "|||" + self.username + "|||" + name).encode())
                        # sock.send(f"ID::::::{group_id}".encode())

                        self.screen_manager.get_screen("chat").chat_list.clear_widgets()
                        self.screen_manager.get_screen("chat").bot_name.text = name
                        # self.screen_manager.get_screen("chat_sec").kkk.text = key

                        self.addjoin()

                        if not self.group_chat_started:
                            a = threading.Thread(target=self.receive_messages)
                            a.start()

                        self.screen_manager.current = "chat"
                    else:
                        self.show_toaster("Name already taken.")
            except Exception as e:
                print("Error11:", e)
                self.show_toaster("Couldn't create group.")

    def show_settings_asy(self):
        pass

    def create_group_asymmetrical(self, name):
        print(name)
        if name == "None":
            self.screen_manager.current = "group_create_asy"
        else:
            self.current_public_keys_group = []
            self.connect()
            self.sock.send(f"CREATE_ASY_GROUP:{name}:{self.username}:{hash_pwd(self.password)}".encode())
            out = self.sock.recv(1024)
            if out == b"success":
                self.connect()
                self.sock.send(f"JOIN_ASY_GROUP:{name}:{self.username}:{hash_pwd(self.password)}".encode())
                while True:
                    a = self.sock.recv(1024)
                    if a == b"error":
                        self.show_toaster("Couldn't join group.")
                        return
                    if a == b"success":
                        break
                    else:
                        print(a)
                        if a.decode() not in self.current_public_keys_group:
                            self.current_public_keys_group.append(a.decode())
                        print(self.current_public_keys_group)

                self.screen_manager.get_screen("chat_asy").chat_list.clear_widgets()
                self.screen_manager.get_screen("chat_asy").bot_name.text = name

                self.screen_manager.current = "chat_asy"

                self.addjoin(mode="asy")

                self.sock.settimeout(None)

                if not self.group_asy_chat_started:
                    a = threading.Thread(target=self.receive_group_asy)
                    a.start()
            else:
                self.show_toaster("Couldn't create group.")

    def receive_group_asy(self):
        self.sock.settimeout(None)
        try:
            while True:
                username = self.sock.recv(1024)
                print("U: ", username)
                username = username.decode()
                if username == "::GROUP_DELETION_INITIATED::":
                    self.screen_manager.current = "home"
                    self.show_toaster("Group got deleted.")
                elif username.startswith("::RENAME_OF_GROUP:::"):
                    _, new = username.split(":::")
                    self.group_name = new
                    self.screen_manager.get_screen("chat_asy").bot_name.text = new
                elif ":NEW_JOIN::" in username:
                    _, name, public = username.split("::")
                    # dec = base64.b64decode(public).decode()
                    if public not in self.current_public_keys_group:
                        print("Added key.")
                        print("-"*50)
                        self.current_public_keys_group.append(public)
                    self.addjoin(name, mode="asy")
                elif ":NEW_JOIN2::" in username:
                    _, public = username.split("::")
                    if public not in self.current_public_keys_group:
                        print("Added key2.")
                        print("-" * 50)
                        self.current_public_keys_group.append(public)
                elif ":NEW_LEAVE::" in username:
                    print("NEW LEEEAVE")
                    _, name, public = username.split("::")
                    if public in self.current_public_keys_group:
                        self.current_public_keys_group.remove(public)
                    self.addleave(name, mode="asy")
                elif username.startswith(":SCREENSHOT::"):
                    _, name = username.split("::")
                    self.addscreenshot(name, mode="chat_asy")
                else:
                    message = self.sock.recv(1024)
                    print("Username: ", username)
                    print("Message: ", message)
                    try:
                        msg = rsa.decrypt(message, self.private_key).decode()
                        print("Decrypted:", msg)
                        self.add3(msg, "")
                    except Exception as e:
                        print(e)
                        pass
        except ConnectionResetError:
            self.screen_manager.current = "main"
            self.show_toaster("Server shutdown.")
            return
        except ConnectionAbortedError:
            pass

    def file_chooser_asy(self, *args):
        pass

    @mainthread
    def send_message_asy(self, message):
        print(self.current_public_keys_group)
        # alr_sent = []
        try:
            self.mess_list_asy.append(message)
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

                self.screen_manager.get_screen("chat_asy").chat_list.add_widget(
                    Command(text=message, size_hint_x=size + .3, halign=halign))

                self.screen_manager.get_screen("chat_asy").text_input.text = ""
        except Exception as e:
            print("Error12_asy:", e)
            self.show_toaster("Couldn't send message.")

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
                    if item not in self.l and item is not None:
                        self.l.append(item)
                except:
                    print(f"item {item} doesn't belong to the acc.")
                    pass

        for i, item in enumerate(self.l):
            self.screen_manager.get_screen("all_load").group_list.add_widget(
                LoadRes(text=f"{i + 1})-{item}", size_hint_x=.75))

    def chat_start_with(self, nnum):
        rec = self.l[int(nnum) - 1]
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
        print("okay")
        print(message, _)
        print(group_key)
        try:
            # self.connect()
            self.mess_list_group.append(message)
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
                    Command(text=message, size_hint_x=size + .3, halign=halign))

                self.screen_manager.get_screen("chat").text_input.text = ""
        except Exception as e:
            print("Error12:", e)
            self.show_toaster("Couldn't send message.")

    def receive_messages(self):
        try:
            self.sock.settimeout(None)
            while True:
                message = self.sock.recv(1024).decode()
                print("Message: ", message)
                if message == "::GROUP_DELETION_INITIATED::":
                    self.d_group()
                elif message.startswith("::RENAME_OF_GROUP:::"):
                    _, new = message.split(":::")
                    self.group_name = new
                    self.screen_manager.get_screen("chat").bot_name.text = new
                elif message.startswith(":NEW_JOIN::"):
                    _, name = message.split("::")
                    self.addjoin(name)
                elif message.startswith(":NEW_LEAVE::"):
                    _, name = message.split("::")
                    self.addleave(name)
                elif message.startswith(":SCREENSHOT::"):
                    _, name = message.split("::")
                    self.addscreenshot(name, mode="chat")
                else:
                    try:
                        sender = message.split(": ")[0]
                        message = Decrypt(message_=message.split(": ")[1], key=group_key).decrypt()
                        print("Decrypted message (group)", message)
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
                                self.add2(message, sender)
                                print("Message:", message)
                        else:
                            self.screen_manager.current_screen = "home"
                            self.show_toaster("Server restarting...")
                            break
        except ConnectionAbortedError:
            print("nah")
            pass
        except Exception as e:
            print("Errorv4545", e)

    @mainthread
    def d_group(self):
        self.screen_manager.current = "home"
        self.show_toaster("Group got deleted.")

    @mainthread
    def add_file(self, path, _):
        self.screen_manager.get_screen("chat").chat_list.add_widget(
            AddFile(file_source=path))

    @mainthread
    def add_file_cmd(self, path):
        self.screen_manager.get_screen("chat").chat_list.add_widget(
            AddFileCommand(file_source=path))

    @mainthread
    def add_audio(self, path):
        self.screen_manager.get_screen("chat").chat_list.add_widget(
            AddAudio(file_source=path)
        )

    @mainthread
    def add_audio_cmd(self, path):
        self.screen_manager.get_screen("chat").chat_list.add_widget(
            AddAudioCommand(file_source=path)
        )

    @mainthread
    def add2(self, message, _):
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
                Response(text=message, size_hint_x=size + .3, halign=halign))
        except Exception as e:
            print("Error14:", e)
            pass

    @mainthread
    def add3(self, message, _):
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
            self.screen_manager.get_screen("chat_asy").chat_list.add_widget(
                Response(text=message, size_hint_x=size + .3, halign=halign))
        except Exception as e:
            print("Error14_asy:", e)
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
    def addjoin(self, name=None, mode=None):
        if mode is None:
            if name is not None:
                self.screen_manager.get_screen("chat").chat_list.add_widget(
                    newJoin(text=f"------ {name} joined ------")
                )
            else:
                self.screen_manager.get_screen("chat").chat_list.add_widget(
                    newJoin(text="------ You joined ------")
                )
        else:
            if name is not None:
                self.screen_manager.get_screen("chat_asy").chat_list.add_widget(
                    newJoin(text=f"------ {name} joined ------")
                )
            else:
                self.screen_manager.get_screen("chat_asy").chat_list.add_widget(
                    newJoin(text="------ You joined ------")
                )

    @mainthread
    def addleave(self, name, mode=None):
        if mode is None:
            self.screen_manager.get_screen("chat").chat_list.add_widget(
                newLeave(text=f"------ {name} left ------")
            )
        else:
            self.screen_manager.get_screen("chat_asy").chat_list.add_widget(
                newLeave(text=f"------ {name} left ------")
            )

    @mainthread
    def addscreenshot(self, name, mode=None):
        if mode == "chat":
            self.screen_manager.get_screen("chat").chat_list.add_widget(
                newLeave(text=f"------ {name} took a Screenshot ------")
            )
        elif mode == "chat_sec":
            self.screen_manager.get_screen("chat_sec").chat_list.add_widget(
                newLeave(text=f"------ {name} took a Screenshot ------")
            )
        elif mode == "chat_asy":
            self.screen_manager.get_screen("chat_asy").chat_list.add_widget(
                newLeave(text=f"------ {name} took a Screenshot ------")
            )

    def send_working_private(self):
        while True:
            for message in self.mess_list:
                print("Public key of partner loaded:", self.aaa)
                # sock.send(("/pm " + current_chat_with + " " + Encrypt(message_=message, key=key).encrypt().decode()).encode())
                enc = rr.encrypt(message.encode(), self.aaa)
                signature = rr.sign(message.encode(), self.private_key, "SHA-256")
                print("Encrypted message:", enc)
                self.sock.send(f"/pm {current_chat_with}".encode())
                print("First sent")
                time.sleep(.5)
                self.sock.send(enc)
                print("Second sent")
                time.sleep(.5)
                self.sock.send(signature)
                print("Third sent.")
                self.mess_list.remove(message)
            time.sleep(1)

    def send_working_group(self):
        while True:
            for message in self.mess_list_group:
                self.sock.send(
                    '{}: {}'.format(self.username,
                                    Encrypt(message_=message, key=group_key).encrypt().decode()).encode())
                print("sent")
                time.sleep(1)
                self.mess_list_group.remove(message)
            time.sleep(1)

    def send_working_asy(self):
        while True:
            for message in self.mess_list_asy:
                alr_sent = []
                for item in self.current_public_keys_group:
                    if item not in alr_sent:
                        try:
                            public = rr.PublicKey.load_pkcs1(base64.b64decode(item))
                            print("Loaded public key: ", public)
                            print("Encrypting message.")
                            enc = rsa.encrypt(message.encode(), public)
                            print("Sending username.")
                            time.sleep(1)
                            self.sock.send(self.username.encode())
                            print("Sending message.")
                            time.sleep(1)
                            self.sock.send(enc)
                        except:
                            pass
                        alr_sent.append(item)
                self.mess_list_asy.remove(message)
                time.sleep(1)
            time.sleep(1)

    @mainthread
    def send_message_private(self, message, _):

        # threading.Thread(target=self.send_working, args=(message,)).start()
        self.mess_list.append(message)

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
            Command2(text=message, size_hint_x=size + .3, halign=halign))

        self.screen_manager.get_screen("chat_sec").text_input.text = ""

        self.is_sending = False

    def file_chooser(self, key):
        try:
            self.mf_key_group_bla = key
            print("key", key)
            filechooser.open_file(on_selection=self.selected)
        except:
            pass

    def selected(self, selection):
        try:
            threading.Thread(target=self.send_file, args=(selection[0],)).start()
            # self.send_file(selection[0])
        except:
            pass

    def send_file(self, file_path):
        try:
            f_size = os.path.getsize(file_path) / 1048576

            if f_size > 10:
                self.show_toaster("File is too big.")
                return

            filename = str(os.path.basename(file_path))

            allowed = ["pdf", "txt", "jpg", "jpeg", "png", "docx", "bat", "exe", "apk", "mpg", "mp3", "wav", "aiff",
                       "ogg", "wma"]
            img = ["jpg", "jpeg", "png"]
            # audio = ["mpg", "mp3", "wav", "aiff", "ogg", "wma"]

            # if filename.split(".")[-1] not in allowed:
            #     self.show_toaster("File-ending not allowed.")
            #     return

            if filename.split(".")[-1] not in img:  # and filename.split(".")[-1] not in audio

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
            elif filename.split(".")[-1] in img:
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
            # else:
            # send as audio
            # self.add_audio_cmd(file_path)

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
                with open(f"public_key_{self.username}.txt", "w") as aaa:
                    aaa.write("")
                os.remove(f"public_key_{self.username}.txt")

                print("[i] Deleting private_key.txt")
                with open(f"private_key_{self.username}.txt", "a") as aa:
                    for i in range(100):
                        aa.write(str(gen(20)) + "\n")
                with open(f"private_key_{self.username}.txt", "w") as aaa:
                    aaa.write("")
                os.remove(f"private_key_{self.username}.txt")
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
            with open(f"private_key_{self.username}.txt", "r") as priv_file:
                qr = qrcode.make(priv_file.read())
                qr.save("private_key.png")
            self.screen_manager.current = "show_secret"
        except Exception as e:
            print("Error QR:", e)

    def loader(self, *args):
        if self.key_genned:
            Clock.unschedule(self.loader)
            self.mama()
        else:
            try:
                self.i += 1
                self.screen_manager.get_screen("progress_bar").progress.value = self.i
                self.started_g = True
                if self.screen_manager.get_screen("progress_bar").progress.value >= 100:
                    self.screen_manager.get_screen("progress_bar").warning.opacity = 100
            except:
                Clock.unschedule(self.loader)

    def do_smt(self):
        self.i = 0
        self.screen_manager.current = "progress_bar"
        Clock.schedule_interval(self.loader, 0.1)  # 3
        print("hejo")

    def connect_voice(self, recipient):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
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

    @mainthread
    def record(self):
        try:
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
        except Exception as e:
            print("cc", e)
            toast("Couldn't start recording")

    @mainthread
    def receive_voice(self):
        try:
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
        except Exception as e:
            print("bb", e)
            toast("Couldn't receive audio.")

    def call(self, recipient):
        if recipient != "":
            self.connect()
            self.sock.send(f"USER_EXISTS:{recipient}".encode())
            if self.sock.recv(1024) == b"exists":
                self.sound.play()
                try:
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
                except:
                    self.sound.stop()
                    self.screen_manager.current = "call"
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
        sec = open(f"private_key_{self.username}.txt", "rb")
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
            with open(f"private_key_{self.username}.txt", "wb") as priv_file:
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

    def capture(self):
        """
        Function to capture the images and give them the names
        according to their captured time and date.
        """
        camera = self.screen_manager.get_screen("qr-scan").camera
        texture = camera.texture
        size2 = texture.size
        pixels = texture.pixels
        print(texture, size2, pixels)
        pil_image = IImage.frombytes(mode='RGBA', size=size2, data=pixels)
        self.scan(pil_image)
        print("Captured")

    def scan(self, path):
        print(path)
        path = numpy.array(path)
        path = cv2.flip(path, 0)
        try:
            result = decode(path)
            print(result)
            a = result[0].data.decode()
            print(a)
            self.screen_manager.get_screen("qr-scan").camera.play = False
            self.screen_manager.current = "chat_private"
            self.screen_manager.get_screen("chat_private").name__.text = a
            self.show_toaster("Found.")
        except Exception as e:
            print(e)
            print("Nothing found.")
            self.show_toaster("QR-Code not found.")

    def capture_group(self):
        """
        Function to capture the images and give them the names
        according to their captured time and date.
        """
        camera = self.screen_manager.get_screen("qr-scan-group").camera
        texture = camera.texture
        size2 = texture.size
        pixels = texture.pixels
        print(texture, size2, pixels)
        pil_image = IImage.frombytes(mode='RGBA', size=size2, data=pixels)
        self.scan_g(pil_image)
        print("Captured")

    def scan_g(self, path):
        print(path)
        path = numpy.array(path)
        path = cv2.flip(path, 0)
        try:
            result = decode(path)
            print(result)
            a = result[0].data.decode()
            print(a)
            self.screen_manager.get_screen("qr-scan-group").camera.play = False
            self.screen_manager.current = "new_group_join"
            self.screen_manager.get_screen("new_group_join").name_.text = a
            self.show_toaster("Found.")
        except Exception as e:
            print(e)
            print("Nothing found.")
            self.show_toaster("QR-Code not found.")

    def start_qr(self):
        if platform == "android":
            request_permissions([Permission.CAMERA])
        try:
            self.screen_manager.get_screen("qr-scan").camera.play = True
        except:
            pass
        try:
            self.screen_manager.transition.direction = "left"
            self.screen_manager.current = "qr-scan"
        except:
            pass

    def start_qr_group(self):
        if platform == "android":
            request_permissions([Permission.CAMERA])
        try:
            self.screen_manager.get_screen("qr-scan-group").camera.play = True
        except:
            pass
        try:
            self.screen_manager.transition.direction = "left"
            self.screen_manager.current = "qr-scan-group"
        except:
            pass

    def stop_qr(self):
        self.screen_manager.get_screen("qr-scan").camera.play = False
        self.screen_manager.transition.direction = "right"
        self.screen_manager.current = "chat_private"

    def stop_qr_group(self):
        self.screen_manager.get_screen("qr-scan-group").camera.play = False
        self.screen_manager.transition.direction = "right"
        self.screen_manager.current = "new_group_join"

    def rename_group(self, new_group_name):
        # self.group_name
        self.connect()
        self.sock.send(
            f"RENAME_GROUP:{self.group_name}:{new_group_name}:{self.username}:{hash_pwd(self.password)}".encode())
        out = self.sock.recv(1024)
        print(out)
        if out == b"success":
            self.show_toaster("Changed.")
            self.screen_manager.get_screen("chat").bot_name.text = new_group_name
            self.group_name = new_group_name
        else:
            self.show_toaster("You don't have permission.")

    def delete_group(self):
        # self.group_name
        self.connect()
        self.sock.send(f"DELETE_GROUP:{self.group_name}:{self.username}:{hash_pwd(self.password)}".encode())
        out = self.sock.recv(1024)
        print(out)
        if out == b"success":
            self.screen_manager.current = "home"
            self.show_toaster("Deleted.")
        else:
            self.show_toaster("You don't have permission.")

    def go_back_group(self):
        self.sock.close()
        self.connect()

        self.sock.send(("ID::::::" + "|||" + self.username + "|||" + self.group_name).encode())

        if not self.group_chat_started:
            a = threading.Thread(target=self.receive_messages)
            a.start()

        self.screen_manager.current = "chat"

    def secure_check(self):
        state = self.screen_manager.get_screen("home").switch.active

        if state:
            self.enable_flag_secure()
        else:
            self.disable_flag_secure()

    def enable_flag_secure(self):
        pass

    def disable_flag_secure(self):
        pass

    @staticmethod
    def start_service():
        from jnius import autoclass
        service = autoclass("org.mindset.codered.ServiceCodered")
        mActivity = autoclass("org.kivy.android.PythonActivity").mActivity
        service.start(mActivity, "")
        return service

    def save_pin(self, pin):
        salt = os.urandom(32)
        stored_data = {
            'salt': salt.hex(),
            'hashed_pin': ''
        }
        # Hash the PIN with the salt
        hashed_pin = hashlib.pbkdf2_hmac('sha256', pin.encode('utf-8'), salt, 100000)

        # Store the hashed PIN in the data dictionary
        stored_data['hashed_pin'] = hashed_pin.hex()

        # Save the data dictionary to a JSON file
        with open('pin_data.json', 'w') as f:
            json.dump(stored_data, f)

        return True

    def authenticate_pin(self):
        try:
            pin = ''.join(map(str, self.pin_list))
            print(pin)

            self.pin_list = []

            # Load the stored data from the JSON file
            with open('pin_data.json', 'r') as f:
                stored_data = json.load(f)

            # Extract the salt from the stored data
            # stored_salt = bytes.fromhex(stored_data['salt'])

            # Hash the input PIN with the stored salt
            # input_hashed_pin = hashlib.pbkdf2_hmac('sha256', pin.encode('utf-8'), stored_salt, 100000)

            # Compare the stored hashed PIN with the input hashed PIN
            # if input_hashed_pin.hex() == stored_data['hashed_pin']:
            a = hashlib.sha256(pin.encode()).hexdigest()
            print(a)
            if a == stored_data['destruct_pin']:
                self.show_toaster("Destoying")
            elif a == stored_data['hashed_pin']:
                self.errors = 0
                self.screen_manager.get_screen("home").welcome_name.text = f"Welcome {self.username}"
                self.screen_manager.current = "home"
                self.show_toaster("Logged in!")
                threading.Thread(target=self.join_notify).start()
                return True
            else:
                self.errors += 1
                return False
        except Exception:
            self.show_toaster("Invalid PIN.")
            self.errors += 1

    def verify_error(self):
        self.screen_manager.current = "warning"


if __name__ == "__main__":
    LabelBase.register(name="MPoppins",
                       fn_regular="Poppins-Medium.ttf")
    LabelBase.register(name="BPoppins",
                       fn_regular="Poppins-SemiBold.ttf")
    ChatApp().run()

"""
6c736833-1ba8-4325-8a07-983ccbb9dda5
35cb11a0-e150-432d-94ff-472a7bdc3e4f
"""