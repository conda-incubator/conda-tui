from dataclasses import dataclass
from typing import List


@dataclass
class Environment:
    name: str
    path: str


def list_environments() -> List[Environment]:
    """Get a list of conda environments installed on local machine."""
    # TODO: Implement
    return [
        Environment(name="base", path="/path/to/base"),
        Environment(name="project-1", path="/path/to/project-1"),
    ]
