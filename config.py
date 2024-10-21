import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        for key, value in os.environ.items():
            self.__setattr__(key, self._convert_type(value))

    @staticmethod
    def _convert_type(value):
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value