import colander


class UserSchema(colander.MappingSchema):

    first_name = colander.SchemaNode(colander.String(), missing='')
    last_name = colander.SchemaNode(colander.String(), missing='')
    email = colander.SchemaNode(colander.String(), missing='')
