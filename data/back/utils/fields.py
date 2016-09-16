from django.db import models

class NullMixin(object):
    """
        Subclass of the EmailField that allows empty strings to be stored as NULL.
        """
    field_instance = models.CharField
    description = "Field that stores NULL but returns ''."

    def from_db_value(self, value, expression, connection, context):
        """
        Gets value right out of the db and changes it if its ``None``.
        """
        if value is None:
            return ''
        else:
            return value

    def to_python(self, value):
        if isinstance(value, self.field_instance):
            return value
        return value or ''

    def get_prep_value(self, value):
        return value or None


class EmailNullField(NullMixin, models.EmailField):
    """
    Subclass of the CharField that allows empty strings to be stored as NULL.
    """
    description = "Field that stores NULL but returns ''."
    field_instance = models.EmailField


class CharNullField(NullMixin, models.CharField):
    """
    Subclass of the CharField that allows empty strings to be stored as NULL.
    """
    description = "CharField that stores NULL but returns ''."
    field_instance = models.CharField
