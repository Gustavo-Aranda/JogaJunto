from json import jsonEncoder
from decimal import Decimal

class CustomEncoder(jsonEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)