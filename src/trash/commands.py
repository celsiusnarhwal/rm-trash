import re
import subprocess
import tempfile
from pathlib import Path


def _execute(cmd: str, return_output=False):
    script = tempfile.TemporaryFile("w+")
    script.write(cmd)
    script.seek(0)
    output = subprocess.run(["osascript", "-e", script.read()], check=True, capture_output=True)

    if return_output:
        return output.stdout.decode()


def _tell_finder(cmd: str):
    _execute(f"tell application \"Finder\" to {cmd}")


def _afplay(path: Path):
    _execute(f"do shell script \"afplay \\\"{path}\\\"\"")


def send_to_trash(path: Path):
    if not path.is_absolute():
        path = path.resolve()

    _tell_finder(f"delete POSIX file \"{path}\"")


def empty_trash():
    _tell_finder("empty the trash")


def toggle_mute(state: bool):
    _execute(f"set volume output muted {state}")


def get_is_muted():
    volume_settings = _execute("get volume settings", return_output=True)

    pattern = re.compile(r"output volume:(\d+), input volume:(\d+), "
                         r"alert volume:(\d+), output muted:(true|false)")

    _, _, _, muted = pattern.match(volume_settings).groups()

    return muted == "true"


def play_trash_sound():
    sound_file = Path(("/System/Library/Components/CoreAudio.component/Contents/"
                       "SharedSupport/SystemSounds/dock/drag to trash.aif"))

    _afplay(sound_file)
