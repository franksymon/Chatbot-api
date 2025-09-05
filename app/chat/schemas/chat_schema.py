from app.core.base_schema import BaseSchema
from marshmallow import fields 

class ChatSchema(BaseSchema):
    message = fields.String(required=True)