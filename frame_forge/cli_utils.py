import re


def frame_list(frames: str) -> list:
    if not re.match(r"\d+(?::\d+)*$", frames):
        raise ValueError("Input must be in the format of int:int i.e. 101:104")
    return [int(x) for x in frames.split(":")]
