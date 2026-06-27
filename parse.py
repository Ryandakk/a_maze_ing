import random


class ConfigError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def is_truncated(s: str) -> bool:
    return s != s.strip()


def contains_space(pair: list[str]) -> bool:
    return is_truncated(pair[0]) or is_truncated(pair[1])


def is_valid(
        configuration: dict[str, str]) -> dict[
            str, str | int | bool | tuple[int, int]]:

    required: list[str] = ["WIDTH", "HEIGHT", "ENTRY",
                           "EXIT", "OUTPUT_FILE", "PERFECT"]
    validated: dict[str, str | int | bool | tuple[int, int]] = {}
    for parameter in required:
        if parameter not in configuration:
            raise ConfigError(f"Missing parameter {parameter}")
        if parameter == "WIDTH" or parameter == "HEIGHT":
            try:
                value: int = int(configuration[parameter])
            except ValueError:
                raise ConfigError(f"{parameter} must be a valid integer")
            if value <= 0:
                raise ConfigError(f"{parameter} must be positive")
            validated[parameter] = value
        elif parameter == "ENTRY" or parameter == "EXIT":
            coordinates = configuration[parameter].split(",")
            if len(coordinates) != 2 or contains_space(coordinates):
                raise ConfigError(f"{parameter} expects value <x>,<y>")
            print("coordinates:       ", coordinates)
            try:
                x: int = int(coordinates[0])
                y: int = int(coordinates[1])
            except ValueError:
                raise ConfigError(f"{parameter} must be a valid integer")
            w = validated["WIDTH"]
            h = validated["HEIGHT"]

            assert isinstance(w, int)
            assert isinstance(h, int)
            if (x < 0 or x >= w or y < 0 or
                    y >= h):
                raise ConfigError(
                    f"{coordinates} is not within the defined dimensions")

            validated[parameter] = (x, y)
        elif parameter == "PERFECT":
            perfect: str = configuration[parameter]
            if perfect == "True":
                validated[parameter] = True
            elif perfect == "False":
                validated[parameter] = False
            else:
                raise ConfigError(f"{parameter} expects True or False")
        else:
            validated[parameter] = configuration[parameter]
    for parameter in configuration:
        if parameter not in validated:
            validated[parameter] = configuration[parameter]
    if validated["ENTRY"] == validated["EXIT"]:
        raise ConfigError("Entry and exit must be different")

    try:
        validated["SEED"] = int(
            configuration["SEED"]) if "SEED" in configuration else (
                random.randint(1, 1000))
    except ValueError:
        raise ConfigError("SEED must be a valid integer")

    return validated


def parsing(content: str) -> dict[
        str, str | int | bool | tuple[int, int]]:
    lines = content.split("\n")
    configuration: dict[str, str] = {}
    for line in lines:
        if line.strip() == "" or line[0] == '#':
            continue
        pair: list[str] = line.split("=")
        if len(pair) != 2:
            raise ConfigError(
                f"Invalid syntax on '{line}'. Must be <key>=<value>")
        if contains_space(pair):
            raise ConfigError(
                f"Line '{line}' contains spaces. Must be <key>=<value>")
        if pair[0] in configuration:
            raise ConfigError(f"{pair[0]} is duplicated")
        configuration[pair[0]] = pair[1]

    return is_valid(configuration)
