COLOR_BLACK = "\033[30m"
COLOR_RED = "\033[31m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"
COLOR_MAGENTA = "\033[35m"
COLOR_CYAN = "\033[36m"
COLOR_WHITE = "\033[37m"
COLOR_RESET = "\033[0m"

def color_text(text, color):
    return f"{color}{text}{COLOR_RESET}"