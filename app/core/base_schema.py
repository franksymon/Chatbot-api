from flask_marshmallow import Marshmallow

ma = Marshmallow()

class BaseSchema(ma.Schema):
    class Meta:
        ordered = True

        