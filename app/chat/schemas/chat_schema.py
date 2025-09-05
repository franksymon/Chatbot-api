from app.core.base_schema import BaseSchema
from marshmallow import fields

class ChatSchema(BaseSchema):
    message = fields.String(required=True)
    session_id = fields.String(required=False, load_default="default")
    prompt_type = fields.String(required=False, load_default="general")
