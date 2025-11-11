import tomllib
from packaging.version import Version, InvalidVersion
from utils.resource_resolver import resource_path

__version__ = "1.0.3"

def get_pyproject_version_str() -> str:
    return __version__

def get_pyproject_version() -> Version | None:
    """Reads version from pyproject.toml file
    """
    with open(resource_path("pyproject.toml"), "rb") as f:
        data = tomllib.load(f)

    version_str: str = data["project"]["version"]
    try:
        return Version(version_str)
    except InvalidVersion:
        return None


def _get_pyproject_version_str(invalid: str = "invalid version") -> str:
    ver = get_pyproject_version()
    if ver:
        return str(ver)
    else:
        return invalid