
from openapi_parser.specification import Path, Object, Schema, Property, Integer, String, Specification

def parse_openapi(grammar:Specification):
    SeedQ = dict()
    for path in grammar.paths:
        methods = path.operations
        SeedQ[path.url] = dict()
        for operation in methods:
            method = operation.method.value
            body = operation.request_body
            if body != None:
                if body.content[0].schema.type.value == "string":
                    schema: String = body.content[0].schema
                    formatting = {
                        "value": schema.example,
                        "type": "string",
                    }

                    if schema.max_length != None:
                        formatting["max_length"] = schema.max_length
                    else:
                        formatting["max_length"] = 10
                    if schema.min_length != None:
                        formatting["min_length"] = schema.min_length
                    else:
                        formatting["min_length"] = 1
                    SeedQ[path.url][method] = {"string": formatting}

                elif body.content[0].schema.type.value == "object":
                    object: Object = body.content[0].schema
                    SeedQ[path.url][method] = {}
                    for i in object.properties:
                        formatting = dict()
                        if i.schema.type.value == "integer":
                            schema: Integer = i.schema
                            formatting = {
                                "value": schema.example,
                                "type": schema.type.value,
                            }
                        else:
                            schema: String = i.schema
                            formatting = {
                                "value": schema.example,
                                "type": schema.type.value,
                            }
                            if schema.max_length != None:
                                formatting["max_length"] = schema.max_length
                            else:
                                formatting["max_length"] = 10
                            if schema.min_length != None:
                                formatting["min_length"] = schema.min_length
                            else:
                                formatting["min_length"] = 1
                        SeedQ[path.url][method][i.name] = formatting
    return SeedQ