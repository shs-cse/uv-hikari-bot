import tomlkit
from bot_environment import state
from bot_environment.config import FilePath

class FormatText:
    """
    Use ANSI color codes/graphics mode to emphasize changes
    reference: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
    """

    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    DIM_BOLD_RESET = "\033[22m"
    ITALICS = "\033[3m"
    UNDERLINE = "\033[4m"

    # dim yellow
    @staticmethod
    def wait(text: str) -> str:
        return f"\n{FormatText.YELLOW}{FormatText.DIM} {text}{FormatText.RESET}"

    # cyan
    @staticmethod
    def status(text: str) -> str:
        return f"\n{FormatText.CYAN}\t• {text}{FormatText.RESET}"

    # green
    @staticmethod
    def success(text: str) -> str:
        return f"\n{FormatText.GREEN}✔ {text}{FormatText.RESET}"

    # yellow
    @staticmethod
    def warning(text: str) -> str:
        return f"\n{FormatText.YELLOW}{FormatText.BOLD}‼️ {text}{FormatText.RESET}"

    # red
    @staticmethod
    def error(text: str) -> str:
        return f"\n\n{FormatText.RED}{FormatText.BOLD}✘ {text}{FormatText.RESET}"

    # only dim text and reset
    @staticmethod
    def dim(text: str) -> str:
        return f"{FormatText.DIM}{text}{FormatText.DIM_BOLD_RESET}"

    # only bold text and reset
    @staticmethod
    def bold(text: str) -> str:
        return f"{FormatText.BOLD}{text}{FormatText.DIM_BOLD_RESET}"


def update_info_key(key: str, new_value) -> None: # noqa:ANN001
    old_value = state.info[key]
    if old_value == new_value:
        return
    state.info[key] = new_value
    info_toml_path = FilePath.INFO_TOML
    with open(info_toml_path, 'w') as fp:
        tomlkit.dump(state.info, fp)
        log = f'{info_toml_path} > "{key}": updated...\n'
        log += FormatText.dim(f'\t- {"from:":>8}  {old_value}\n')
        log += FormatText.bold(f'\t+ {"to:":>8}  {new_value}')
        print(FormatText.warning(log))