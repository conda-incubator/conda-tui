from typing import Dict

from conda.core.prefix_data import PrefixData


def list_packages(prefix: str) -> Dict[str, PrefixData]:
    installed = sorted(
        PrefixData(prefix, pip_interop_enabled=True).iter_records(),
        key=lambda x: x.name,
    )
    return {prec.name: prec for prec in installed}


if __name__ == "__main__":
    from env_list import get_envs, get_name
    from rich import print
    from rich.table import Table

    for env in get_envs():
        tbl = Table(title=get_name(env) or env)
        tbl.add_column("Package")
        tbl.add_column("Version")
        tbl.add_column("Build")
        tbl.add_column("Features")
        tbl.add_column("Channel")
        for name, prec in list_packages(env).items():
            tbl.add_row(
                name,
                prec.version,
                prec.build,
                ", ".join(prec.get("format", ())),
                prec.get("schannel"),
            )

        print(tbl)
