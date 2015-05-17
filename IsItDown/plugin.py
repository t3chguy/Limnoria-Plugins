###
# Copyright (c) 2015, Michael Daniel Telatynski <postmaster@webdevguru.co.uk>
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
from supybot.commands import *
import supybot.plugins as plugins
import supybot.callbacks as callbacks

import re
from bs4 import BeautifulSoup
from urllib.request import build_opener
from urllib.error import HTTPError
from urllib.parse import quote

class IsItDown(callbacks.Privmsg):
    def isitdown(self, irc, msg, args, url):
        """
        <url>: Returns the response from http://www.downforeveryoneorjustme.com/
        """
        site = 'http://downforeveryoneorjustme.com/'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        # strip the protocol because downforeveryoneorjustme.com is
        # too stupid to do that; we're smarter than that, damnit
        url = re.sub(r'^.*?://', r'', url)
        try:
            html = opener.open(site + url)
            html_str = html.read()
            soup = BeautifulSoup(html_str)
            response = soup.div.contents[0].strip()
            irc.reply(response, prefixNick=True)
        except HTTPError as oops:
            irc.reply("Hmm. downforeveryoneorjustme.com returned the following error: [%s]" % (str(oops)), prefixNick=True)
        except AttributeError:
            irc.reply("Hmm. downforeveryoneorjustme.com probably changed its response format; please update me.", prefixNick=True)
        except:
            irc.reply("Man, I have no idea; things blew up real good.", prefixNick=True)
    isitdown = wrap(isitdown, ['url'])

    def isitrestful(self, irc, msg, args, url):
        """
        <url>: Returns the response from http://isitrestful.com/
        """
        site = 'http://isitrestful.com/?url=%s'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        try:
            html = opener.open(site % quote(url))
            html_str = html.read()
            soup = BeautifulSoup(html_str)
            response = soup.h2.contents[0].strip()
            irc.reply(response, prefixNick=True)
        except HTTPError as oops:
            irc.reply("Hmm. isitrestful.com returned the following error: [%s]" % (str(oops)), prefixNick=True)
        except:
            irc.reply("Man, I have no idea; things blew up real good.", prefixNick=True)
    isitrestful = wrap(isitrestful, ['url'])

Class = IsItDown

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
