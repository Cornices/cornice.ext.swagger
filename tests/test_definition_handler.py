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


class FeelingList(colander.SequenceSchema):
    feel = FeelingsSchema(validator=colander.OneOf(['bleh', 'aaaa']))


class ToDoStuff(colander.MappingSchema):
    todo = colander.SchemaNode(colander.String())


class CheckList(colander.SequenceSchema):
    todo = ToDoStuff()


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

    def test_single_level_oneOf_schema(self):
        handler = DefinitionHandler(ref=1)
        oneOf = colander.OneOf(['bleh', 'aaaa'])
        feels = FeelingsSchema(title='Feelings', validator=oneOf)
        ref = handler.from_schema(feels)

        ref_feels = handler.definition_registry['Feelings']
        self.assertEquals(ref, {'$ref': '#/definitions/Feelings'})
        self.assertDictEqual(ref_feels, convert(feels))

    def test_multi_level_oneOf_schema(self):
        handler = DefinitionHandler(ref=-1)
        oneOf = colander.OneOf(['bleh', 'aaaa'])
        feels = FeelingsSchema(title='Feelings', validator=oneOf)
        ref1 = handler.from_schema(feels)
        self.assertEquals(ref1, {'$ref': '#/definitions/Feelings'})

        feelings_schema = {
            'oneOf': [
                {'$ref': '#/definitions/Aaaa'},
                {'$ref': '#/definitions/Bleh'}
            ]
        }
        feelings_refs = handler.definition_registry['Feelings']
        self.assertIn('oneOf', feelings_refs)
        self.assertIsInstance(feelings_refs['oneOf'], list)
        self.assertListEqual(sorted(feelings_schema['oneOf'], key=lambda x: x['$ref']),
                             sorted(feelings_refs['oneOf'], key=lambda x: x['$ref']))
        self.assertDictContainsSubset(convert(AnxietySchema()),
                                      handler.definition_registry['Aaaa'])

    def test_single_level_simple_array(self):
        handler = DefinitionHandler(ref=1)
        todo_list = CheckList()
        ref = handler.from_schema(todo_list)

        ref_todo = handler.definition_registry['CheckList']
        self.assertEquals(ref, {'$ref': '#/definitions/CheckList'})
        self.assertDictEqual(ref_todo, convert(todo_list))

    def test_multi_level_simple_array(self):
        handler = DefinitionHandler(ref=-1)
        todo_list = CheckList()
        ref = handler.from_schema(todo_list)

        check_list = {
            'type': 'array',
            'items': {'$ref': '#/definitions/Todo'},
            'title': 'CheckList'
        }
        ref_check_list = handler.definition_registry['CheckList']
        self.assertEquals(ref, {'$ref': '#/definitions/CheckList'})
        self.assertDictEqual(ref_check_list, check_list)
        ref_todo = handler.definition_registry['Todo']
        self.assertDictEqual(ref_todo, convert(ToDoStuff(title='Todo')))

    def test_single_level_oneOf_array_no_title(self):
        handler = DefinitionHandler(ref=1)
        all_those_feels = FeelingList()
        ref = handler.from_schema(all_those_feels)

        ref_feels = handler.definition_registry['FeelingList']
        self.assertEquals(ref, {'$ref': '#/definitions/FeelingList'})
        self.assertDictEqual(ref_feels, convert(all_those_feels))

    def test_single_level_oneOf_array_with_title(self):
        handler = DefinitionHandler(ref=1)
        all_those_feels = FeelingList(title='ThoseFeels')
        ref = handler.from_schema(all_those_feels)

        ref_feels = handler.definition_registry['ThoseFeels']
        self.assertEquals(ref, {'$ref': '#/definitions/ThoseFeels'})
        self.assertDictEqual(ref_feels, convert(all_those_feels))

    def test_multi_level_oneOf_array(self):
        handler = DefinitionHandler(ref=-1)
        all_those_feels = FeelingList()
        ref = handler.from_schema(all_those_feels)

        feel_list_schema = {
            'type': 'array',
            'items': {
                '$ref': '#/definitions/FeelingListItem'
            },
            'title': 'FeelingList'
        }
        feel_items = [
            {'$ref': '#/definitions/Aaaa'},
            {'$ref': '#/definitions/Bleh'}
        ]
        ref_feels = handler.definition_registry['FeelingList']
        self.assertEquals(ref, {'$ref': '#/definitions/FeelingList'})
        self.assertDictEqual(feel_list_schema, ref_feels)
        ref_feels_item = handler.definition_registry['FeelingListItem']
        self.assertIn('oneOf', ref_feels_item)
        self.assertListEqual(sorted(ref_feels_item['oneOf'], key=lambda x: x['$ref']),
                             sorted(feel_items, key=lambda x: x['$ref']))
