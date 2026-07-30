from json import JSONEncoder
from decimal import Decimal

class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)