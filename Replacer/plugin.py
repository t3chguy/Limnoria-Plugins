# -*- coding: utf-8 -*-

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
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks

from .timeout import timeout, TimeoutError
import time
import re

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Replacer')
except ImportError:
    _ = lambda x: x


SED_PATTERN = (r"s(?P<delim>[^\w\\])(?P<pattern>.*?)(?P=delim)"
               r"(?P<replacement>.*?)(?:(?P=delim)(?P<flags>[gi]*))?$")
ACT_PATTERN = r"^(?i)(?:(?P<nick>[a-z_\-\[\]\\^{}|`][\w\-\[\]\\^{}|`]*)[|:, ]{1,2})?"
SED_REGEX = re.compile(r"^" + SED_PATTERN)


class RegexpTimeout(Exception):
    pass


class Replacer(callbacks.PluginRegexp):
    """History Replacer - Sed Regex Syntax"""
    threaded = True
    public = True
    unaddressedRegexps = ['replacer']

    @staticmethod
    def _unpack_sed(expr):
        if '\0' in expr:
            raise ValueError('Expression can\'t contain NUL')

        delim = expr[1]
        escaped_expr = ''

        for (i, c) in enumerate(expr):
            if c == delim and i > 0:
                if expr[i - 1] == '\\':
                    escaped_expr = escaped_expr[:-1] + '\0'
                    continue

            escaped_expr += c

        match = SED_REGEX.search(escaped_expr)

        if not match:
            return None

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

    @timeout(0.01)
    def _regexsearch(self, text, pattern):
        return pattern.search(text)

    @timeout(2)
    def replacer(self, irc, msg, regex):
        if not self.registryValue('enable', msg.args[0]):
            return None
        iterable = reversed(irc.state.history)
        msg.tag('Replacer')
        target = regex.group('nick') or ''

        if target:
            checkNick = target
            prefix = '%s thinks %s' % (msg.nick, target)
        else:
            checkNick = msg.nick
            prefix = msg.nick

        try:
            message = 's' + msg.args[1][len(target):].split('s', 1)[-1]
            (pattern, replacement, count) = self._unpack_sed(message)
        except ValueError as e:
            self.log.warning(_("Replacer error: %s"), e)
            if self.registryValue('displayErrors', msg.args[0]):
                irc.error(_("Replacer error: %s" % e), Raise=True)
            return None

        next(iterable)
        for m in iterable:
            if m.nick == checkNick and \
                    m.args[0] == msg.args[0] and \
                    m.command == 'PRIVMSG':

                if ircmsgs.isAction(m):
                    text = ircmsgs.unAction(m)
                    tmpl = 'do'
                else:
                    text = m.args[1]
                    tmpl = 'say'

                try:
                    if not self._regexsearch(text, pattern):
                        continue
                except TimeoutError as e: # Isn't working for some reason
                    self.log.error('TIMEOUT ERROR CAUGHT!!')
                    break
                except Exception as e:
                    self.log.error('Replacer: %s' % type(e).__name__)
                    break

                if self.registryValue('ignoreRegex', msg.args[0]) and \
                        m.tagged('Replacer'):
                    continue
                irc.reply(_("%s meant to %s “ %s ”") %
                          (prefix, tmpl, pattern.sub(replacement,
                           text, count)), prefixNick=False)
                return None

        self.log.debug(_("""Replacer: Search %r not found in the last %i
                       messages."""), regex, len(irc.state.history))
        if self.registryValue("displayErrors", msg.args[0]):
            irc.error(_("Search not found in the last %i messages.") %
                      len(irc.state.history), Raise=True)
        return None
    replacer.__doc__ = ACT_PATTERN + SED_PATTERN

Class = Replacer


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
