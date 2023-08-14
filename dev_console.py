import threading
import sys


class CommandHandler:
    def __init__(self, script, id):
        self.script = script
        self.id = id
        self.console = Console.get_instance()
        self.logger = self.console.logger

    def call(self, command:str):
        """
            a command gets requested from this handler
            the handler id is always at the first position
            like: id command arg1 arg2 arg3 arg...
        """
        self.logger.info(f"{self.id} received command: {command}")

    @staticmethod
    def help_call(original_function):
        def wrapper(self, log):
            """Wrapper function to show help menu for handler"""
            text = f"\nHelp for handler: {self.id}\n"
            text += "=================================\n"
            text += "|||  built-in                 |||\n"
            text += "---------------------------------\n"
            text += f"{self.id} help - show this menu\n"
            text += "---------------------------------\n"
            text += "|||  custom                   |||\n"
            text += "---------------------------------\n"

            # Call the decorated function and append its result to the text
            result = original_function(self)
            text += result

            text += "\n=================================\n"
            log.info(text)

        return wrapper


class Console:
    _instance = None
    _lock = threading.Lock()

    @staticmethod
    def get_instance(game=None, logger=None, module_ref=None):
        with Console._lock:
            if Console._instance is None:
                Console._instance = Console(game, logger, module_ref)
        return Console._instance

    def __init__(self, game, logger, module_ref):
        if Console._instance is not None:
            raise Exception("Console class is a singleton. Use Console.get_instance() to get the instance.")

        self.game = game
        self.logger = logger
        self.module_ref = module_ref
        self.handler = {}

    def register_handler(self, handler:CommandHandler):
        self.handler[handler.id] = handler
        self.logger.info(f"{handler.id} registered as command handler")

    def console(self):
        """input handler"""
        while self.game.game_active:
            sys.stdout.write("> ")
            command = input().strip()

            split = command.split(" ", 1)
            if len(split) != 2:
                self.logger.warn(f"invalid command: {command}")
                sys.stdout.write("> ")
                continue

            handler_id = split[0]
            handler:CommandHandler = self.handler.get(handler_id)
            if handler is None:
                self.logger.warn(f"handler id: {handler_id} not registered")
                sys.stdout.write("> ")
                continue

            if command.startswith(handler_id + " help"):
                handler.help(self.logger)
                sys.stdout.write("> ")
                continue

            handler.call(command, self.logger)
            sys.stdout.write("> ")

    def run(self):
        """run dev console"""
        self.logger.info("Developer console started.")
        thread = threading.Thread(target=self.console)
        thread.start()
