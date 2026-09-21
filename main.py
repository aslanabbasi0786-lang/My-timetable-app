from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.label import Label

import json
import os
import hashlib


class TimetableApp(App):

    def build(self):

        self.schedules = []
        self.load_schedules()

        self.pin_file = os.path.join(
            self.user_data_dir,
            "pin.txt"
        )

        # अगर PIN पहले से बना है
        if os.path.exists(self.pin_file):
            return self.lock_screen()

        # पहली बार PIN बनाना
        return self.create_pin_screen()

    # ---------------- PIN CREATE ----------------

    def create_pin_screen(self):

        layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=15
        )

        title = Label(
            text="CREATE YOUR PIN",
            font_size=28
        )

        pin = TextInput(
            hint_text="Enter 4 digit PIN",
            password=True,
            input_filter="int",
            multiline=False
        )

        confirm = TextInput(
            hint_text="Confirm PIN",
            password=True,
            input_filter="int",
            multiline=False
        )

        button = Button(
            text="SAVE PIN",
            size_hint_y=None,
            height=60
        )

        message = Label(
            text="",
            font_size=18
        )

        layout.add_widget(title)
        layout.add_widget(pin)
        layout.add_widget(confirm)
        layout.add_widget(button)
        layout.add_widget(message)

        button.bind(
            on_press=lambda x: self.save_pin(
                pin.text,
                confirm.text,
                message
            )
        )

        return layout

    def save_pin(self, pin, confirm, message):

        if len(pin) != 4:
            message.text = "PIN must be 4 digits"
            return

        if pin != confirm:
            message.text = "PINs do not match"
            return

        hashed_pin = hashlib.sha256(
            pin.encode()
        ).hexdigest()

        with open(self.pin_file, "w") as file:
            file.write(hashed_pin)

        self.root.clear_widgets()
        self.root.add_widget(
            self.timetable_screen()
        )

    # ---------------- LOCK SCREEN ----------------

    def lock_screen(self):

        layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=20
        )

        title = Label(
            text="🔒 TIMETABLE LOCKED",
            font_size=28
        )

        pin = TextInput(
            hint_text="Enter PIN",
            password=True,
            input_filter="int",
            multiline=False
        )

        button = Button(
            text="UNLOCK",
            size_hint_y=None,
            height=60
        )

        message = Label(
            text="",
            font_size=18
        )

        layout.add_widget(title)
        layout.add_widget(pin)
        layout.add_widget(button)
        layout.add_widget(message)

        button.bind(
            on_press=lambda x: self.check_pin(
                pin.text,
                message
            )
        )

        return layout

    def check_pin(self, pin, message):

        if len(pin) != 4:
            message.text = "Enter 4 digit PIN"
            return

        hashed_pin = hashlib.sha256(
            pin.encode()
        ).hexdigest()

        try:
            with open(self.pin_file, "r") as file:
                saved_pin = file.read()

            if hashed_pin == saved_pin:

                self.root.clear_widgets()
                self.root.add_widget(
                    self.timetable_screen()
                )

            else:
                message.text = "Wrong PIN"

        except:
            message.text = "PIN error"

    # ---------------- TIMETABLE ----------------

    def timetable_screen(self):

        self.main_layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        add_button = Button(
            text="ADD SCHEDULE",
            font_size=25,
            size_hint_y=None,
            height=60
        )

        add_button.bind(
            on_press=self.add_schedule
        )

        self.main_layout.add_widget(
            add_button
        )

        self.show_schedules()

        return self.main_layout

    # ---------------- ADD SCHEDULE ----------------

    def add_schedule(self, instance):

        box = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        subject = TextInput(
            hint_text="Subject / Work",
            multiline=False
        )

        time = TextInput(
            hint_text="Time (e.g. 8:00-9:00)",
            multiline=False
        )

        save_button = Button(
            text="SAVE",
            size_hint_y=None,
            height=50
        )

        box.add_widget(subject)
        box.add_widget(time)
        box.add_widget(save_button)

        popup = Popup(
            title="Add Schedule",
            content=box,
            size_hint=(0.9, 0.6)
        )

        save_button.bind(
            on_press=lambda x: self.save_schedule(
                subject.text,
                time.text,
                popup
            )
        )

        popup.open()

    def save_schedule(
        self,
        subject,
        time,
        popup
    ):

        if subject.strip() == "" or time.strip() == "":
            return

        self.schedules.append({
            "subject": subject,
            "time": time
        })

        self.save_data()

        popup.dismiss()

        self.show_schedules()

    # ---------------- SHOW SCHEDULES ----------------

    def show_schedules(self):

        while len(self.main_layout.children) > 1:

            self.main_layout.remove_widget(
                self.main_layout.children[0]
            )

        for item in reversed(self.schedules):

            schedule = Label(
                text=(
                    item["time"]
                    + "  -  "
                    + item["subject"]
                ),
                font_size=20,
                size_hint_y=None,
                height=50
            )

            self.main_layout.add_widget(
                schedule
            )

    # ---------------- SAVE DATA ----------------

    def save_data(self):

        path = os.path.join(
            self.user_data_dir,
            "timetable.json"
        )

        with open(path, "w") as file:
            json.dump(
                self.schedules,
                file
            )

    # ---------------- LOAD DATA ----------------

    def load_schedules(self):

        path = os.path.join(
            self.user_data_dir,
            "timetable.json"
        )

        if os.path.exists(path):

            try:

                with open(path, "r") as file:
                    self.schedules = json.load(file)

            except:

                self.schedules = []


TimetableApp().run()