import random


class ConfigError(Exception):
    """Exception raised when the maze configuration is invalid."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with an error message.

        Args:
            message: Description of the configuration error.
        """
        super().__init__(message)


def is_truncated(s: str) -> bool:
    """Return whether a string has leading or trailing whitespace.

    Args:
        s: String to inspect.

    Returns:
        True if the string contains leading or trailing whitespace,
        False otherwise.
    """
    return s != s.strip()


def contains_space(pair: list[str]) -> bool:
    """Return whether either element has leading or trailing whitespace.

    Args:
        pair: Two-element list containing a configuration key and value.

    Returns:
        True if either string contains leading or trailing whitespace,
        False otherwise.
    """
    return is_truncated(pair[0]) or is_truncated(pair[1])


def is_valid(
        configuration: dict[str, str]) -> dict[
            str, str | int | bool | tuple[int, int]]:
    """Validate and convert a parsed maze configuration.

    Required parameters are checked for presence and validity. Numeric,
    boolean, and coordinate values are converted to their appropriate
    types, optional values are preserved, and a random seed is generated
    if none is provided.

    Args:
        configuration: Mapping of configuration keys to their raw string
            values.

    Returns:
        A validated configuration dictionary containing values converted
        to their appropriate types.

    Raises:
        ConfigError: If a required parameter is missing, a value has an
            invalid format, coordinates lie outside the maze dimensions,
            or the configuration is otherwise invalid.
    """

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
    """Parse and validate a maze configuration file.

    Blank lines and comments are ignored. Each remaining line must have
    the form ``key=value`` with no leading or trailing whitespace around
    the key or value.

    Args:
        content: Contents of the configuration file.

    Returns:
        A validated configuration dictionary with values converted to
        their appropriate types.

    Raises:
        ConfigError: If the configuration contains invalid syntax,
            duplicate keys, or invalid parameter values.
    """
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
