from setuptools import find_packages, setup

setup(
    name="cfmgrapi",
    version="2.0.0",
    author="Neil Clack",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask==2",
        "flask-basicauth",
        "flask-sqlalchemy",
        "flask-migrate",
        "flask-marshmallow",
        "marshmallow-sqlalchemy",
        "boto3",
        "psycopg2-binary",
        "gunicorn",
    ],
)
