from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from datetime import datetime, timedelta
from kivy.clock import Clock


class Language:
    RU = {
        "main_title": "Главное меню",
        "days_until": "Дней до даты",
        "days_in_love": "Дней в отношениях",
        "select_date": "Выберите дату",
        "open_calendar": "Открыть календарь",
        "back": "Назад",
        "days_left": "Осталось: {} дней, {} часов, {} минут, {} секунд",
        "select_love_date": "Выберите дату начала отношений",
        "days_together": "Вместе: {} дней, {} часов, {} минут, {} секунд",
        "language": "Язык"
    }

    EN = {
        "main_title": "Main Menu",
        "days_until": "Days until date",
        "days_in_love": "Days in relationship",
        "select_date": "Select date",
        "open_calendar": "Open calendar",
        "back": "Back",
        "days_left": "Left: {} days, {} hours, {} minutes, {} seconds",
        "select_love_date": "Select relationship start date",
        "days_together": "Together: {} days, {} hours, {} minutes, {} seconds",
        "language": "Language"
    }


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.build_ui()

    def build_ui(self):
        self.layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        # Language switcher
        settings_layout = MDBoxLayout(size_hint=(1, None), height=50, spacing=10)
        self.lang_btn = MDFlatButton(
            text=self.app.get_translation("language"),
            theme_text_color="Custom",
            text_color=self.app.theme_cls.primary_color
        )
        self.lang_btn.bind(on_release=self.show_lang_menu)
        settings_layout.add_widget(self.lang_btn)

        self.layout.add_widget(settings_layout)

        # Main buttons
        self.btn_date = MDRaisedButton(
            text=self.app.get_translation("days_until"),
            size_hint=(1, None),
            height=50
        )
        self.btn_date.bind(on_release=self.switch_to_date_counter)

        self.btn_love = MDRaisedButton(
            text=self.app.get_translation("days_in_love"),
            size_hint=(1, None),
            height=50
        )
        self.btn_love.bind(on_release=self.switch_to_relationship_counter)

        self.layout.add_widget(self.btn_date)
        self.layout.add_widget(self.btn_love)
        self.add_widget(self.layout)

    def show_lang_menu(self, instance):
        menu_items = [
            {
                "text": "Русский",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.app.switch_language("RU")
            },
            {
                "text": "English",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.app.switch_language("EN")
            }
        ]
        self.menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4
        )
        self.menu.open()

    def switch_to_date_counter(self, *args):
        self.manager.current = 'date_counter'

    def switch_to_relationship_counter(self, *args):
        self.manager.current = 'relationship_counter'

    def update_language(self):
        self.lang_btn.text = self.app.get_translation("language")
        self.btn_date.text = self.app.get_translation("days_until")
        self.btn_love.text = self.app.get_translation("days_in_love")


class DateCounterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.selected_date = None
        self.time_event = None
        self.build_ui()

    def build_ui(self):
        self.layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        self.label = MDLabel(
            text=self.app.get_translation("select_date"),
            halign="center",
            font_style="H6",
            theme_text_color="Primary"
        )

        self.btn_pick = MDRaisedButton(
            text=self.app.get_translation("open_calendar"),
            size_hint=(1, None),
            height=50
        )
        self.btn_pick.bind(on_release=self.show_date_picker)

        self.btn_back = MDRaisedButton(
            text=self.app.get_translation("back"),
            size_hint=(1, None),
            height=50
        )
        self.btn_back.bind(on_release=self.go_back)

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.btn_pick)
        self.layout.add_widget(self.btn_back)
        self.add_widget(self.layout)

    def show_date_picker(self, *args):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_selected)
        date_dialog.open()

    def on_date_selected(self, instance, value, date_range):
        self.selected_date = value
        if self.time_event:
            self.time_event.cancel()
        self.time_event = Clock.schedule_interval(self.update_counter, 1)
        self.update_counter()

    def update_counter(self, *args):
        if self.selected_date:
            now = datetime.now()
            target = datetime.combine(self.selected_date, datetime.min.time())
            if target < now:
                self.label.text = "Выбранная дата уже прошла!"
                if self.time_event:
                    self.time_event.cancel()
                return

            delta = target - now
            days = delta.days
            seconds = delta.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60

            self.label.text = self.app.get_translation("days_left").format(
                days, hours, minutes, seconds
            )

    def go_back(self, *args):
        if self.time_event:
            self.time_event.cancel()
        self.manager.current = 'main'

    def update_language(self):
        self.label.text = self.app.get_translation("select_date")
        self.btn_pick.text = self.app.get_translation("open_calendar")
        self.btn_back.text = self.app.get_translation("back")
        if self.selected_date:
            self.update_counter()


class RelationshipCounterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.start_date = None
        self.time_event = None
        self.build_ui()

    def build_ui(self):
        self.layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        self.label = MDLabel(
            text=self.app.get_translation("select_love_date"),
            halign="center",
            font_style="H6",
            theme_text_color="Primary"
        )

        self.btn_pick = MDRaisedButton(
            text=self.app.get_translation("open_calendar"),
            size_hint=(1, None),
            height=50
        )
        self.btn_pick.bind(on_release=self.show_date_picker)

        self.btn_back = MDRaisedButton(
            text=self.app.get_translation("back"),
            size_hint=(1, None),
            height=50
        )
        self.btn_back.bind(on_release=self.go_back)

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.btn_pick)
        self.layout.add_widget(self.btn_back)
        self.add_widget(self.layout)

    def show_date_picker(self, *args):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_selected)
        date_dialog.open()

    def on_date_selected(self, instance, value, date_range):
        self.start_date = value
        if self.time_event:
            self.time_event.cancel()
        self.time_event = Clock.schedule_interval(self.update_counter, 1)
        self.update_counter()

    def update_counter(self, *args):
        if self.start_date:
            now = datetime.now()
            start = datetime.combine(self.start_date, datetime.min.time())
            if start > now:
                self.label.text = "Дата начала в будущем!"
                if self.time_event:
                    self.time_event.cancel()
                return

            delta = now - start
            days = delta.days
            seconds = delta.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60

            self.label.text = self.app.get_translation("days_together").format(
                days, hours, minutes, seconds
            )

    def go_back(self, *args):
        if self.time_event:
            self.time_event.cancel()
        self.manager.current = 'main'

    def update_language(self):
        self.label.text = self.app.get_translation("select_love_date")
        self.btn_pick.text = self.app.get_translation("open_calendar")
        self.btn_back.text = self.app.get_translation("back")
        if self.start_date:
            self.update_counter()


class LoveDaysApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.language = "RU"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"

    def build(self):
        self.sm = MDScreenManager()
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(DateCounterScreen(name='date_counter'))
        self.sm.add_widget(RelationshipCounterScreen(name='relationship_counter'))
        return self.sm

    def get_translation(self, key):
        return getattr(Language, self.language).get(key, key)

    def switch_language(self, lang):
        self.language = lang
        for screen in self.sm.screens:
            if hasattr(screen, 'update_language'):
                screen.update_language()
        if hasattr(self, 'menu'):
            self.menu.dismiss()


if __name__ == '__main__':
    LoveDaysApp().run()