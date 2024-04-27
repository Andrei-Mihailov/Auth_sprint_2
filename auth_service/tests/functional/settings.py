from os import environ as env
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

load_dotenv(".dev.env")


class TestSettings(BaseSettings):
    SERVICE_HOST: str = Field(default={env.get("SERVICE_HOST")})
    SERVICE_PORT: int = Field(default={env.get("SERVICE_PORT")})

    SU_email: str = Field(default={env.get("SU_email")})
    SU_password: str = Field(default={env.get("SU_password")})

    @property
    def SERVISE_URL(self):
        return f"http://{self.SERVICE_HOST}:{self.SERVICE_PORT}"


test_settings = TestSettings()
