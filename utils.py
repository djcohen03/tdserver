import random
import datetime
from td.db.models import Tradable, Option, OptionData, session


class AppUtils(object):
    @classmethod
    def memoryused(cls):
        ''' Get's the amount of memory used in GB
        '''
        query = session.execute("SELECT pg_database_size('options');")
        memory = [byts for (byts,) in query][0]
        gigabytes = memory / (1000. ** 3)
        return round(gigabytes, 2)
