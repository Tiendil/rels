# coding: utf-8

class RelsException(Exception): pass
class ColumnException(RelsException): pass
class RecordException(RelsException): pass
class RelationException(RelsException): pass

class PrimaryWithoutUniqueError(ColumnException):
    def __init__(self, column_name):
        message = 'Primary column "%s" MUST has unique restriction' % column_name
        super(PrimaryWithoutUniqueError, self).__init__(message)

class ExternalWithoutUniqueError(ColumnException):
    def __init__(self, column_name):
        message = 'External column "%s" MUST has unique restriction' % column_name
        super(ExternalWithoutUniqueError, self).__init__(message)

class DuplicateValueError(ColumnException):
    def __init__(self, column_name, value):
        message = 'Duplicate value "%s" in column "%s"' % (value, column_name)
        super(DuplicateValueError, self).__init__(message)

class SingleTypeError(ColumnException):
    def __init__(self, column_name):
        message = 'Column "%s" MUST contain values of one type' % (column_name)
        super(SingleTypeError, self).__init__(message)

class ColumnsNumberError(RecordException):
    def __init__(self, columns, data):
        message = 'Wrong columns number in record: %s (expected: %d)' % (data, len(columns))
        super(ColumnsNumberError, self).__init__(message)

class SetRelatedNameError(RecordException):
    def __init__(self, object):
        message = ('Can not set related name for object %r, it has no method "set_related_name"'
                   % object)
        super(SetRelatedNameError, self).__init__(message)

class DuplicateRelatonNameError(RecordException):
    def __init__(self, record, name):
        message = 'Can not set related name for record %s, it has already had attribute with name "%s"' % (record, name)
        super(DuplicateRelatonNameError, self).__init__(message)

class DuplicateIsPrimaryError(RecordException):
    def __init__(self, record, column, attr_name, primary_name):
        message = ('record %(record)s attribute %(attr_name)s of column %(column_name)s duplicates another record attribute (probably, column with name "%(primary_name)s")' %
        {'attr_name': attr_name,
         'record': record,
         'column_name': column.name,
         'primary_name': primary_name})
        super(DuplicateIsPrimaryError, self).__init__(message)

class PrimaryDuplicatesRelationAttributeError(RelationException):
    def __init__(self, column_name, duplicates):
        message = 'Primary names "%(duplicates)r" of column "%(column)s" duplicate another table attributes' % {'duplicates': duplicates, 'column': column_name}
        super(PrimaryDuplicatesRelationAttributeError, self).__init__(message)

class IndexDuplicatesRelationAttributeError(RelationException):
    def __init__(self, column_name, index_name):
        message = ('Index name "%s" of column "%s" duplicates another table attribute'
                   % (index_name, column_name))
        super(IndexDuplicatesRelationAttributeError, self).__init__(message)

class NotExternalValueError(RelationException):
    def __init__(self, id_):
        message = '"%(id)s" is not external value' % {'id': id_}
        super(NotExternalValueError, self).__init__(message)

class MultipleExternalColumnsError(RelationException):
    def __init__(self, external_columns):
        message = ('there are more then 1 external column: %s' %
                   ', '.join(column.name for column in external_columns))
        super(MultipleExternalColumnsError, self).__init__(message)


class WrongRelationNameError(RelationException):

    def __init__(self, relation_name, enum_name):
        message = 'wrong relation name "%s", expected enum name: "%s"' % (relation_name, enum_name)
        super(WrongRelationNameError, self).__init__(message)
