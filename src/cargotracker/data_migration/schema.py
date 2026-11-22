import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.apps import apps


class DataExportError(Exception):
    pass


def model_index():
    return {
        model._meta.db_table: model
        for model in apps.get_models()
        if not model._meta.proxy and not model._meta.auto_created
    }


def field_for_column(model, column):
    for field in model._meta.concrete_fields:
        if column in (field.column, field.name, field.attname):
            return field
    raise DataExportError(f'{model._meta.db_table}: no target column {column!r}')


def timestamp_timezone(mapping):
    zone = (mapping.get('defaults') or {}).get('timestamp_tz', 'UTC')
    try:
        return ZoneInfo(zone)
    except (TypeError, ZoneInfoNotFoundError) as error:
        raise DataExportError(f'unknown timestamp timezone {zone!r}') from error


def format_value(value, timezone):
    if value is None:
        return r'\N'
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            value = value.replace(tzinfo=timezone)
        return value.astimezone(datetime.UTC).isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)
