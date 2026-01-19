def colorString(color="", string=""):
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
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
        case _:
            return string
