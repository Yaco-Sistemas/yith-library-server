import colander
from deform.widget import TextInputWidget


class ApplicationSchema(colander.MappingSchema):

    name = colander.SchemaNode(colander.String())
    main_url = colander.SchemaNode(colander.String())
    callback_url = colander.SchemaNode(colander.String())


class ReadOnlyTextInputWidget(TextInputWidget):

    def serialize(self, field, cstruct, readonly=False):
        return super(ReadOnlyTextInputWidget, self).serialize(field, cstruct=cstruct, readonly=True)


class FullApplicationSchema(ApplicationSchema):

    client_id = colander.SchemaNode(colander.String(),
                                    widget=ReadOnlyTextInputWidget())
    client_secret = colander.SchemaNode(colander.String(),
                                        widget=ReadOnlyTextInputWidget())
