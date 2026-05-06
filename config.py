from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Bella Tavola API"
    description: str = "API do restaurante Bella Tavola"
    version: str = "1.0.0"
    chef: str = "Enzo Takida"
    debug: bool = False
    max_mesas: int = 20
    max_pessoas_por_mesa: int = 10


settings = Settings()
