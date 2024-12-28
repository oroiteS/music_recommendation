# config.py
import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             'mssql+pymssql://sa:yyk200412=@localhost:1433/python_final')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
