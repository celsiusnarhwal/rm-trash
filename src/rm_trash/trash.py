import os
import subprocess
from pathlib import Path

import inflect as ifl
import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, track

import commands

inflect = ifl.engine()

app = typer.Typer()


@app.command()
def trash(files: list[Path] = typer.Argument(...),
          dirs: bool = typer.Option(False, "--dir", "-d", help="Also trash directories."),
          force: bool = typer.Option(False, "--force", "-f",
                                     help="Trash files without asking and don't complain when attempting to trash "
                                          "files that don't exist. Overrides -i and -I."),
          interactive: bool = typer.Option(False, "--interactive", "-i", help="Ask before trashing each file,"
                                                                              " regardless of the file's permissions. "
                                                                              "Overrides -I."),
          interactive_once: bool = typer.Option(False, "--interactive=once", "-I", help="Ask once before trashing "
                                                                                        "more than three files or "
                                                                                        "recursively trashing a "
                                                                                        "directory."),
          recursive: bool = typer.Option(False, "--recursive", "-R", "-r",
                                         help="Trash directories recursively. You will "
                                              "not be asked for confirmation to trash "
                                              "files within the directories "
                                              "you specify, regardless of the file's "
                                              "permissions or whether you also passed "
                                              "-i or -I. Implies -d."),
          verbose: bool = typer.Option(False, "--verbose", "-v", help="Show the name of each file as it's trashed."),
          quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all output aside from errors and "
                                                                  "prompts. Overrides -v."),
          one_file_system: bool = typer.Option(False, "--one-file-system", "-x", help="When recursively trashing a "
                                                                                      "directory, skip subdirectories "
                                                                                      "on different volumes."),
          mute: bool = typer.Option(False, "--mute", "-m", help="Mute the \"Trash\" sound effect by muting your volume "
                                                                "while trash runs and then unmuting it afterwards "
                                                                "(if it was unmuted before trash was run). trash "
                                                                "will play the sound effect once on completion. Has no "
                                                                "effect if your volume is muted to start with."),
          full_mute: bool = typer.Option(False, "--mute=full", "-M", help="The same as -m, but trash will not play "
                                                                          "the sound effect on completion. Overrides "
                                                                          "-m."),
          dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run as usual but without actually trashing "
                                                                      "anything.")

          ):
    """
    Move files to the trash.
    """

    def echo(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    was_initially_muted = commands.get_is_muted()

    dirs = dirs or recursive
    interactive = interactive and not force
    interactive_once = interactive_once and not any([force, interactive])
    verbose = verbose and not quiet
    mute = mute and not full_mute

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        if not quiet:
            progress.add_task("Getting ready...", total=None)

        are_directories = any(Path(file).is_dir() for file in files)
        if are_directories and not dirs:
            echo(
                "[bold red]Error: [/bold red]Refusing to remove directories without [bold green]-d[/] or "
                "[bold green]-R[/]."
            )
            raise typer.Exit(1)

        if are_directories and any(
                Path(file).exists() and next(Path(file).iterdir(), None) for file in files
        ) and not recursive:
            echo("[bold red]Error: [/]Refusing to remove non-empty directories without [bold green]-R[/].")
            raise typer.Exit(1)

    if interactive_once:
        warnings = []
        if len(files) > 3:
            warnings.append("remove more than three files")

        if are_directories and recursive:
            warnings.append("remove one or more directories recursively")

        if warnings:
            if not typer.confirm(f"You're trying to {inflect.join(warnings)}. Are you sure?"):
                raise typer.Exit()

    if mute or full_mute:
        commands.toggle_mute(state=True)

    for path in track(files, description="Trashing...") if not quiet else files:
        if not path.is_absolute():
            path = path.resolve()

        if path.exists():
            if interactive:
                if not typer.confirm(f"Remove {path}?"):
                    continue
            elif not os.access(path, os.W_OK):
                if not typer.confirm(f"{path} is read-only. Remove anyway?"):
                    continue

            if one_file_system:
                if Path.cwd().parents[1] == "Volumes" and Path.cwd().parents[1] != path.parents[1]:
                    continue
                elif path.parents[1] == "Volumes":
                    continue

            if verbose:
                echo(f"Trashing [bold yellow]{path}[/]")

            if not dry_run:
                commands.send_to_trash(path)
        elif not force:
            echo(f"[bold yellow]Warning: [/bold yellow]'{path}' does not exist.")
            continue

    if mute or full_mute:
        if not was_initially_muted:
            commands.toggle_mute(state=False)

        if not full_mute:
            commands.play_trash_sound()


@app.command(name="dir")
def trash_dir(directories: list[Path] = typer.Argument(...),
              components: bool = typer.Option(False, "--parents", "-p", help="Also trash directory parents. "
                                                                             "The parent directories must be empty "
                                                                             "aside from their child directories "
                                                                             "in the same path, which in turn must be "
                                                                             "empty in the same way."),
              verbose: bool = typer.Option(False, "--verbose", "-v",
                                           help="Print the name of each directory as it's trashed."),
              quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all output aside from errors and "
                                                                      "prompts. Overrides -v."),
              mute: bool = typer.Option(False, "--mute", "-m", help="Mute the \"Trash\" sound effect by muting your "
                                                                    "volume while trash runs and then unmuting it "
                                                                    "afterwards (if it was unmuted before trash "
                                                                    "was run). trash will play the sound effect once "
                                                                    "on completion. Has no effect if your volume is "
                                                                    "muted to start with."),
              full_mute: bool = typer.Option(False, "--mute=full", "-M", help="The same as -m, but trash will not "
                                                                              "play the sound effect on completion. "
                                                                              "Overrides -m."),
              dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run as usual but without actually trashing "
                                                                          "anything.")):
    """
    Move directories to the trash. Directories must be empty.
    """
    if not all(Path(directory).is_dir() for directory in directories):
        print("[bold red]Error: [/]Refusing to remove non-directories. Use [bold green]trash[/] instead.")
        raise typer.Exit(1)

    if any(next(Path(directory).iterdir(), None) for directory in directories) and not components:
        print("[bold red]Error: [/]Refusing to remove non-empty directories. Use [bold green]trash -R[/] instead.")
        raise typer.Exit(1)

    removals = []
    for path in directories:
        if components:
            parts = path.resolve().parts
            resolved_parts = [Path("/").joinpath(*parts[:i]) for i in range(1, len(parts) + 1)]
            root_part_index = -len(str(path).split("/"))

            if any(len(list(part.iterdir())) > 1 for part in resolved_parts[root_part_index:]):
                print(f"[bold red]Error: [/]'{path}' is not empty or has non-empty parents. Use [bold green]trash "
                      f"-R[/] instead.")
                raise typer.Exit(1)

            removals.extend(
                reversed(["/".join(parts[:i]).replace("//", "/") for i in range(1, len(parts) + 1)][root_part_index:]))
        else:
            removals.append(path)

    trash(list(map(Path, removals)), dirs=True, verbose=verbose, quiet=quiet, mute=mute, full_mute=full_mute,
          dry_run=dry_run)


@app.command()
def empty(yes: bool = typer.Option(None, "--yes", "-y", help="Bypass the confirmation prompt.")):
    """
    Empty the trash. This can't be undone.
    """
    if yes or typer.confirm("Are you sure you want to empty the trash? This can't be undone."):
        commands.empty_trash()


def license_callback(value: bool):
    if value:
        print(Path("LICENSE.md").read_text())
        raise typer.Exit()


@app.callback(epilog="Copyright (c) 2022-present celsius narhwal. Licensed under MIT.")
def main(show_license: bool = typer.Option(False, "--license", "-l", callback=license_callback, is_eager=True,
                                           help="Show trash's license.")):
    """
    Trash files and directories from your command line. A safer alternative to rm and rmdir.

    For help with a specific command, run trash [command] --help.
    """
    if os.geteuid() == 0 and "disabled" in subprocess.run(["csrutil", "status"], capture_output=True).stdout.decode():
        print("[bold red]Error: [/]trash refuses to run as root when System Integrity Protection is disabled.\n"
              "If you must do whatever you're trying to do, do it with [bold green]rm[/].\n"
              "(If you aliased rm to trash, you can escape the alias with a backslash (e.g., [bold green]\\rm[/]).)")
        raise typer.Exit(1)


if __name__ == '__main__':
    app()
