import colander
from deform.widget import TextAreaWidget

class UserSchema(colander.MappingSchema):

    first_name = colander.SchemaNode(colander.String(), missing='')
    last_name = colander.SchemaNode(colander.String(), missing='')
    email = colander.SchemaNode(colander.String(), missing='')


class AccountDestroySchema(colander.MappingSchema):

    reason = colander.SchemaNode(
        colander.String(),
        missing='',
        title='Do you mind telling us your reasons? We want to get better!',
        widget=TextAreaWidget(css_class='input-xlarge'),
        )
