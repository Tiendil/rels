# codings: utf-8

from rels.relations import Column, Relation


class Enum(Relation):
    name = Column(primary=True, no_index=True, primary_checks=True)
    value = Column(external=True, no_index=True)


class EnumWithText(Relation):
    name = Column(primary=True, no_index=True, primary_checks=True)
    value = Column(external=True, no_index=True)
    text = Column()


class NullObject(object):

    def set_related_name(self, *argv, **kwargs):
        pass
