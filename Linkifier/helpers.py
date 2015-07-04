import random
def getUserAgent(self):
    """
    Returns a random user agent from the ones available
    """
    return random.choice(self.registryValue("userAgents"))

import re
from datetime import timedelta
def getSecondsFromDuration(input):
    regex = re.compile('(?P<sign>-?)P(?:(?P<years>\d+)Y)?(?:(?P<months>\d+)M)?(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?')
    duration = regex.match(input).groupdict(0)
    delta = timedelta(hours=int(duration['hours']),
                      minutes=int(duration['minutes']),
                      seconds=int(duration['seconds']))
    return delta.total_seconds()

def getTimeFromSeconds(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        duration = "%02d:%02d" % (m, s)
        if h > 0:
            duration = "%02d:%s" % (h, duration)
        return duration