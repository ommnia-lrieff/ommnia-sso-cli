from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import typer
import tomlkit

from ommnia_sso_cli.data.models import ConfigModel


@dataclass
class ConfigRepository:
    app_name: str

    @property
    def app_path(self) -> Path:
        return Path(typer.get_app_dir(self.app_name))

    @property
    def config_file_path(self) -> Path:
        return self.app_path / "config.toml"

    def load(self) -> Optional[ConfigModel]:
        try:
            with self.config_file_path.open("r") as config_file:
                return ConfigModel.model_validate(tomlkit.load(config_file))
        except FileNotFoundError:
            return None

    def save(self, config: ConfigModel) -> None:
        self.app_path.mkdir(parents=True, exist_ok=True)
        with self.config_file_path.open("w+") as config_file:
            config_file.write(tomlkit.dumps(config.model_dump()))
