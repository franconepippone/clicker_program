import tomllib
from packaging.version import Version, InvalidVersion


def get_pyproject_version() -> Version | None:
    """Reads version from pyproject.toml file
    """
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)

    version_str: str = data["project"]["version"]
    try:
        return Version(version_str)
    except InvalidVersion:
        return None


def get_pyproject_version_str(invalid: str = "invalid version") -> str:
    ver = get_pyproject_version()
    if ver:
        return str(ver)
    else:
        return invalid