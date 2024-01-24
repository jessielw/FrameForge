import sys
from pathlib import Path


def exit_application(msg: str, exit_code: int = 0):
    """A clean way to exit the program without raising traceback errors

    Args:
        msg (str): Success or Error message you'd like to display in the console
        exit_code (int): Can either be 0 (success) or 1 (fail)
    """
    if exit_code not in {0, 1}:
        raise ValueError("exit_code must only be '0' or '1' (int)")

    if exit_code == 0:
        output = sys.stdout
    elif exit_code == 1:
        output = sys.stderr

    print(msg, file=output, flush=True)
    sys.exit(exit_code)


def get_working_dir():
    """
    Used to determine the correct working directory automatically.
    This way we can utilize files/relative paths easily.

    Returns:
        (Path): Current working directory
    """
    # we're in a pyinstaller bundle
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys.executable).parent

    # we're running from a *.py file
    else:
        return Path.cwd()


def hex_to_bgr(hex_code):
    # Remove the '#' if present
    hex_code = hex_code.lstrip("#")

    # Convert hex to BGR format
    bgr_values = f"&H{int(hex_code[4:6], 16):02X}{int(hex_code[2:4], 16):02X}{int(hex_code[0:2], 16):02X}"

    return bgr_values
