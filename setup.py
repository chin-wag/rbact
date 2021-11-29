from setuptools import setup
from os import path

desc_file = "README.md"

here = path.abspath(path.dirname(__file__))

with open(desc_file, "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rbact",
    packages=["rbact", "rbact.peewee", "rbact.peewee_async"],
    url="https://github.com/chin-wag/rbact",
    license="MIT",
    author="Svetlana Fedorishcheva",
    author_email="svetlanafedorishcheva99@gmail.com",
    description="Simple RBAC library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "rbac",
        "auth",
        "authorization",
        "access control",
        "permission",
    ],
    extras_require={
        "peewee": ["peewee>=3.14.1"],
        "peewee_async": ["peewee>=3.14.1", "peewee-async>=0.7.2"],
    },
)
