import json
from datetime import datetime
from typing import Any


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder that handles datetime objects"""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def json_dumps(obj: Any) -> str:
    """
    Serialize object to JSON string, handling datetime objects.

    Args:
        obj: The object to serialize

    Returns:
        str: JSON string
    """
    return json.dumps(obj, cls=CustomJSONEncoder)
