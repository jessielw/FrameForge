import os
import re
import shutil
import sys
from pathlib import Path
from subprocess import run


def get_site_packages() -> Path:
    output = run(
        ["uv", "pip", "show", "awsmfunc"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    get_location = re.search(r"Location: (.+)\n", output, flags=re.MULTILINE)
    if not get_location:
        raise FileNotFoundError("Can not detect site packages")
    return Path(get_location.group(1))


def build_app():
    # Change directory to the project's root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Ensure we're in a virtual env, if we are, install dependencies
    if sys.prefix == sys.base_prefix:
        raise Exception("You must activate your virtual environment first")
    else:
        check_packages = run(["uv", "sync", "--inexact"], check=True, text=True)
        if check_packages.returncode != 0:
            raise Exception("Failed to sync packages with UV")

    # Define the PyInstaller output path
    pyinstaller_folder = project_root / "pyinstaller_build"

    # Delete the old build folder if it exists
    shutil.rmtree(pyinstaller_folder, ignore_errors=True)

    # Create a folder for the PyInstaller output
    pyinstaller_folder.mkdir(exist_ok=True)

    # Define paths before changing directory
    img_gen = project_root / "frame_forge.py"
    icon_path = project_root / "images" / "icon.ico"
    additional_hooks_path = Path(Path.cwd() / "hooks")

    # get paths to needed vapoursynth files in venv
    site_packages = get_site_packages()
    vapoursynth_64 = site_packages / "vapoursynth64"
    vapoursynth_64_portable = site_packages / "portable.vs"

    # Change directory so PyInstaller outputs all of its files in its own folder
    os.chdir(pyinstaller_folder)

    # Run PyInstaller command
    build_job = run(
        [
            "uv",
            "run",
            "pyinstaller",
            # "-w",
            "--onefile",
            f"--icon={icon_path}",
            "--add-data",
            f"{vapoursynth_64};vapoursynth64",
            "--add-data",
            f"{vapoursynth_64_portable};.",
            "--name",
            "FrameForge",
            str(img_gen),
            f"--additional-hooks-dir={str(additional_hooks_path)}",
        ]
    )

    # Ensure the output of the .exe
    success = "Did not complete successfully"
    exe_path = project_root / pyinstaller_folder / "dist" / "FrameForge.exe"
    if exe_path.is_file() and str(build_job.returncode) == "0":
        success = f"\nSuccess!\nPath to exe: {str(exe_path)}"

    # Change directory back to the original directory
    os.chdir(project_root)

    # Return a success message
    return success


if __name__ == "__main__":
    build = build_app()
    print(build)
