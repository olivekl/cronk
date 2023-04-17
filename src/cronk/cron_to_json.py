import json
import re
from dataclasses import dataclass, field
from io import TextIOWrapper
from typing import Tuple

from loguru import logger

from cronk.json_routine import Json, Routine


def cron_to_json(fp: TextIOWrapper) -> Json:
    """
    Converts a cron file to a json file.

    The json schema is:
    ```
        {
            intro: [
                "# initial comments",
                "# ..."
            ],
            commands: [
                {
                    description: [
                        "# comments above action"
                    ],
                    time: "Every day at 5 AM",
                    command: "echo Hello world"
                },
                {
                    description: [],
                    time: "Every hour",
                    command: "echo hackhackhack"
                }
            ],
            outro: [
                "# final comments",
                "..."
            ]
        }
    ```

    The intro comments and the first command's description are separated by the
    last blank line, unless there is a single comment block, in which case it is
    assumed to be the first command's description.

    ```
    # this is the intro
    # as is this

    # this is still the intro
                        <- this is the last blank line before the first command
    # this is the first command's description
    0 0 0 * * echo Hello World
    ```

    ```
    # There is no blank line, so this is all considered to be the first
    # command's description
    0 0 0 * * echo Hello World
    ```
    """
    logger.debug(f"Converting {fp.name} to json")

    lines = [s.rstrip() for s in fp.readlines()]

    # identify commands
    command_idx = _get_command_line_idx(lines)
    commands = [lines[i] for i in command_idx]

    if not commands:  # "empty" cron file, no commands
        return Json(intro=lines)

    intro, command_comments, outro = _split_comments(lines, command_idx)

    commands = [
        Routine(comment, command)
        for comment, command in zip(command_comments, commands)
    ]

    return Json(intro=intro, commands=commands, outro=outro)


def _is_command(s: str) -> bool:
    return s != "" and not bool(re.search("^ *#", s))


def _get_command_line_idx(lines: list[str]) -> list[int]:
    line_types = [_is_command(line) for line in lines]
    return [i for i, is_command_line in enumerate(line_types) if is_command_line]


def _split_comments(
    lines: list[str], command_idx: list[int]
) -> Tuple[list[str], list[list[str]], list[str]]:
    end_of_intro = 0
    for i, line in enumerate(lines[: command_idx[0]]):
        if line == "":
            end_of_intro = i

    intro = lines[:end_of_intro]

    command_comments = [
        lines[(start + 1) : end]
        for start, end in zip([end_of_intro] + command_idx, command_idx + [len(lines)])
    ]

    outro = command_comments.pop()

    return intro, command_comments, outro


if __name__ == "__main__":
    with open("src/cronk/test.txt") as f:
        print(cron_to_json(f))
