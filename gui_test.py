from guizero import App, Text, PushButton, TextBox

def say_my_name():
    welcome_message.value = my_name.value

app = App(title="World Record Indoor Ski")
my_name = TextBox(app)


update_text = PushButton(app, command=say_my_name, text="Display my name")
welcome_message = Text(app, text="Welcome to my app", size=40, font="Times New Roman", color="lightblue")

app.display()
