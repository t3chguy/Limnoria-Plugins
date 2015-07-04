###
# Copyright (c) 2015, Michael Daniel Telatynski
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

from urllib.parse import urlencode, urlparse
from jinja2 import Template
from . import parts
import re


import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Linkifier')
except ImportError:
    _ = lambda x: x

class Linkifier(callbacks.PluginRegexp):
    """Parses URLs, Modularly"""
    unaddressedRegexps = ['process']
    callBefore = ["Web"]
    link_cache = []
    threaded = True
    handlers = {}

    def __init__(self, irc):
        self.__parent = super(Linkifier, self)
        self.__parent.__init__(irc)
        self.addHandlers()

    def addHandlers(self):
        for part in parts.list:
            try:
                name = part.__name__.rsplit('.', 1)[-1]
                getattr(part, name).addHandlers(self.handlers)
            except Exception as e:
                print(e)
                pass
        print(self.handlers)

    def process(self, irc, msg, regex):
        channel = msg.args[0]
        if (not irc.isChannel(channel) or ircmsgs.isCtcp(msg)):
            return None

        url = regex.group(0).strip()
        #checkCache = self.readCache(url)
        checkCache = None
        if checkCache is not None:
            return checkCache
        else:
            title = ""
            info = urlparse(url)
            domain = info.netloc
            if domain in self.handlers:
                title += self.handlers[domain](self, url, info, Template)
            else:
                try:
                    title += self.handlers["_"](self, url, info, Template)
                except:
                    pass
            try:
                title += self.handlers["*"](self, url, info, Template)
            except:
                pass
            irc.sendMsg(ircmsgs.privmsg(channel, title))


Class = Linkifier

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
