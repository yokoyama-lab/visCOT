"""Entry point for visCOT — visualize COT tree representations."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .core.canvas import Canvas
from .core.parser import parse


def main() -> None:
    arg_parser = argparse.ArgumentParser(
        description="Visualize COT tree representation of structurally stable "
        "incompressible flows."
    )
    arg_parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    arg_parser.add_argument(
        "expression",
        nargs="?",
        default=None,
        help="COT expression to visualize (reads stdin if omitted).",
    )
    arg_parser.add_argument(
        "-i", "--interactive", help="interactive mode", action="store_true"
    )
    arg_parser.add_argument(
        "-o", "--output", help="specify an output file (.png, .pdf, .svg, .eps)."
    )
    arg_parser.add_argument(
        "-f", "--file",
        type=argparse.FileType("r"),
        default=None,
        help="read expression from a file instead of stdin.",
    )
    arg_parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="output image resolution in DPI (default: 150).",
    )
    arg_parser.add_argument(
        "--parse-only",
        help="parse and print the tree structure without drawing.",
        action="store_true",
    )
    args = arg_parser.parse_args()

    if args.parse_only:
        text = _read_input(args)
        tree = parse(text)
        print(tree.show())
        return

    canvas = Canvas()
    if args.interactive:
        while True:
            try:
                s = input(">>> ")
                tree = parse(s)
                tree.set_canvas(canvas)
                tree.draw()
                action = input("Select (save/show): ")
                if action == "save":
                    filename = input("Filename: ")
                    if not filename:
                        filename = s + ".png"
                    canvas.save_canvas(filename, dpi=args.dpi)
                elif action == "show":
                    canvas.show_canvas()
                canvas.clear_canvas()
            except (AttributeError, ValueError) as e:
                print(f"Error: {e}", file=sys.stderr)
            except EOFError:
                break
    else:
        text = _read_input(args)
        tree = parse(text)
        tree.set_canvas(canvas)
        tree.draw()
        if args.output is None:
            canvas.show_canvas()
        else:
            canvas.save_canvas(args.output, dpi=args.dpi)
            canvas.close()


def _read_input(args: argparse.Namespace) -> str:
    """Read expression from positional argument, file, or stdin."""
    if args.expression:
        return str(args.expression)
    if args.file:
        with args.file as f:
            return str(f.read()).strip()
    return sys.stdin.read().strip()


if __name__ == "__main__":
    main()
