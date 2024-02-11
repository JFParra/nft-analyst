"""
    Common configuration data and functions for the application.

    author: Spori.eth
"""
from pydantic import BaseModel

from config.yaml_parser import YamlParser


class AlchemyConfig(BaseModel):
    api_key: str | None
    base_url: str


class NFTConfig(BaseModel):
    contract_address: str


class AppConfig(BaseModel):
    alchemy: AlchemyConfig
    nft: NFTConfig


class Configuration:
    def __init__(self, cfg_path: str):
        self.cfg_path: str = cfg_path
        print(self.cfg_path)
        self.config: dict = YamlParser.parse(self.cfg_path)
        self.app_config: AppConfig = AppConfig.parse_obj(self.config)

# ======================================
# End of script configuration.py
# ======================================
