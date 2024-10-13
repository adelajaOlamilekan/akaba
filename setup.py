from setuptools import setup, find_packages

setup(
    name='akaba',  # Name of your CLI tool
    version='1.0.1',
    description="This is a CLI scaffolding tool for FastAPI. It helps create a project structure template with boilerplate code",
    py_modules=['akaba'],  # Name of the Python file without the .py extension
    packages=find_packages(),
    install_requires=[
        'Click',  # Required dependency for Click CLI
        'pydantic-settings',  # Required dependency for config settings
        'FastAPI',  # Required dependency for FastAPI
        'SQLAlchemy',  # Required dependency for database operations
        'alembic',  # Required for database migrations
        'pydantic',  # Required for data validation
    ],
    entry_points='''
        [console_scripts]
        akaba=akaba:create_project_structure
    ''',
)
