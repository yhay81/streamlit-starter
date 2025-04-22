from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # OpenAI APIの設定
    openai_api_key: str = Field(..., description="OpenAI API Key")

    # 環境変数の設定
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# シングルトンパターンでインスタンスを生成
settings = Settings()
