# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.core.exceptions import ValidationError

from south.modelsinspector import add_introspection_rules

from rels.relations import Record
from rels.shortcuts import EnumWithText

class DjangoEnum(EnumWithText):

    @classmethod
    def choices(cls):
        return [(record, record.text) for record in cls.records]


class TableIntegerField(models.IntegerField):

    __metaclass__ = models.SubfieldBase

    def __init__(self, *argv, **kwargs):
        self._relation = kwargs.get('relation')
        self._relation_column = kwargs.get('relation_column', 'value')

        if 'choices' not in kwargs and hasattr(self._relation, 'choices'):
            kwargs['choices'] = self._relation.choices()

        # TODO: check if relation has column with relation_column name
        # TODO: check if column has int type

        if 'relation' in kwargs: del kwargs['relation']
        if 'relation_column' in kwargs: del kwargs['relation_column']

        super(TableIntegerField, self).__init__(*argv, **kwargs)

    def to_python(self, value):
        if self._relation is None:
            # emulate default behaviour for south
            return super(TableIntegerField, self).to_python(value)

        if value is None:
            return None

        if isinstance(value, Record):
            if value._table == self._relation:
                return value
            else:
                raise ValidationError(u'record %r is not from %r' % (value, self._relation))

        if isinstance(value, basestring) and '.' in value:
            relation_name, primary_name = value.split('.')

            if relation_name != self._relation.__name__:
                raise ValidationError(u'wrong relation name "%s", expected "%s"' % (relation_name, self._relation.__name__))

            return getattr(self._relation, primary_name)

        try:
            return getattr(self._relation, 'index_%s' % self._relation_column)[int(value)]
        except ValueError:
            raise ValidationError(u'can not convert %r to %r' % (value, self._relation))

    def get_prep_value(self, value):
        if self._relation is None:
            # emulate default behaviour for south
            return super(TableIntegerField, self).get_prep_value(value)

        if isinstance(value, Record):
            if value._table == self._relation:
                return getattr(value, self._relation_column)
            else:
                # TODO: change exception type
                raise ValidationError(u'record %r is not from %r' % (value, self._relation))

        if isinstance(value, basestring) and '.' in value:
            relation_name, primary_name = value.split('.')

            if relation_name != self._relation.__name__:
                # TODO: change exception type
                raise ValidationError(u'wrong relation name "%s", expected "%s"' % (relation_name, self._relation.__name__))

            return getattr(getattr(self._relation, primary_name), self._relation_column)

        return value


add_introspection_rules([], ["^rels\.django_staff\.TableIntegerField"])
