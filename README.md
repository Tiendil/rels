Extended Python enums with relations between them.

See rels.tests for examples.

```
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
                 
                 
class SimpleTableTests(TestCase):
                 
    def test_relations_setup(self):
        self.assertEqual(RelationSourceTable.STATE_1, RelationDestinationTable.STATE_1.rel_source)
        self.assertEqual(RelationSourceTable.STATE_2, RelationDestinationTable.STATE_2.rel_source)
        self.assertEqual(RelationSourceTable.STATE_1.rel, RelationDestinationTable.STATE_1)
        self.assertEqual(RelationSourceTable.STATE_2.rel, RelationDestinationTable.STATE_2)
        self.assertEqual(RelationSourceTable.STATE_1, RelationSourceTable.STATE_1.rel.rel_source)
        self.assertEqual(RelationSourceTable.STATE_2, RelationSourceTable.STATE_2.rel.rel_source)

```
