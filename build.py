from pathlib import Path
from subprocess import run, PIPE
import os
import shutil
import sys


def build_app():
    # Change directory to the project's root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Ensure we're in a virtual env, if we are, install dependencies using Poetry
    if sys.prefix == sys.base_prefix:
        raise Exception("You must activate your virtual environment first")
    else:
        # Use Poetry to install dependencies
        run(["poetry", "install"])

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

    # get poetry venv path
    poetry_venv_path = run(
        ["cmd", "/c", "poetry", "env", "info", "--path"],
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        check=True,
    )
    if poetry_venv_path.returncode == 0 and poetry_venv_path.stdout:
        poetry_venv_path = Path(poetry_venv_path.stdout.strip())
        site_packages = poetry_venv_path / "Lib" / "site-packages"

        # get paths to needed vapoursynth files in poetry venv
        vapoursynth_64 = site_packages / "vapoursynth64"
        vapoursynth_64_portable = site_packages / "portable.vs"
    else:
        raise FileNotFoundError("Cannot find path to poetry venv")

    # Change directory so PyInstaller outputs all of its files in its own folder
    os.chdir(pyinstaller_folder)

    # Run PyInstaller command with Poetry's virtual environment
    build_job = run(
        [
            "poetry",
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
