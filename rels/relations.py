# coding: utf-8

# TODO: check full mapping of one enum to another (is every value of mapped enum has pair and vice versa)
# TODO: pep8
# TODO: pylint
# TODO: generate docs
# TODO: rewrite exceptions texts & rename exception classes
import random

from rels import exceptions

class Column(object):
    __slots__ = ('_creation_order', 'primary', 'unique', 'single_type', 'name', 'index_name', 'no_index', 'related_name', 'external', 'primary_checks')

    _creation_counter = 0

    def __init__(self,
                 name=None,
                 unique=True,
                 primary=False,
                 external=False,
                 single_type=True,
                 index_name=None,
                 no_index=True,
                 related_name=None,
                 primary_checks=False):
        '''
        name usually setupped by Relation class. In constructor it used in tests
        '''
        self._creation_order = self.__class__._creation_counter
        self.__class__._creation_counter += 1

        self.primary = bool(primary)
        self.unique = bool(unique)

        self.single_type = single_type
        self.name = name
        self.index_name = index_name
        self.no_index = no_index
        self.related_name = related_name
        self.external = external
        self.primary_checks = primary_checks

    def __repr__(self):
        repr_str = 'Column(name=%(name)r, unique=%(unique)r, primary=%(primary)r, '\
            'single_type=%(single_type)r, index_name=%(index_name)r, related_name=%(related_name)r)'
        return repr_str % self.__dict__

    def initialize(self, name):
        self.name = name

        if self.index_name is None:
            self.index_name = 'index_%s' % self.name

        if self.primary and not self.unique:
            raise exceptions.PrimaryWithoutUniqueError(self.name)

        if self.external and not self.unique:
            raise exceptions.ExternalWithoutUniqueError(self.name)

    def check_uniqueness_restriction(self, records):
        if not self.unique: return

        values = set()

        for record in records:
            value = getattr(record, self.name)

            if value in values:
                raise exceptions.DuplicateValueError(self.name, value)

            values.add(value)

    def check_single_type_restriction(self, records):
        if not self.single_type: return

        if not records: return

        expected_type = getattr(records[0], self.name).__class__

        for record in records:
            value_type = getattr(record, self.name).__class__
            if expected_type != value_type:
                raise exceptions.SingleTypeError(self.name)

    def get_primary_attributes(self, records):
        if not records: return {}
        return { getattr(record, self.name):record for record in records}

    def get_index(self, records):

        index = {}

        if self.unique:
            for record in records:
                index[getattr(record, self.name)] = record
        else:
            for record in records:
                value = getattr(record, self.name)
                # save declaration order
                index[value] = index.get(value, []) + [record]

            index = { k:tuple(v) for k, v in index.items()}

        return index


class Record(object):

    def __init__(self, columns, data, relation_class=None):
        self._primaries = []
        self._relation = relation_class

        if len(columns) != len(data):
            raise exceptions.ColumnsNumberError(columns, data)

        for column, value in zip(columns, data):
            setattr(self, column.name, value)

            if column.related_name is not None:
                if not hasattr(value, 'set_related_name'):
                    raise exceptions.SetRelatedNameError(value)
                value.set_related_name(column.related_name, self)

    def __getattr__(self, name):
        if name.startswith('is_'):
            return getattr(self._relation, name[3:]) is self

        return getattr(super(), name)

    def _add_primary(self, primary_name):
        self._primaries.append(primary_name)

    def set_related_name(self, name, record):
        if hasattr(self, name):
            raise exceptions.DuplicateRelatonNameError(record, name)
        setattr(self, name, record)

    def _set_primary_checks(self, column, ids):
        if not column.primary_checks:
            return

        for id_ in ids:
            attr_name = 'is_%s' % id_
            if hasattr(self, attr_name):
                raise exceptions.DuplicateIsPrimaryError(self, column, attr_name, id_)
            setattr(self, attr_name, id_ == getattr(self, column.name))

    def __repr__(self):
        relation_name = self._relation.__name__ if self._relation is not None else None
        primary_name = self._primaries[0] if self._primaries else None
        return '%(relation)s.%(primary)s' % {'relation': relation_name,
                                             'primary': primary_name}

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


class _RelationMetaclass(type):

    @classmethod
    def process_class_attributes(cls, relation_class, bases, attributes):
        relation_attributes = {}
        columns = {}
        raw_records = []

        for attr_name, attr_value in attributes.items():
            if attr_name == 'records':
                raw_records = attr_value
            elif isinstance(attr_value, Column):
                attr_value.initialize(name=attr_name)
                columns[attr_name] = attr_value
            else:
                relation_attributes[attr_name] = attr_value

        for base in bases:
            if hasattr(base, '_columns'):
                for column in base._columns:
                    if column.name not in columns:
                        columns[column.name] = column
            if hasattr(base, '_raw_records'):
                raw_records = list(base._raw_records) + list(raw_records)

        columns = sorted(columns.values(), key=lambda c: c._creation_order)

        external_columns = [column for column in columns if column.external]
        if len(external_columns) > 1:
            raise exceptions.MultipleExternalColumnsError(external_columns)

        records = [Record(columns, record, relation_class) for record in raw_records]

        relation_attributes['records'] = tuple(records)
        relation_attributes['_raw_records'] = tuple(raw_records)
        relation_attributes['_columns'] = columns
        relation_attributes['_external_index'] = {}

        return columns, relation_attributes, records

    def __new__(cls, name, bases, attributes):

        relation_class = super(_RelationMetaclass, cls).__new__(cls, name, bases, {})

        columns, relation_attributes, records = cls.process_class_attributes(relation_class,
                                                                          bases,
                                                                          attributes)

        for column in columns:
            column.check_uniqueness_restriction(records)
            column.check_single_type_restriction(records)

        # create primaries
        for column in columns:
            if not column.primary:
                continue
            attributes = column.get_primary_attributes(records)

            duplicates = list(set(attributes.keys()) & set(relation_attributes.keys()))
            if duplicates:
                raise exceptions.PrimaryDuplicatesRelationAttributeError(duplicates, column.name)

            for record in records:
                record._set_primary_checks(column, list(attributes.keys()))

            for attr_name, record in attributes.items():
                record._add_primary(attr_name)

            relation_attributes.update(attributes)

        # create indexes
        for column in columns:
            index = None

            if not column.no_index or column.external:
                index = column.get_index(records)

                if column.index_name in relation_attributes:
                    raise exceptions.IndexDuplicatesRelationAttributeError(column.name, column.index_name)

                relation_attributes[column.index_name] = index

                if column.external:
                    relation_attributes['_external_index'] = index

        for attr_name, attr_value in relation_attributes.items():
            setattr(relation_class, attr_name, attr_value)

        return relation_class

    def __call__(self, id_):
        if id_ not in self._external_index:
            raise exceptions.NotExternalValueError(id_)
        return self._external_index[id_]

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self



class Relation(object, metaclass=_RelationMetaclass):

    @classmethod
    def select(cls, *field_names):
        result = []
        for record in cls.records:
            row = tuple(getattr(record, field_name) for field_name in field_names)
            result.append(row)
        return tuple(result)

    @classmethod
    def random(cls, exclude=()):
        return random.choice([record for record in cls.records if record not in exclude])

    @classmethod
    def get_from_name(cls, name):
        # TODO: write tests
        relation_name, primary_name = name.split('.')

        if relation_name != cls.__name__:
            raise exceptions.WrongRelationNameError(relation_name=relation_name, enum_name=cls.__name__)

        return getattr(cls, primary_name)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self
