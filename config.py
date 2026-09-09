from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    model_name: str = "ProtectAI/deberta-v3-base-prompt-injection-v2"
    threshold: float = 0.85
    max_segment_chars: int = 512
    backend_url: str = "http://localhost:11434/v1/chat/completions"
    backend_api_key: str = ""
    db_path: str = "data/audit.db"
    host: str = "0.0.0.0"
    port: int = 8080
    policy_mode: str = "block"  # block | flag | observe


settings = Settings()
