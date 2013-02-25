# coding: utf-8

from unittest import TestCase

from rels.relations import Table, Column, Record

from rels import exceptions

from rels.shortcuts import Enum, EnumWithText

class EmptyTable(Table):
    pass

# just to test, that empy records does not break class costruction
class EmptyRecordsTable(Table):
    name = Column()
    value = Column()


class SimplestTable(Table):
    name = Column()
    value = Column()

    _records = (('name_a', 1),
                ('name_b', 2))


class SimplestEnum(Table):
    name = Column(primary=True)
    value = Column(external=True)

    _records = ( ('state_1', 'val_1'),
                 ('state_2', 'val_2') )

class EnumWith2Primaries(Table):

    name = Column(primary=True)
    value = Column(primary=True)

    _records = ( ('STATE_1', 'value_1'),
                 ('STATE_2', 'value_2') )

class IndexesTable(Table):
    name = Column(primary=True)
    val_1 = Column()
    val_2 = Column(unique=False)
    val_3 = Column(index_name='val_3_index')

    _records = ( ('rec_1', 'val_1_1', 'val_2_1', 'val_3_1'),
                 ('rec_2', 'val_1_2', 'val_2_2', 'val_3_2'),
                 ('rec_3', 'val_1_3', 'val_2_2', 'val_3_3'),
                 ('rec_4', 'val_1_4', 'val_2_4', 'val_3_4'),)

class RelationDestinationTable(Table):
    name = Column(primary=True)
    val_1 = Column()

    _records = ( ('STATE_1', 'value_1'),
                 ('STATE_2', 'value_2') )

class RelationSourceTable(Table):
    name = Column(primary=True)
    val_1 = Column()
    rel = Column(related_name='rel_source')

    _records = ( ('STATE_1', 'value_1', RelationDestinationTable.STATE_1),
                 ('STATE_2', 'value_2', RelationDestinationTable.STATE_2) )

class ShortcutEnum(Enum):
    _records = ( ('ID_1', 1),
                 ('ID_2', 2) )

class ShortcutEnumWithText(EnumWithText):
    _records = ( ('ID_1', 1, u'verbose name 1'),
                 ('ID_2', 2, u'verbose name 2') )



class SimpleColumnTests(TestCase):

    def test_default_index_name(self):
        column = Column()
        column.initialize(name='test')
        self.assertEqual(column.index_name, '_index_test')

    def test_custom_index_name(self):
        column = Column(index_name='my_index')
        column.initialize(name='test')
        self.assertEqual(column.index_name, 'my_index')

    def test_check_uniqueness_restriction_success(self):
        column_1 = Column()
        column_1.initialize('column_1')

        records = ( Record([column_1], ['uuid_1']),
                    Record([column_1], ['uuid_2']))

        column_1.check_uniqueness_restriction(records)

    def test_primary_without_unique(self):
        column = Column(primary=True, unique=False)
        self.assertRaises(exceptions.PrimaryWithoutUniqueError, column.initialize, name='column')

    def test_external_without_unique(self):
        column = Column(external=True, unique=False)
        self.assertRaises(exceptions.ExternalWithoutUniqueError, column.initialize, name='column')

    def test_check_uniqueness_restriction_exception(self):
        column_1 = Column()
        column_1.initialize('column_1')

        records = ( Record([column_1], ['uuid_1']),
                    Record([column_1], ['uuid_1']))

        self.assertRaises(exceptions.DuplicateValueError,
                          column_1.check_uniqueness_restriction, records)

    def test_check_single_type_restriction_success(self):
        column_1 = Column()
        column_1.initialize('column_1')

        records = ( Record([column_1], ['str_1']),
                    Record([column_1], ['str_2']))

        column_1.check_single_type_restriction(records)

    def test_check_single_type_restriction_exception(self):
        column_1 = Column()
        column_1.initialize('column_1')

        records = ( Record([column_1], [1]),
                    Record([column_1], ['str_2']))

        self.assertRaises(exceptions.SingleTypeError,
                          column_1.check_single_type_restriction, records)

    def test_get_index_unique(self):
        column_1 = Column()
        column_1.initialize('column_1')

        records = ( Record([column_1], ['str_1']),
                    Record([column_1], ['str_2']))

        self.assertEqual(column_1.get_index(records), {'str_1': records[0],
                                                       'str_2': records[1]})

    def test_get_index_not_unique(self):
        column_1 = Column(unique=False)
        column_1.initialize('column_1')

        records = ( Record([column_1], ['str_1']),
                    Record([column_1], ['str_2']))

        self.assertEqual(column_1.get_index(records), {'str_1': (records[0], ),
                                                       'str_2': (records[1], )})

    def test_repr(self):
        column = Column(related_name='rel_name')
        column.initialize(name='col_name')

        column._creation_order += 1 # enshure, that creation order will be equal
        self.assertEqual(eval(repr(column)).__dict__, column.__dict__)


class SimpleRecordTests(TestCase):

    def test_wrong_data_length(self):
        columns = (Column(name='col_1'), Column(name='col_2'))
        data = (1, 2, 3)
        self.assertRaises(exceptions.ColumnsNumberError, Record, columns=columns, data=data)

    def test_columns_values(self):
        columns = (Column(name='col_1'), Column(name='col_2'))
        data = (1, 2)
        r = Record(columns=columns, data=data)
        self.assertEqual(r.col_1, 1)
        self.assertEqual(r.col_2, 2)

    def test_equality(self):
        columns = (Column(name='col_1'), Column(name='col_2'))
        data = (1, 2)
        r_1 = Record(columns=columns, data=data)
        r_2 = Record(columns=columns, data=data)
        self.assertNotEqual(r_1, r_2)
        self.assertEqual(r_1, r_1)

    def test_repr(self):
        self.assertEqual(repr(RelationDestinationTable._records[0]),
                         'RelationDestinationTable.STATE_1')


class SimpleTableTests(TestCase):

    def setUp(self):
        pass

    def test_empy_table(self):
        self.assertEqual(EmptyTable._records, tuple())

    def test_simplest_table(self):
        self.assertEqual(len(SimplestTable._records), 2)
        self.assertEqual(SimplestTable._raw_records, (('name_a', 1),
                                                      ('name_b', 2)))

    def test_uniqueness_restriction(self):
        def create_bad_table():
            class SimplestTable(Table):
                name = Column()
                value = Column(unique=True)

                _records = (('name_a', 1),
                            ('name_b', 1))

        self.assertRaises(exceptions.DuplicateValueError, create_bad_table)

    def test_primary_uniqueness_restriction(self):
        def create_bad_table():
            class SimplestTable(Table):
                name = Column(primary=True, unique=False)
                value = Column()

                _records = (('name_a', 1),
                            ('name_b', 1))

        self.assertRaises(exceptions.PrimaryWithoutUniqueError, create_bad_table)


    def test_simplest_enum_attributes(self):
        self.assertEqual(SimplestEnum.state_1.value, 'val_1')
        self.assertEqual(SimplestEnum.state_1.name, 'state_1')
        self.assertEqual(SimplestEnum.state_2.value, 'val_2')
        self.assertEqual(SimplestEnum.state_2.name, 'state_2')

    def test_primary_attributes_setupped(self):
        self.assertEqual(SimplestEnum._records, (SimplestEnum.state_1, SimplestEnum.state_2))

    def test_only_primary_attributes_setupped(self):
        self.assertFalse(hasattr(SimplestEnum, 'val_1'))
        self.assertFalse(hasattr(SimplestEnum, 'val_2'))

    def test_records_check_attributes_setupped(self):
        self.assertTrue(SimplestEnum.state_1._is_state_1)
        self.assertFalse(SimplestEnum.state_1._is_state_2)
        self.assertFalse(SimplestEnum.state_2._is_state_1)
        self.assertTrue(SimplestEnum.state_2._is_state_2)

        self.assertFalse(hasattr(SimplestEnum.state_1, '_is_val_1'))
        self.assertFalse(hasattr(SimplestEnum.state_1, '_is_val_2'))
        self.assertFalse(hasattr(SimplestEnum.state_2, '_is_val_1'))
        self.assertFalse(hasattr(SimplestEnum.state_2, '_is_val_2'))

    def test_get_record_by_not_external_id(self):
        self.assertRaises(exceptions.NotExternalValueError, SimplestEnum, 'bla-bla')

    def test_more_then_1_external_columns(self):
        def create_bad_table():
            class SimplestTable(Table):
                name = Column(external=True)
                value = Column(external=True)

                _records = (('name_a', 'name_c'),
                            ('name_b', 'name_d'))

        self.assertRaises(exceptions.MultipleExternalColumnsError, create_bad_table)

    def test_get_record_by_external_id(self):
        self.assertEqual(SimplestEnum('val_1'), SimplestEnum.state_1)
        self.assertEqual(SimplestEnum('val_2'), SimplestEnum.state_2)

    def test_simplest_enum_attributes_with_2_primaries(self):
        self.assertEqual(EnumWith2Primaries.STATE_1.value, 'value_1')
        self.assertEqual(EnumWith2Primaries.STATE_1.name, 'STATE_1')
        self.assertEqual(EnumWith2Primaries.STATE_2.value, 'value_2')
        self.assertEqual(EnumWith2Primaries.STATE_2.name, 'STATE_2')

        self.assertEqual(EnumWith2Primaries.STATE_1,
                         EnumWith2Primaries.value_1)

        self.assertEqual(EnumWith2Primaries.STATE_2,
                         EnumWith2Primaries.value_2)

        self.assertEqual(EnumWith2Primaries._records,
                         (EnumWith2Primaries.STATE_1,
                          EnumWith2Primaries.STATE_2))

    def test_primary_name_duplicate_another_table_attribute(self):
        def create_bad_table():
            class SimplestTable(Table):
                name = Column(primary=True)
                value = Column(primary=True)

                _records = (('name_a', 'name_c'),
                            ('name_b', 'name_a'))

        self.assertRaises(exceptions.PrimaryDuplicatesTableAttributeError, create_bad_table)

    def test_primary_name_duplicate_another_record_attribute(self):
        def create_bad_table():
            class SimplestTable(Table):
                name = Column(primary=True)
                _is_name = Column(primary=True)

                _records = (('name_a', 'name_c'),
                            ('name_b', 'name'))

        self.assertRaises(exceptions.DuplicateIsPrimaryError, create_bad_table)


    def test_simplest_indexes(self):
        self.assertEqual(IndexesTable._index_name,
                         {'rec_1': IndexesTable.rec_1,
                          'rec_2': IndexesTable.rec_2,
                          'rec_3': IndexesTable.rec_3,
                          'rec_4': IndexesTable.rec_4 })

        self.assertEqual(IndexesTable._index_val_1,
                         {'val_1_1': IndexesTable.rec_1,
                          'val_1_2': IndexesTable.rec_2,
                          'val_1_3': IndexesTable.rec_3,
                          'val_1_4': IndexesTable.rec_4 })

        self.assertEqual(IndexesTable._index_val_2,
                         {'val_2_1': (IndexesTable.rec_1,),
                          'val_2_2': (IndexesTable.rec_2, IndexesTable.rec_3),
                          'val_2_4': (IndexesTable.rec_4,) })

        self.assertEqual(IndexesTable.val_3_index,
                         {'val_3_1': IndexesTable.rec_1,
                          'val_3_2': IndexesTable.rec_2,
                          'val_3_3': IndexesTable.rec_3,
                          'val_3_4': IndexesTable.rec_4 })

    def test_index_duplicate_another_table_attribute(self):
        def create_bad_table():
            class SimplestTable(Table):
                name = Column(primary=True, index_name='name_a')
                value = Column()

                _records = (('name_a', 1),
                            ('name_b', 2))

        self.assertRaises(exceptions.IndexDuplicatesTableAttributeError, create_bad_table)

    def test_relations_setup(self):
        self.assertEqual(RelationSourceTable.STATE_1, RelationDestinationTable.STATE_1.rel_source)
        self.assertEqual(RelationSourceTable.STATE_2, RelationDestinationTable.STATE_2.rel_source)
        self.assertEqual(RelationSourceTable.STATE_1.rel, RelationDestinationTable.STATE_1)
        self.assertEqual(RelationSourceTable.STATE_2.rel, RelationDestinationTable.STATE_2)
        self.assertEqual(RelationSourceTable.STATE_1, RelationSourceTable.STATE_1.rel.rel_source)
        self.assertEqual(RelationSourceTable.STATE_2, RelationSourceTable.STATE_2.rel.rel_source)

    def test_relations_setup_without_set_method(self):
        def create_bad_table():
            class RelationSourceTable(Table):
                name = Column(primary=True)
                val_1 = Column()
                rel = Column(related_name='rel_source')

                _records = ( ('STATE_1', 'value_1', 1), # just any type without .set_related_name
                             ('STATE_2', 'value_2', RelationDestinationTable.STATE_2) )

        self.assertRaises(exceptions.SetRelatedNameError, create_bad_table)

    def test_relations_setup_duplicate_name_error(self):
        def create_bad_table():
            class RelationSourceTable(Table):
                name = Column(primary=True)
                val_1 = Column()
                rel = Column(related_name='rel_source')

                # "name" duplicate primary attribute of RelationDestinationTable
                _records = ( ('name', 'value_1', RelationDestinationTable.STATE_1),
                             ('STATE_2', 'value_2', RelationDestinationTable.STATE_2) )

        self.assertRaises(exceptions.DuplicateRelatonNameError, create_bad_table)

    def test_table_inheritance(self):
        class BaseTable(Table):
            name = Column(primary=True)
            value = Column()

        class ChildTable(BaseTable):
            _records = (('id_1', 1),
                        ('id_2', 2))

        self.assertEqual(ChildTable.id_1.name, 'id_1')
        self.assertEqual(ChildTable.id_2.name, 'id_2')

    def test_column_redifinition(self):
        class BaseTable(Table):
            name = Column(primary=True)
            value = Column()

        class ChildTable(BaseTable):
            value = Column(unique=False)
            _records = (('id_1', 1),
                        ('id_2', 1))

        self.assertEqual(ChildTable._index_value, {1: ChildTable._records})

    def test_table_inheritance_with_records(self):
        class BaseTable(Table):
            name = Column(primary=True)
            value = Column()
            _records = (('id_0', 0),)

        class ChildTable(BaseTable):
            value = Column(unique=False)
            _records = (('id_1', 1),
                        ('id_2', 2))

        self.assertEqual(ChildTable.id_0.name, 'id_0')
        self.assertEqual(ChildTable.id_1.name, 'id_1')
        self.assertEqual(ChildTable.id_2.name, 'id_2')

        self.assertEqual(len(ChildTable._records), 3)
        self.assertEqual(ChildTable._raw_records, (('id_0', 0),
                                                   ('id_1', 1),
                                                   ('id_2', 2),))

        self.assertRaises(AttributeError, getattr, BaseTable, 'id_1')

        self.assertEqual(len(BaseTable._index_name), 1)
        self.assertEqual(len(ChildTable._index_name), 3)


    def test_shortcut_enum(self):
        self.assertEqual(ShortcutEnum.ID_1.value, 1)
        self.assertEqual(ShortcutEnum.ID_2.name, 'ID_2')

    def test_shortcur_enum_with_text(self):
        self.assertEqual(ShortcutEnumWithText.ID_1.value, 1)
        self.assertEqual(ShortcutEnumWithText.ID_2.name, 'ID_2')
        self.assertEqual(ShortcutEnumWithText.ID_2.text, u'verbose name 2')

    def test_hash(self):
        container = set()
        container.add(SimplestEnum.state_1)
        container.add(SimplestEnum.state_2)
        self.assertEqual(len(container), 2)

        container.add(SimplestEnum.state_2)
        self.assertEqual(len(container), 2)

        container = {SimplestEnum.state_2: 666}
        self.assertEqual(container[SimplestEnum.state_2], 666)
