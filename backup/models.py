import time,uuid
from orm import Model,StringField,BooleanField,Floatfield,Textfield
def next_id():
	return '%(015d%s000)'%(int(time.time()*1000),uuid.uuid4().hex)
class User(Model):
    __table__=