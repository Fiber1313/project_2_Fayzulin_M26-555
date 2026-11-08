import prompt


def welcome():
    """Приветствует пользователя и обрабатывает команды help и exit."""
    print("Первая попытка запустить проект!")
    print("\n***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

    while True:
        command = prompt.string("Введите команду: ")
        if command == "exit":
            return
        elif command == "help":
            print("\n<command> exit - выйти из программы")
            print("<command> help - справочная информация")