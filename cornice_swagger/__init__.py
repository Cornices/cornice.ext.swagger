__author__ = """Josip Delic"""
__email__ = 'delicj@delijati.net'
__version__ = '0.3.0'


class CorniceSwaggerPredicate(object):
    def __init__(self, schema, config):
        self.schema = schema

    def phash(self):
        return str(self.schema)


def includeme(config):
    config.add_view_predicate('response_schemas', CorniceSwaggerPredicate)
    config.add_view_predicate('tags', CorniceSwaggerPredicate)
