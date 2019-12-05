# coding: utf-8


from django.db import models
from django.utils import functional
from django.core.exceptions import ValidationError
from django.core import validators as django_validators

from rels.relations import Record
from rels.shortcuts import EnumWithText


class DjangoEnum(EnumWithText):

    @classmethod
    def choices(cls):
        return [(record, record.text) for record in cls.records]


class RelationIntegerField(models.IntegerField):

    def __init__(self, *argv, **kwargs):
        self._relation = kwargs.get('relation')
        self._relation_column = kwargs.get('relation_column', 'value')

        if 'choices' not in kwargs and hasattr(self._relation, 'choices'):
            kwargs['choices'] = self._relation.choices()

        # TODO: check if relation has column with relation_column name
        # TODO: check if column has int type

        if 'relation' in kwargs: del kwargs['relation']
        if 'relation_column' in kwargs: del kwargs['relation_column']

        super(RelationIntegerField, self).__init__(*argv, **kwargs)

    def to_python(self, value):
        if self._relation is None:
            # emulate default behaviour for migrations
            return super(RelationIntegerField, self).to_python(value)

        if value is None:
            return None

        if isinstance(value, Record):
            if value._relation == self._relation:
                return value
            else:
                raise ValidationError('record %r is not from %r' % (value, self._relation))

        if isinstance(value, str) and '.' in value:
            relation_name, primary_name = value.split('.')

            if relation_name != self._relation.__name__:
                raise ValidationError('wrong relation name "%s", expected "%s"' % (relation_name, self._relation.__name__))

            return getattr(self._relation, primary_name)

        try:
            return getattr(self._relation, 'index_%s' % self._relation_column)[int(value)]
        except ValueError:
            raise ValidationError('can not convert %r to %r' % (value, self._relation))

    def get_prep_value(self, value):
        if self._relation is None:
            # emulate default behaviour for migrations
            return super(RelationIntegerField, self).get_prep_value(value)

        if isinstance(value, Record):
            if value._relation == self._relation:
                return getattr(value, self._relation_column)
            else:
                # TODO: change exception type
                raise ValidationError('record %r is not from %r' % (value, self._relation))

        if isinstance(value, str) and '.' in value:
            relation_name, primary_name = value.split('.')

            if relation_name != self._relation.__name__:
                # TODO: change exception type
                raise ValidationError('wrong relation name "%s", expected "%s"' % (relation_name, self._relation.__name__))

            return getattr(getattr(self._relation, primary_name), self._relation_column)

        return value

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def deconstruct(self):
        name, path, args, kwargs = super(RelationIntegerField, self).deconstruct()
        if 'choices' in kwargs:
            del kwargs['choices']
        return name, path, args, kwargs

    @functional.cached_property
    def validators(self):
        validators = super(RelationIntegerField, self).validators

        # remove unnecessary validators
        validators = [validator
                      for validator in validators
                      if not isinstance(validator, (django_validators.MinValueValidator, django_validators.MaxValueValidator))]

        return validators
