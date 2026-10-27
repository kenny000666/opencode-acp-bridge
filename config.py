"""Bridge configuration — env-driven via pydantic-settings."""
from __future__ import annotations
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    acp_host: str = Field(default="127.0.0.1", alias="ACP_HOST")
    acp_port: int = Field(default=8000, alias="ACP_PORT")
    opencode_url: str = Field(default="http://127.0.0.1:4096", alias="OPENCODE_URL")
    opencode_username: str = Field(default="opencode", alias="OPENCODE_SERVER_USERNAME")
    opencode_password: str = Field(default="", alias="OPENCODE_SERVER_PASSWORD")
    opencode_timeout_s: float = Field(default=600.0, alias="OPENCODE_TIMEOUT_S")
    opencode_working_dir: str = Field(default="", alias="OPENCODE_WORKING_DIR")
    agent_name: str = Field(default="opencode", alias="ACP_AGENT_NAME")
    agent_description: str = Field(default="Autonomous coding agent backed by a remote OpenCode server.", alias="ACP_AGENT_DESCRIPTION")
    reuse_sessions: bool = Field(default=True, alias="ACP_REUSE_SESSIONS")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
