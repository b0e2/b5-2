"""Command-line interface for Mini Git."""

import shlex


class CommandError(Exception):
    """An error that can be shown to the user."""


def run_command(line: str) -> bool:
    """Parse one command; return False to leave the REPL."""
    try:
        parts = shlex.split(line)
    except ValueError as exc:
        raise CommandError("Invalid args") from exc
    if not parts:
        return True

    command, *args = parts
    if command.upper() in ("EXIT", "QUIT"):
        if args:
            raise CommandError("Invalid args")
        return False
    raise CommandError(f"Unknown command: {command}")


def main() -> None:
    """Keep accepting commands until the user exits or closes input."""
    while True:
        try:
            line = input("mini-git> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        try:
            if not run_command(line):
                break
        except CommandError as exc:
            print(exc)


if __name__ == "__main__":
    main()
