from bot_environment import state
import sys, warnings
from setup_validation.toml_inputs import check_and_load_info


def main() -> None:
    # check if `-d` flag was used `python -dO main.py`
    state.is_debug = "d" in sys.orig_argv[1]
    # ignore pygsheets warnings in normal mode
    if not state.is_debug:
        warnings.simplefilter("ignore")
    # validate and update state.info
    check_and_load_info()


if __name__ == "__main__":
    main()