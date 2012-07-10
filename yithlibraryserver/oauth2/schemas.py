import colander


class ApplicationSchema(colander.MappingSchema):

    name = colander.SchemaNode(colander.String())
    main_url = colander.SchemaNode(colander.String())
    callback_url = colander.SchemaNode(colander.String())

