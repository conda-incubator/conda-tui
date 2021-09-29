import enum
from dataclasses import dataclass
from typing import List

from conda_tui.environment import Environment


@dataclass
class ChannelType(enum.Enum, str):
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
            type=ChannelType.CONDA,
            version=f"{i / 10:0.1f}",
        )
        for i in range(1, 11)
    ]
