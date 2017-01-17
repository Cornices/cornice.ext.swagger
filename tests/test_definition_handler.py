import unittest

import colander

from cornice_swagger.swagger import DefinitionHandler
from cornice_swagger.converters import convert_schema as convert


class MyListSchema(colander.SequenceSchema):
    entry = colander.SchemaNode(colander.String())


class BoredoomSchema(colander.MappingSchema):
    motivators = MyListSchema()
    status = colander.SchemaNode(colander.String(),
                                 validator=colander.OneOf(['increasing', 'decrasing']))


class AnxietySchema(colander.MappingSchema):
    level = colander.SchemaNode(colander.Integer(),
                                validator=colander.Range(42, 9000))


class FeelingsSchema(colander.MappingSchema):
    bleh = BoredoomSchema()
    aaaa = AnxietySchema()


class DefinitionTest(unittest.TestCase):

    def setUp(self):
        self.handler = DefinitionHandler()

    def test_from_schema(self):
        self.assertDictEqual(self.handler.from_schema(FeelingsSchema()),
                             convert(FeelingsSchema()))


class RefDefinitionTest(unittest.TestCase):

    def test_single_level(self):
        handler = DefinitionHandler(ref=1)
        ref = handler.from_schema(FeelingsSchema(title='Feelings'))

        self.assertEquals(ref, {'$ref': '#/definitions/Feelings'})
        self.assertDictEqual(handler.definition_registry['Feelings'],
                             convert(FeelingsSchema(title='Feelings')))

    def test_multi_level(self):
        handler = DefinitionHandler(ref=-1)

        ref1 = handler.from_schema(FeelingsSchema(title='Feelings'))
        self.assertEquals(ref1, {'$ref': '#/definitions/Feelings'})

        feelings_schema = {
            'properties': {
                'aaaa': {'$ref': '#/definitions/Aaaa'},
                'bleh': {'$ref': '#/definitions/Bleh'}
            }
        }
        self.assertDictContainsSubset(feelings_schema,
                                      handler.definition_registry['Feelings'])

        self.assertDictContainsSubset(convert(AnxietySchema()),
                                      handler.definition_registry['Aaaa'])
