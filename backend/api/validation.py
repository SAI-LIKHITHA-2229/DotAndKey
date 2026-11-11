from flask import request


def json_body():
    """The request's JSON object, or {} if the body is missing or not an object.

    Treating a list, string or number body as empty means the normal
    validation answers with a clear 400 instead of the code crashing.
    """
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _storable(text):
    """Remove what PostgreSQL text cannot hold: NUL characters and broken Unicode."""
    return text.replace("\x00", "").encode("utf-8", "ignore").decode("utf-8")


def text_field(data, key):
    """A stripped string field, or "" if it is missing or not a string."""
    value = data.get(key)
    return _storable(value).strip() if isinstance(value, str) else ""


def raw_text_field(data, key):
    """Like text_field but keeps surrounding spaces (for passwords)."""
    value = data.get(key)
    return _storable(value) if isinstance(value, str) else ""
