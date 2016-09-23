'''
api definition

'''
import json,logging,inspect,functools
class APIError(Exception):
    def __init__(self,error,data='',message=''):
        super(api_version(),self).__init__(message)
        self.error=error
        self.data=data
        self.message=message
    