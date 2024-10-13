import click
from pathlib import Path
import subprocess

@click.command()
@click.option("--project_foldername", default=Path(__file__).parents[1], help="Path to the project folder")

def create_project_structure(project_foldername):
    project_foldername =Path(project_foldername)
    app_folder = Path(project_foldername).joinpath("app")
    test_folder = Path(project_foldername).joinpath("test")
    backend_folder= app_folder.joinpath("backend")
    external_services_folder=  app_folder.joinpath("external_services")
    schemas_folder= app_folder.joinpath("schemas")
    utils_folder= app_folder.joinpath("utils")
    cruds_folder= app_folder.joinpath("cruds")
    models_folder= app_folder.joinpath("models")
    routes_folder= app_folder.joinpath("routes")
    services_folder= app_folder.joinpath("services")
    
    folders = {
                project_foldername: "project", app_folder: "app", 
                test_folder:"test", backend_folder:"backend",
                external_services_folder:"external_services", schemas_folder: "schemas",
                utils_folder: "utils", cruds_folder: "cruds", models_folder: "models",
                routes_folder: "routes", services_folder:"services"
            }

    for folder, folder_name in folders.items():
        if not folder.exists():
            Path.mkdir(folder)
        else:
            click.echo(f"{folder_name} folder exists already in the project")

    #Create boilerplate files 
    # Boilerplate for config
    config_code= """\
from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import field_validator, ValidationInfo
from pathlib import Path
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    BASE_DIR : str = str(Path(__file__).parents[2])
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    @lru_cache
    def create_db_url(cls, v: Optional[str], values: ValidationInfo):
        return (
            f"sqlite:///{values.data["BASE_DIR"]}/app.db"
        )
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", str_to_lower=True)


settings = Settings()
"""

    config_file = backend_folder.joinpath("config.py") 
    dependencies_file = backend_folder.joinpath("dependencies.py")
    init_file = backend_folder.joinpath("__init__.py")

    with open(file=config_file, mode='w') as file:
        file.write(config_code)

    with open(file=dependencies_file, mode='w') as file:
        file.write("")

    with open(file=init_file, mode="w") as file:
        file.write("")

    model_init_code = """\
from sqlalchemy.orm import declarative_base

Base = declarative_base()

"""

    base_model_code = """\
from app.models import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.backend.config import settings

engine = create_engine(settings.DATABASE_URL)
session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
"""
    base_model_file = models_folder.joinpath("base.py") 
    model_init_file = models_folder.joinpath("__init__.py")

    with open(file=model_init_file, mode='w') as file:
        file.write(model_init_code)

    with open(file=base_model_file, mode='w') as file:
        file.write(base_model_code)

    project_setup_commands = f"""\
    cd {project_foldername};
    python -m venv venv; 
    source ./venv/bin/activate
    pip install fastapi; pip install uvicorn;
    pip install sqlalchemy; pip install alembic; pip install pydantic-settings
    alembic init alembic
    pip freeze > requirements.txt
    """

    venv_result = subprocess.run(project_setup_commands, shell=True, capture_output=True)

    alembic_env_file = project_foldername.joinpath("alembic/env.py")

    lines = []

    with open(alembic_env_file, 'r') as file:
        lines = file.readlines()
    
    for line_number, line in enumerate(lines):
        if line == "config = context.config\n":
            lines.insert(line_number+1, """from app.backend.config import settings\n""")
            lines.insert(line_number+2, """config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)\n""")
        if line == "target_metadata = None\n":
            lines[line_number] = "#target_metadata = None\n"
            lines.insert(line_number+1, """from app.models.base import Base\n""")
            lines.insert(line_number+2, """target_metadata=Base.metadata\n""")
    
    with open(alembic_env_file, 'w') as file:
        file.writelines(lines)

if __name__== "__main__":
    create_project_structure()