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
import supybot.ircdb as ircdb
import supybot.plugins as plugins
import supybot.callbacks as callbacks

import re

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Replacer')
except ImportError:
    _ = lambda x: x

SED_PATTERN = re.compile(
    r'^s(?P<delim>[^A-Za-z0-9\\])(?P<pattern>.*?)(?P=delim)'
    r'(?P<replacement>.*?)(?:(?P=delim)(?P<flags>[gi]*))?$')
# SED_PATTERN = re.compile(r'^s(?P<delim>[' + re.escape(string.punctuation) + '])
# (?P<pattern>.*?)(?P=delim)(?P<replacement>.*?)(?:(?P=delim)(?P<flags>[gi]*))?$')


class Replacer(callbacks.PluginRegexp):
    """History Replacer - Sed Regex Syntax"""
    threaded = True
    public = True
    unaddressedRegexps = ('replacer',)

    @staticmethod
    def _unpack_sed(expr):
        if '\0' in expr:
            raise ValueError('expr can\'t contain NUL')

        delim = expr[1]
        escaped_expr = ''

        for (i, c) in enumerate(expr):
            if c == delim and i > 0:
                if expr[i - 1] == delim and expr[i - 2] != '\\':
                    raise ValueError('invalid expression')

                if expr[i - 1] == '\\':
                    escaped_expr = escaped_expr[:-1] + '\0'
                    continue

            escaped_expr += c

        match = re.search(SED_PATTERN, escaped_expr)

        if not match:
            raise ValueError('invalid expression')

        groups = match.groupdict()
        pattern = groups['pattern'].replace('\0', delim)
        replacement = groups['replacement'].replace('\0', delim)

        if groups['flags']:
            raw_flags = set(groups['flags'])
        else:
            raw_flags = set()

        flags = 0
        count = 1

        for flag in raw_flags:
            if flag == 'g':
                count = 0
            if flag == 'i':
                flags |= re.IGNORECASE

        pattern = re.compile(pattern, flags)

        return (pattern, replacement, count)

    def replacer(self, irc, msg, regex):
        r"^s(?P<delim>[^A-Za-z0-9\\])(?:.*?)(?P=delim)"
        r"(?:.*?)(?:(?P=delim)(?:[gi]*))?$"

        if ircdb.channels.getChannel(msg.args[0]).lobotomized:
            return

        iterable = reversed(irc.state.history)
        try:
            (pattern, replacement, count) = self._unpack_sed(msg.args[1])
        except ValueError as e:
            return
        next(iterable)
        for m in iterable:
            if m.nick == msg.nick and \
                    m.args[0] == msg.args[0] and \
                    msg.command == 'PRIVMSG' and \
                    pattern.search(m.args[1]):
                irc.reply(_("%s meant => %s") %
                          (msg.nick, pattern.sub(replacement, m.args[1], count)),
                          prefixNick=False)
                break
        return

Class = Replacer


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
