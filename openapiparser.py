from copy import deepcopy
import itertools
from openapi_parser.specification import (
    Path,
    Object,
    Schema,
    Property,
    Integer,
    String,
    Specification,
)
from collections import OrderedDict


def parse_openapi(grammar: Specification):
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

                    if SeedQ[path.url].get(method) == None:
                        SeedQ[path.url][method] = []
                    SeedQ[path.url][method].append({"string": formatting})

                elif body.content[0].schema.type.value == "object":
                    if SeedQ[path.url].get(method) == None:
                        SeedQ[path.url][method] = []
                    object: Object = body.content[0].schema
                    current_object = dict()
                    combination_lists = list()
                    for i in object.properties:
                        formatting = OrderedDict()
                        if i.schema.read_only == True:
                            continue
                        if i.schema.type.value == "integer":
                            schema: Integer = i.schema
                            if schema.example != None:
                                combination_lists.append(schema.example)
                            formatting = {
                                "value": 0,
                                "type": schema.type.value,
                            }
                        else:
                            schema: String = i.schema
                            if schema.example != None:
                                combination_lists.append(schema.example)
                            formatting = {
                                "value": "",
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

                        current_object[i.name] = formatting
                    combination = itertools.product(*combination_lists)

                    for i in combination:
                        copyed_object = deepcopy(current_object)
                        entries = list(copyed_object.keys())
                        for j in range(len(i)):

                            copyed_object[entries[j]]["value"] = i[j]

                        SeedQ[path.url][method].append(copyed_object)
            else:
                SeedQ[path.url][method] = []
    return SeedQ


def parse_new_openapi(grammar: Specification):
    paths = grammar.paths
    SeedQ = dict()
    schema_keys = list()
    # compile schemas into a dict
    for path in paths:
        SeedQ[path.url.lower()] = {"schema": "", "methods": [], "seeds": []}
        for operation in path.operations:
            SeedQ[path.url.lower()]["methods"].append(operation.method.value)
            if operation.request_body != None:
                cur_schema: Object = operation.request_body.content[0].schema
                if SeedQ[path.url.lower()]["schema"] == "":
                    combination_lists = list()
                    SeedQ[path.url.lower()]["schema"] = cur_schema
                    if cur_schema.type.value == "object":
                        i: Property
                        for i in cur_schema.properties:
                            combination_lists.append(i.schema.example)
                            schema_keys.append(i.name)
                        combination = itertools.product(*combination_lists)
                        cur_object = dict()
                        for i in combination:
                            for j in range(len(i)):
                                cur_object[schema_keys[j]] = i[j]
                            SeedQ[path.url.lower()]["seeds"].append(cur_object)
                    
                    elif cur_schema.type.value == "string":
                        SeedQ[path.url.lower()]["seeds"].append({"string": cur_schema.example})
    return SeedQ    
