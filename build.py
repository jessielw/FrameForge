from pathlib import Path
from subprocess import run
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
    img_gen = project_root / "image_generator.py"
    icon_path = project_root / "images" / "icon.ico"
    additional_hooks_path = Path(Path.cwd() / "hooks")

    # paths to needed vapoursynth files
    vapoursynth_64 = project_root / ".venv" / "Lib" / "site-packages" / "vapoursynth64"
    vapoursynth_64_portable = (
        project_root / ".venv" / "Lib" / "site-packages" / "portable.vs"
    )

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
            "Image-Generator",
            str(img_gen),
            f"--additional-hooks-dir={str(additional_hooks_path)}",
        ]
    )

    # Ensure the output of the .exe
    success = "Did not complete successfully"
    exe_path = project_root / pyinstaller_folder / "dist" / "Image-Generator.exe"
    if exe_path.is_file() and str(build_job.returncode) == "0":
        success = f"\nSuccess!\nPath to exe: {str(exe_path)}"

    # Change directory back to the original directory
    os.chdir(project_root)

    # Return a success message
    return success


if __name__ == "__main__":
    build = build_app()
    print(build)
