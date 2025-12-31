"""Configuration management for the audiobook creator."""

from pathlib import Path
from typing import Any, Dict
import yaml
from pydantic import BaseModel, Field


class AudioConfig(BaseModel):
    """Audio generation configuration."""
    voice: str = "Alex"
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    format: str = Field(default="mp3", pattern="^(mp3|m4b|aiff)$")
    quality: str = Field(default="high", pattern="^(low|medium|high)$")
    bitrate: int = Field(default=192, ge=64, le=320)


class ProcessingConfig(BaseModel):
    """Text processing configuration."""
    detect_chapters: bool = True
    clean_text: bool = True
    remove_page_numbers: bool = True
    remove_headers_footers: bool = True
    normalize_whitespace: bool = True
    fix_hyphenation: bool = True
    lines_per_chunk: int = Field(default=50, ge=1, le=1000)


class OutputConfig(BaseModel):
    """Output configuration."""
    separate_chapters: bool = False
    add_metadata: bool = True
    cleanup_intermediate: bool = True
    create_m4b: bool = False


class DatabaseConfig(BaseModel):
    """Database configuration."""
    path: str = Field(default="audiobooks.db")
    echo: bool = Field(default=False)


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str | None = None


class PerformanceConfig(BaseModel):
    """Performance configuration."""
    max_workers: int = Field(default=4, ge=1, le=16)
    timeout_seconds: int = Field(default=300, ge=30, le=3600)
    max_retries: int = Field(default=3, ge=1, le=10)


class Config(BaseModel):
    """Main configuration class."""
    audio: AudioConfig = AudioConfig()
    processing: ProcessingConfig = ProcessingConfig()
    output: OutputConfig = OutputConfig()
    database: DatabaseConfig = DatabaseConfig()
    logging: LoggingConfig = LoggingConfig()
    performance: PerformanceConfig = PerformanceConfig()
    chapter_patterns: list[str] = []


class ConfigManager:
    """Manages application configuration."""

    def __init__(self, config_path: Path | None = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to custom config file. If None, uses default config.
        """
        self.config_path = config_path or self._get_default_config_path()
        self._config: Config | None = None

    @staticmethod
    def _get_default_config_path() -> Path:
        """Get path to default configuration file."""
        return Path(__file__).parent.parent.parent / "config" / "default_config.yaml"

    def load(self) -> Config:
        """
        Load configuration from file.

        Returns:
            Config: Loaded configuration object

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)

        try:
            self._config = Config(**config_dict)
            return self._config
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}") from e

    @property
    def config(self) -> Config:
        """
        Get current configuration, loading if necessary.

        Returns:
            Config: Current configuration
        """
        if self._config is None:
            self.load()
        return self._config

    def reload(self) -> Config:
        """
        Reload configuration from file.

        Returns:
            Config: Reloaded configuration
        """
        return self.load()

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration values.

        Args:
            updates: Dictionary of configuration updates
        """
        if self._config is None:
            self.load()

        # Update nested configuration
        for key, value in updates.items():
            if hasattr(self._config, key):
                if isinstance(value, dict):
                    # Update nested config
                    nested_config = getattr(self._config, key)
                    for nested_key, nested_value in value.items():
                        setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(self._config, key, value)


# Global configuration instance
_config_manager: ConfigManager | None = None


def get_config(config_path: Path | None = None) -> Config:
    """
    Get global configuration instance.

    Args:
        config_path: Optional path to custom config file

    Returns:
        Config: Global configuration object
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager.config


def reload_config() -> Config:
    """
    Reload global configuration.

    Returns:
        Config: Reloaded configuration
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.reload()
