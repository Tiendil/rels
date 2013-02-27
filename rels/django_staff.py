# coding: utf-8

from django.db import models
from django.core.exceptions import ValidationError

from south.modelsinspector import add_introspection_rules

from rels.relations import Record


class TableIntegerField(models.IntegerField):

    __metaclass__ = models.SubfieldBase

    def __init__(self, *argv, **kwargs):
        self._relation = kwargs.get('relation')
        self._relation_column = kwargs.get('relation_column')

        if 'choices' not in kwargs and hasattr(self._relation, '_choices'):
            kwargs['choices'] = self._relation._choices()

        # TODO: check if relation has column with relation_column name
        # TODO: check if column has int type

        if self._relation: del kwargs['relation']
        if self._relation_column: del kwargs['relation_column']

        super(TableIntegerField, self).__init__(*argv, **kwargs)

    def to_python(self, value):
        if isinstance(value, Record):
            if isinstance(value._table, self._relation):
                return value
            else:
                raise ValidationError(u'record %r is not from %r' % (value, self._relation))

        try:
            return getattr(self._relation, '_index_%s' % self._relation_column)[int(value)]
        except ValueError:
            raise ValidationError(u'can not convert %r to %r' % (value, self._relation))

    def get_prep_value(self, value):
        return getattr(value, self._relation_column)


add_introspection_rules([], ["^rels\.django_staff\.TableIntegerField"])
