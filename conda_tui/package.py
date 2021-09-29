import enum
import random
from dataclasses import dataclass
from typing import List

from conda_tui.environment import Environment


@dataclass
class ChannelType(str, enum.Enum):
    CONDA = "conda"
    PIP = "pip"


@dataclass
class Package:
    name: str
    version: str
    type: ChannelType
    description: str


def list_packages_for_environment(environment: Environment) -> List[Package]:
    environment_name = environment.name

    print(environment_name)

    return [
        Package(
            name=f"package-{i}",
            description=f"Package {i} does some cool thing",
            type=random.choice([ChannelType.CONDA, ChannelType.PIP]),
            version=f"{i / 10:0.1f}",
        )
        for i in range(1, 11)
    ]
