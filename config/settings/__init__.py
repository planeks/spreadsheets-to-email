from decouple import config
if config('PROD', cast=bool) == True:
    from .prod import *
else:
    from .dev import *