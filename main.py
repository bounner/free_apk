import sqlite3
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen

# --- Database ---
class DatabaseHelper:
    def __init__(self, db_name="OrangeApp.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()
    
    def create_table(self):
        query = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)"
        self.conn.execute(query)
        self.conn.commit()
    
    def add_user(self, username, password):
        query = "INSERT INTO users (username, password) VALUES (?, ?)"
        self.conn.execute(query, (username, password))
        self.conn.commit()
    
    def check_user(self, username, password):
        cursor = self.conn.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        row = cursor.fetchone()
        return row is not None

# --- Models ---
class Level:
    def __init__(self, id, price, forfait):
        self.id = id
        self.price = price
        self.forfait = forfait

class Operator:
    def __init__(self, name, levels):
        self.name = name
        self.levels = levels

# --- Screens ---
class LoginScreen(Screen):
    def register(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        if username and password:
            self.manager.db_helper.add_user(username, password)
            self.show_popup("Compte créé ! Connectez-vous.")
        else:
            self.show_popup("Remplissez tous les champs")
    
    def login(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        if self.manager.db_helper.check_user(username, password):
            self.manager.current = "main"
        else:
            self.show_popup("Identifiants incorrects")
    
    def show_popup(self, message):
        popup = Popup(title="Info",
                      content=Label(text=message),
                      size_hint=(0.6, 0.4))
        popup.open()

class MainScreen(Screen):
    def on_enter(self):
        self.operators = [
            Operator("MTN CM", [Level(1, 10, "500 Mo - 500 FCFA"),
                                Level(2, 20, "1 Go - 1000 FCFA"),
                                Level(3, 30, "2 Go - 2000 FCFA")]),
            Operator("Orange CM", [Level(1, 10, "500 Mo - 500 FCFA"),
                                   Level(2, 20, "1 Go - 1000 FCFA"),
                                   Level(3, 30, "2 Go - 2000 FCFA")]),
            Operator("MOOV (Bénin)", [Level(1, 15, "750 Mo - 750 FCFA"),
                                      Level(2, 25, "1.5 Go - 1500 FCFA")]),
            Operator("Airtel (Niger)", [Level(1, 12, "600 Mo - 600 FCFA"),
                                        Level(2, 22, "1.2 Go - 1200 FCFA")])
        ]
        rv = self.ids.operator_rv
        rv.data = [{'text': op.name, 'on_release': lambda op=op: self.show_levels_dialog(op)} for op in self.operators]
    
    def show_levels_dialog(self, operator):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        for level in operator.levels:
            btn = Button(text=f"Level {level.id} : {level.price} USDT - {level.forfait}",
                         size_hint_y=None, height=dp(40))
            btn.bind(on_release=lambda inst, lvl=level: self.show_payment_dialog(lvl))
            content.add_widget(btn)
        popup = Popup(title=operator.name, content=content, size_hint=(0.8, 0.8))
        popup.open()
    
    def show_payment_dialog(self, level):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        info = Label(text=f"Prix : {level.price} USDT\nAdresse USDT : 0x1234567890abcdef1234567890abcdef")
        content.add_widget(info)
        btn = Button(text="Activer le forfait", size_hint_y=None, height=dp(40))
        content.add_widget(btn)
        payment_popup = Popup(title="Paiement", content=content, size_hint=(0.8, 0.5))
        btn.bind(on_release=lambda instance: self.redirect_telegram(payment_popup))
        payment_popup.open()
    
    def redirect_telegram(self, popup):
        popup.dismiss()
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        label = Label(text="Pour activer votre forfait, vous serez redirigé vers un admin Telegram.\n"
                           "Veuillez préparer une capture d’écran de votre paiement et l’ID de transaction (hash USDT) comme preuve.")
        content.add_widget(label)
        btn = Button(text="OK", size_hint_y=None, height=dp(40))
        content.add_widget(btn)
        redirect_popup = Popup(title="Redirection", content=content, size_hint=(0.8, 0.5))
        btn.bind(on_release=lambda instance: redirect_popup.dismiss())  # No webbrowser on GitHub
        redirect_popup.open()
    
    def show_note(self):
        note_text = ("Comment procéder :\n"
                     "1. Choisissez un opérateur et un level.\n"
                     "2. Notez le prix en USDT et envoyez-le à l’adresse affichée via votre portefeuille.\n"
                     "3. Prenez une capture d’écran et trouvez l’ID de transaction.\n"
                     "4. Cliquez sur 'Activer le forfait', lisez la pop-up, puis contactez l’admin Telegram.\n"
                     "5. Envoyez la capture et l’ID à l’admin.")
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        label = Label(text=note_text)
        content.add_widget(label)
        btn = Button(text="OK", size_hint_y=None, height=dp(40))
        content.add_widget(btn)
        note_popup = Popup(title="Note", content=content, size_hint=(0.8, 0.5))
        btn.bind(on_release=lambda instance: note_popup.dismiss())
        note_popup.open()

# --- KV Layout ---
kv = '''
ScreenManager:
    LoginScreen:
        name: "login"
    MainScreen:
        name: "main"

<LoginScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 10
        TextInput:
            id: username
            hint_text: "Nom d'utilisateur"
            multiline: False
        TextInput:
            id: password
            hint_text: "Mot de passe"
            password: True
            multiline: False
        Button:
            text: "S'inscrire"
            on_press: root.register()
        Button:
            text: "Se connecter"
            on_press: root.login()

<MainScreen>:
    BoxLayout:
        orientation: "vertical"
        RecycleView:
            id: operator_rv
            viewclass: 'Button'
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
        Button:
            text: "Note"
            size_hint_y: None
            height: dp(50)
            on_press: root.show_note()
'''

class MyApp(App):
    def build(self):
        sm = Builder.load_string(kv)
        sm.db_helper = DatabaseHelper()
        return sm

if __name__ == '__main__':
    MyApp().run()