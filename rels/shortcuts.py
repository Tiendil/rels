# codings: utf-8

from rels.relations import Column, Table


class Enum(Table):
    name = Column(primary=True)
    value = Column(external=True)


class EnumWithText(Table):
    name = Column(primary=True)
    value = Column(external=True)
    text = Column()

class DjangoEnum(EnumWithText):

    @classmethod
    def _choices(cls):
        return cls._select('value', 'text')
