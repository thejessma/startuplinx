from wtforms import StringField, BooleanField, IntegerField, DecimalField 
from wtforms import validators
from wtforms.widgets import TextArea
from flask_wtf import Form

def model_form(ModelClass, field_list):
    class F(Form):
        pass

    for field_name in field_list:
        col = getattr(ModelClass, field_name)
        type = str(col.property.columns[0].type)
        if type.startswith('VARCHAR'):
            setattr(F, field_name, StringField(field_name))
        elif type.startswith('TEXT'):
            setattr(F, field_name, StringField(field_name, widget=TextArea()))
        elif type.startswith('INTEGER') or type.startswith('BIGINT'):
            setattr(F, field_name, IntegerField(field_name, [validators.Optional()]))
        elif type.startswith('FLOAT'):
            setattr(F, field_name, DecimalField(field_name, [validators.Optional()]))
        elif type.startswith('BOOLEAN'):
            setattr(F, field_name, BooleanField(field_name, [validators.Optional()]))
        else:
            print 'WARNING: UNKNOWN SQLALCHEMY TYPE --> ' + str(type)
            print '               for field ' + field_name
            setattr(F, field_name, StringField(field_name))
    return F

