# coding: utf-8

# TODO: check full mapping of one enum to another (is every value of mapped enum has pair and vice versa)
# TODO: pep8
# TODO: pylint
# TODO: generate docs
# TODO: rewrite exceptions texts & rename exception classes

from rels import exceptions

class Column(object):

    _creation_counter = 0

    def __init__(self,
                 name=None,
                 unique=True,
                 primary=False,
                 external=False,
                 single_type=True,
                 index_name=None,
                 related_name=None):
        '''
        name usually setupped by Table class. In constructor it used in tests
        '''
        self._creation_order = self.__class__._creation_counter
        self.__class__._creation_counter += 1

        self.primary = bool(primary)
        self.unique = bool(unique)

        self.single_type = single_type
        self.name = name
        self.index_name = index_name
        self.related_name = related_name
        self.external = external

    def __repr__(self):
        repr_str = 'Column(name=%(name)r, unique=%(unique)r, primary=%(primary)r, '\
            'single_type=%(single_type)r, index_name=%(index_name)r, related_name=%(related_name)r)'
        return repr_str % self.__dict__

    def initialize(self, name):
        self.name = name

        if self.index_name is None:
            self.index_name = '_index_%s' % self.name

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

    def __init__(self, columns, data, table_class=None):
        self._data = data
        self._primaries = []
        self._table = table_class

        if len(columns) != len(data):
            raise exceptions.ColumnsNumberError(columns, data)

        for column, value in zip(columns, data):
            setattr(self, column.name, value)

            if column.related_name is not None:
                if not hasattr(value, 'set_related_name'):
                    raise exceptions.SetRelatedNameError(value)
                value.set_related_name(column.related_name, self)

    def _add_primary(self, primary_name):
        self._primaries.append(primary_name)

    def set_related_name(self, name, record):
        if hasattr(self, name):
            raise exceptions.DuplicateRelatonNameError(record, name)
        setattr(self, name, record)

    def _set_primary_checks(self, column, ids):
        for id_ in ids:
            attr_name = '_is_%s' % id_
            if hasattr(self, attr_name):
                raise exceptions.DuplicateIsPrimaryError(self, column, attr_name, id_)
            setattr(self, attr_name, id_ == getattr(self, column.name))

    def __repr__(self):
        table_name = self._table.__name__ if self._table is not None else None
        primary_name = self._primaries[0] if self._primaries else None
        return '%(table)s.%(primary)s' % {'table': table_name,
                                          'primary': primary_name}


class _TableMetaclass(type):

    @classmethod
    def process_class_attributes(cls, table_class, bases, attributes):
        table_attributes = {}
        columns = {}
        raw_records = []

        for attr_name, attr_value in attributes.items():
            if attr_name == '_records':
                raw_records = attr_value
            elif isinstance(attr_value, Column):
                attr_value.initialize(name=attr_name)
                columns[attr_name] = attr_value
            else:
                table_attributes[attr_name] = attr_value

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

        records = [Record(columns, record, table_class) for record in raw_records]

        table_attributes['_records'] = tuple(records)
        table_attributes['_raw_records'] = tuple(raw_records)
        table_attributes['_columns'] = columns
        table_attributes['_external_index'] = {}

        return columns, table_attributes, records

    def __new__(cls, name, bases, attributes):

        table_class = super(_TableMetaclass, cls).__new__(cls, name, bases, {})

        columns, table_attributes, records = cls.process_class_attributes(table_class,
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

            duplicates = list(set(attributes.keys()) & set(table_attributes.keys()))
            if duplicates:
                raise exceptions.PrimaryDuplicatesTableAttributeError(duplicates, column.name)

            for record in records:
                record._set_primary_checks(column, attributes.keys())

            for attr_name, record in attributes.items():
                record._add_primary(attr_name)

            table_attributes.update(attributes)

        # create indexes
        for column in columns:
            index = column.get_index(records)

            if column.index_name in table_attributes:
                raise exceptions.IndexDuplicatesTableAttributeError(column.name, column.index_name)

            table_attributes[column.index_name] = index

            if column.external:
                table_attributes['_external_index'] = index

        for attr_name, attr_value in table_attributes.items():
            setattr(table_class, attr_name, attr_value)

        return table_class

    def __call__(self, id_):
        if id_ not in self._external_index:
            raise exceptions.NotExternalValueError(id_)
        return self._external_index[id_]


class Table(object):
    __metaclass__ = _TableMetaclass

    @classmethod
    def _select(cls, *field_names):
        result = []
        for record in cls._records:
            row = tuple(getattr(record, field_name) for field_name in field_names)
            result.append(row)
        return tuple(result)

    @classmethod
    def _get_from_name(cls, name):
        # TODO: write tests
        relation_name, primary_name = name.split('.')

        if relation_name != cls.__name__:
            # TODO: make custom exception
            raise Exception(u'wrong relation name "%s", expected "%s"' % (relation_name, cls.__name__))

        return getattr(cls, primary_name)
