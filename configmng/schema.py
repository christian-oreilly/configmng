from pathlib import Path


class Schema:

    def __init__(self, schema):

        if isinstance(schema, (str, Path)):
            #self.load_from_file(schema)
            self.path = Path(schema)
            if not self.path.exists():
                raise FileNotFoundError("The schema file {} was not found.".format(self.path))

        else:
            raise TypeError("schema must be a str or a Path object pointing to a schema file.")

    #def load_from_file(self, schema_path):
    #    ...
