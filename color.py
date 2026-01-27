def colorString(color="", string=""):
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_GREEN = "\033[92m"
    ENDC = "\033[0m"

    match color:
        case "red":
            return f"{RED}{string}{ENDC}"
        case "green":
            return f"{GREEN}{string}{ENDC}"
        case "yellow":
            return f"{YELLOW}{string}{ENDC}"
        case "blue":
            return f"{BLUE}{string}{ENDC}"
        case "magenta":
            return f"{MAGENTA}{string}{ENDC}"
        case "cyan":
            return f"{CYAN}{string}{ENDC}"
        case "bright_magenta":
            return f"{BRIGHT_MAGENTA}{string}{ENDC}"
        case "bright_green":
            return f"{BRIGHT_GREEN}{string}{ENDC}"
        case _:
            return string
