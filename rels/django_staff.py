# coding: utf-8

from django.db import models
from django import forms
from django.core.exceptions import ValidationError

from south.modelsinspector import add_introspection_rules

from rels.relations import Record
from rels.shortcuts import EnumWithText

class DjangoEnum(EnumWithText):

    @classmethod
    def _choices(cls):
        return [(record, record.text) for record in cls._records]


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
            return getattr(self._relation, '_index_%s' % self._relation_column)[int(value)]
        except ValueError:
            raise ValidationError(u'can not convert %r to %r' % (value, self._relation))

    def get_prep_value(self, value):
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

    def formfield(self, **kwargs):
        # django 1.4 does not support redifinition of choices field
        # django 1.5 process form_class argument correctly
        from django.utils.text import capfirst

        defaults = {'required': not self.blank,
                    'label': capfirst(self.verbose_name),
                    'help_text': self.help_text}
        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()

        if self.choices:
            # Fields with choices get special treatment.
            include_blank = (self.blank or
                             not (self.has_default() or 'initial' in kwargs))
            defaults['choices'] = self.get_choices(include_blank=include_blank)
            defaults['coerce'] = self.to_python
            if self.null:
                defaults['empty_value'] = None

            #########
            defaults['coerce'] = self._relation._get_from_name
            form_class = forms.TypedChoiceField
            #########

            for k in kwargs.keys():
                if k not in ('coerce', 'empty_value', 'choices', 'required',
                             'widget', 'label', 'initial', 'help_text',
                             'error_messages', 'show_hidden_initial'):
                    del kwargs[k]
        defaults.update(kwargs)
        return form_class(**defaults)


add_introspection_rules([], ["^rels\.django_staff\.TableIntegerField"])
