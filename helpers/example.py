# coding: utf-8

########################
# Базовое использование
########################

from rels import Column, Relation

# Enum и EnumWithText уже объявлены в библиотеке
# и доступны как rels.Enum и rels.EnumWithText
# тут их объявления привидены для упрощения понимания

class Enum(Relation):             # объявляем абстраткное перечисление
    name = Column(primary=True)   # имя
    value = Column(external=True) # значение


# наследование — добавляем дополнительный столбец для какого-нибудь текста
#                например, для использования в пользовательском интерфейсе
class EnumWithText(Enum):
    text = Column()


class SOME_CONSTANTS(Enum):       # объявляем конкретное перечисление
    records = ( ('NAME_1', 1),    # и указываем данные для него
                ('NAME_2', 2))


class SOME_CONSTANTS_WITH_TEXT(EnumWithText): # ещё одно конкретное перечисление
    records = ( ('NAME_1', 1, 'constant 1'),
                ('NAME_2', 2, 'constant 2'))


# Работаем с перечислениями

# доступ к данным
SOME_CONSTANTS.NAME_1.name == 'NAME_1'          # True
SOME_CONSTANTS.NAME_1.value == 1                # True

# получение элемента перечисления из «сырых» данных
SOME_CONSTANTS(1) == SOME_CONSTANTS.NAME_1      # True

# сравнения
SOME_CONSTANTS.NAME_2 == SOME_CONSTANTS.NAME_2  # True
SOME_CONSTANTS.NAME_2 != SOME_CONSTANTS.NAME_1  # True

# теперь для проверок не надо всюду тягать импорты перечисления
SOME_CONSTANTS.NAME_2.is_NAME_1                 # False
SOME_CONSTANTS.NAME_2.is_NAME_2                 # True

# каждый элемент перечисления — отдельный объект,
# поэтому даже объекты с одинаковыми данными равны не будут
SOME_CONSTANTS.NAME_2 != SOME_CONSTANTS_WITH_TEXT.NAME_2  # True
SOME_CONSTANTS.NAME_1 != SOME_CONSTANTS_WITH_TEXT.NAME_1  # True

# наследование — добавляем новые элементы
class EXTENDED_CONSTANTS(SOME_CONSTANTS_WITH_TEXT):  # расширяем набор данных в перечислении
    records = ( ('NAME_3', 3, 'constant 3'), )       # добавляем ещё одно значение


########################
# Индексы
########################

class ENUM(Relation):
    name = Column(primary=True)   # для этого столбца имя индекса будет .index_name
    value = Column(external=True) # для этого столбца имя индекса будет .index_value
    text = Column(unique=False, index_name='by_key') # указываем своё имя для индекса

    records = ( ('NAME_1', 0, 'key_1'),
                ('NAME_2', 1, 'key_2'),
                ('NAME_3', 2, 'key_2'), )

# если данные в столбце уникальны, значением в словаре будет элемент перечисления
ENUM.index_name # {'NAME_1': ENUM.NAME_1, 'NAME_2': ENUM.NAME_2,  'NAME_3': ENUM.NAME_3}

# если данные в столбце не уникальны, значением в словаре будет список элементов перечисления
ENUM.by_key     # {'key_1': [ENUM.NAME_1], 'key_2': [ENUM.NAME_2, ENUM.NAME_3]}


########################
# Обратные ссылки
########################

# объявляем отношение, на которое будем ссылаться
class DESTINATION_ENUM(Relation):
    name = Column(primary=True)
    val = Column()

    records = ( ('STATE_1', 'value_1'),
                ('STATE_2', 'value_2') )

# объявляем отношение, которое будет ссылаться
class SOURCE_ENUM(Relation):
    name = Column(primary=True)
    val = Column()
    rel = Column(related_name='rel_source')

    records = ( ('STATE_1', 'value_1', DESTINATION_ENUM.STATE_1),
                ('STATE_2', 'value_2', DESTINATION_ENUM.STATE_2) )

# проверяем работу ссылок
DESTINATION_ENUM.STATE_1.rel_source == SOURCE_ENUM.STATE_1 # True
DESTINATION_ENUM.STATE_2 == SOURCE_ENUM.STATE_2.rel        # True
