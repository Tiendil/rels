# coding: utf-8
import copy

from unittest import TestCase

from rels.relations import Relation, Column, Record

from rels import exceptions

class Enum(Relation):
    name = Column(primary=True, no_index=False, primary_checks=True)
    value = Column(external=True, no_index=False)


class EnumWithText(Relation):
    name = Column(primary=True, no_index=False, primary_checks=True)
    value = Column(external=True, no_index=False)
    text = Column(no_index=False)


class EmptyRelation(Relation):
    pass

# just to test, that empy records does not break class costruction
class EmptyRecordsRelation(Relation):
    name = Column(no_index=False)
    value = Column(no_index=False)


class SimplestRelation(Relation):
    name = Column(no_index=False)
    value = Column(no_index=False)

    records = (('name_a', 1),
                ('name_b', 2))


class SimplestEnum(Relation):
    name = Column(primary=True, no_index=False, primary_checks=True)
    value = Column(external=True, no_index=False)

    records = ( ('state_1', 'val_1'),
                 ('state_2', 'val_2') )

class EnumWith2Primaries(Relation):

    name = Column(primary=True, no_index=False, primary_checks=True)
    value = Column(primary=True, no_index=False, primary_checks=True)

    records = ( ('STATE_1', 'value_1'),
                 ('STATE_2', 'value_2') )

class IndexesRelation(Relation):
    name = Column(primary=True, no_index=False, primary_checks=True)
    val_1 = Column(no_index=False)
    val_2 = Column(unique=False, no_index=False)
    val_3 = Column(index_name='val_3_index', no_index=False)

    records = ( ('rec_1', 'val_1_1', 'val_2_1', 'val_3_1'),
                 ('rec_2', 'val_1_2', 'val_2_2', 'val_3_2'),
                 ('rec_3', 'val_1_3', 'val_2_2', 'val_3_3'),
                 ('rec_4', 'val_1_4', 'val_2_4', 'val_3_4'),)

class RelationDestinationRelation(Relation):
    name = Column(primary=True, no_index=False, primary_checks=True)
    val_1 = Column(no_index=False)

    records = ( ('STATE_1', 'value_1'),
                 ('STATE_2', 'value_2') )

class RelationSourceRelation(Relation):
    name = Column(primary=True, no_index=False, primary_checks=True)
    val_1 = Column(no_index=False)
    rel = Column(related_name='rel_source', no_index=False)

    records = ( ('STATE_1', 'value_1', RelationDestinationRelation.STATE_1),
                 ('STATE_2', 'value_2', RelationDestinationRelation.STATE_2) )

class ShortcutEnum(Enum):
    records = ( ('ID_1', 1),
                 ('ID_2', 2) )

class ShortcutEnumWithText(EnumWithText):
    records = ( ('ID_1', 1, 'verbose name 1'),
                 ('ID_2', 2, 'verbose name 2') )



class SimpleColumnTests(TestCase):

    def test_default_index_name(self):
        column = Column()
        column.initialize(name='test')
        self.assertEqual(column.index_name, 'index_test')

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

    # def test_get_index__no_index(self):
    #     column_1 = Column(no_index=True)
    #     column_1.initialize('column_1')

    #     records = ( Record([column_1], ['str_1']),
    #                 Record([column_1], ['str_2']))

    #     self.assertEqual(column_1.get_index(records), None)

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

    # def test_repr(self):
    #     column = Column(related_name='rel_name')
    #     column.initialize(name='col_name')

    #     column._creation_order += 1 # enshure, that creation order will be equal
    #     self.assertEqual(eval(repr(column)).__dict__, column.__dict__)


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
        self.assertEqual(repr(RelationDestinationRelation.records[0]),
                         'RelationDestinationRelation.STATE_1')


class SimpleRelationTests(TestCase):

    def setUp(self):
        pass

    def test_empy_relation(self):
        self.assertEqual(EmptyRelation.records, tuple())

    def test_simplest_relation(self):
        self.assertEqual(len(SimplestRelation.records), 2)
        self.assertEqual(SimplestRelation._raw_records, (('name_a', 1),
                                                      ('name_b', 2)))

    def test_uniqueness_restriction(self):
        def create_bad_relation():
            class SimplestRelation(Relation):
                name = Column()
                value = Column(unique=True)

                records = (('name_a', 1),
                            ('name_b', 1))

        self.assertRaises(exceptions.DuplicateValueError, create_bad_relation)

    def test_primary_uniqueness_restriction(self):
        def create_bad_relation():
            class SimplestRelation(Relation):
                name = Column(primary=True, unique=False)
                value = Column()

                records = (('name_a', 1),
                            ('name_b', 1))

        self.assertRaises(exceptions.PrimaryWithoutUniqueError, create_bad_relation)


    def test_simplest_enum_attributes(self):
        self.assertEqual(SimplestEnum.state_1.value, 'val_1')
        self.assertEqual(SimplestEnum.state_1.name, 'state_1')
        self.assertEqual(SimplestEnum.state_2.value, 'val_2')
        self.assertEqual(SimplestEnum.state_2.name, 'state_2')

    def test_primary_attributes_setupped(self):
        self.assertEqual(SimplestEnum.records, (SimplestEnum.state_1, SimplestEnum.state_2))

    def test_only_primary_attributes_setupped(self):
        self.assertFalse(hasattr(SimplestEnum, 'val_1'))
        self.assertFalse(hasattr(SimplestEnum, 'val_2'))

    def test_records_check_attributes_setupped(self):
        self.assertTrue(SimplestEnum.state_1.is_state_1)
        self.assertFalse(SimplestEnum.state_1.is_state_2)
        self.assertFalse(SimplestEnum.state_2.is_state_1)
        self.assertTrue(SimplestEnum.state_2.is_state_2)

        self.assertFalse(hasattr(SimplestEnum.state_1, '_is_val_1'))
        self.assertFalse(hasattr(SimplestEnum.state_1, '_is_val_2'))
        self.assertFalse(hasattr(SimplestEnum.state_2, '_is_val_1'))
        self.assertFalse(hasattr(SimplestEnum.state_2, '_is_val_2'))

    def test_get_record_by_not_external_id(self):
        self.assertRaises(exceptions.NotExternalValueError, SimplestEnum, 'bla-bla')

    def test_more_then_1_external_columns(self):
        def create_bad_relation():
            class SimplestRelation(Relation):
                name = Column(external=True)
                value = Column(external=True)

                records = (('name_a', 'name_c'),
                            ('name_b', 'name_d'))

        self.assertRaises(exceptions.MultipleExternalColumnsError, create_bad_relation)

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

        self.assertEqual(EnumWith2Primaries.records,
                         (EnumWith2Primaries.STATE_1,
                          EnumWith2Primaries.STATE_2))

    def test_primary_name_duplicate_another_relation_attribute(self):
        def create_bad_relation():
            class SimplestRelation(Relation):
                name = Column(primary=True)
                value = Column(primary=True)

                records = (('name_a', 'name_c'),
                            ('name_b', 'name_a'))

        self.assertRaises(exceptions.PrimaryDuplicatesRelationAttributeError, create_bad_relation)

    def test_primary_name_duplicate_another_record_attribute(self):
        def create_bad_relation():
            class SimplestRelation(Relation):
                name = Column(primary=True, no_index=False, primary_checks=True)
                is_name = Column(primary=True, no_index=False, primary_checks=True)

                records = (('name_a', 'name_c'),
                           ('name_b', 'name'))

        self.assertRaises(exceptions.DuplicateIsPrimaryError, create_bad_relation)


    def test_simplest_indexes(self):
        self.assertEqual(IndexesRelation.index_name,
                         {'rec_1': IndexesRelation.rec_1,
                          'rec_2': IndexesRelation.rec_2,
                          'rec_3': IndexesRelation.rec_3,
                          'rec_4': IndexesRelation.rec_4 })

        self.assertEqual(IndexesRelation.index_val_1,
                         {'val_1_1': IndexesRelation.rec_1,
                          'val_1_2': IndexesRelation.rec_2,
                          'val_1_3': IndexesRelation.rec_3,
                          'val_1_4': IndexesRelation.rec_4 })

        self.assertEqual(IndexesRelation.index_val_2,
                         {'val_2_1': (IndexesRelation.rec_1,),
                          'val_2_2': (IndexesRelation.rec_2, IndexesRelation.rec_3),
                          'val_2_4': (IndexesRelation.rec_4,) })

        self.assertEqual(IndexesRelation.val_3_index,
                         {'val_3_1': IndexesRelation.rec_1,
                          'val_3_2': IndexesRelation.rec_2,
                          'val_3_3': IndexesRelation.rec_3,
                          'val_3_4': IndexesRelation.rec_4 })

    def test_index_duplicate_another_relation_attribute(self):
        def create_bad_relation():
            class SimplestRelation(Relation):
                name = Column(primary=True, index_name='name_a', no_index=False)
                value = Column(no_index=False)

                records = (('name_a', 1),
                            ('name_b', 2))

        self.assertRaises(exceptions.IndexDuplicatesRelationAttributeError, create_bad_relation)

    def test_relations_setup(self):
        self.assertEqual(RelationSourceRelation.STATE_1, RelationDestinationRelation.STATE_1.rel_source)
        self.assertEqual(RelationSourceRelation.STATE_2, RelationDestinationRelation.STATE_2.rel_source)
        self.assertEqual(RelationSourceRelation.STATE_1.rel, RelationDestinationRelation.STATE_1)
        self.assertEqual(RelationSourceRelation.STATE_2.rel, RelationDestinationRelation.STATE_2)
        self.assertEqual(RelationSourceRelation.STATE_1, RelationSourceRelation.STATE_1.rel.rel_source)
        self.assertEqual(RelationSourceRelation.STATE_2, RelationSourceRelation.STATE_2.rel.rel_source)

    def test_relations_setup_without_set_method(self):
        def create_bad_relation():
            class RelationSourceRelation(Relation):
                name = Column(primary=True)
                val_1 = Column()
                rel = Column(related_name='rel_source')

                records = ( ('STATE_1', 'value_1', 1), # just any type without .set_related_name
                             ('STATE_2', 'value_2', RelationDestinationRelation.STATE_2) )

        self.assertRaises(exceptions.SetRelatedNameError, create_bad_relation)

    def test_relations_setup_duplicate_name_error(self):
        def create_bad_relation():
            class RelationSourceRelation(Relation):
                name = Column(primary=True)
                val_1 = Column()
                rel = Column(related_name='rel_source')

                # "name" duplicate primary attribute of RelationDestinationRelation
                records = ( ('name', 'value_1', RelationDestinationRelation.STATE_1),
                             ('STATE_2', 'value_2', RelationDestinationRelation.STATE_2) )

        self.assertRaises(exceptions.DuplicateRelatonNameError, create_bad_relation)

    def test_relation_inheritance(self):
        class BaseRelation(Relation):
            name = Column(primary=True)
            value = Column()

        class ChildRelation(BaseRelation):
            records = (('id_1', 1),
                        ('id_2', 2))

        self.assertEqual(ChildRelation.id_1.name, 'id_1')
        self.assertEqual(ChildRelation.id_2.name, 'id_2')

    def test_column_redifinition(self):
        class BaseRelation(Relation):
            name = Column(primary=True, no_index=False)
            value = Column(no_index=False)

        class ChildRelation(BaseRelation):
            value = Column(unique=False, no_index=False)
            records = (('id_1', 1),
                        ('id_2', 1))

        self.assertEqual(ChildRelation.index_value, {1: ChildRelation.records})

    def test_relation_inheritance_with_records(self):
        class BaseRelation(Relation):
            name = Column(primary=True, no_index=False)
            value = Column(no_index=False)
            records = (('id_0', 0),)

        class ChildRelation(BaseRelation):
            value = Column(unique=False, no_index=False)
            records = (('id_1', 1),
                        ('id_2', 2))

        self.assertEqual(ChildRelation.id_0.name, 'id_0')
        self.assertEqual(ChildRelation.id_1.name, 'id_1')
        self.assertEqual(ChildRelation.id_2.name, 'id_2')

        self.assertEqual(len(ChildRelation.records), 3)
        self.assertEqual(ChildRelation._raw_records, (('id_0', 0),
                                                   ('id_1', 1),
                                                   ('id_2', 2),))

        self.assertRaises(AttributeError, getattr, BaseRelation, 'id_1')

        self.assertEqual(len(BaseRelation.index_name), 1)
        self.assertEqual(len(ChildRelation.index_name), 3)


    def test_shortcut_enum(self):
        self.assertEqual(ShortcutEnum.ID_1.value, 1)
        self.assertEqual(ShortcutEnum.ID_2.name, 'ID_2')

    def test_shortcur_enum_with_text(self):
        self.assertEqual(ShortcutEnumWithText.ID_1.value, 1)
        self.assertEqual(ShortcutEnumWithText.ID_2.name, 'ID_2')
        self.assertEqual(ShortcutEnumWithText.ID_2.text, 'verbose name 2')

    def test_hash(self):
        container = set()
        container.add(SimplestEnum.state_1)
        container.add(SimplestEnum.state_2)
        self.assertEqual(len(container), 2)

        container.add(SimplestEnum.state_2)
        self.assertEqual(len(container), 2)

        container = {SimplestEnum.state_2: 666}
        self.assertEqual(container[SimplestEnum.state_2], 666)

    def test_copy_relation(self):
        self.assertEqual(id(SimplestRelation), id(copy.copy(SimplestRelation)))

    def test_deepcopy_relation(self):
        self.assertEqual(id(SimplestRelation), id(copy.deepcopy(SimplestRelation)))

    def test_copy_record(self):
        self.assertEqual(id(SimplestRelation.records[0]), id(copy.copy(SimplestRelation.records[0])))

    def test_deepcopy_record(self):
        self.assertEqual(id(SimplestRelation.records[0]), id(copy.deepcopy(SimplestRelation.records[0])))
