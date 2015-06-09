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

import supybot.conf as conf
import supybot.registry as registry
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('CleverbotIO')
except:
    _ = lambda x: x

def configure(advanced):
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('CleverbotIO', True)
    if advanced:
        output('The CleverbotIO Plugin allows you to interact with cleverbot.io')

CleverbotIO = conf.registerPlugin('CleverbotIO')

conf.registerChannelValue(CleverbotIO, 'invalidCommand',
    registry.Boolean(False, _("""Should I be invoked on Invalid Commands?""")))
conf.registerGlobalValue(CleverbotIO, 'botName',
	registry.String('', _("""The Cleverbot.io API BotName String""")))
conf.registerGlobalValue(CleverbotIO, 'appUser',
	registry.String('', _("""The Cleverbot.io API App_User String
	(required)"""), private=True))
conf.registerGlobalValue(CleverbotIO, 'appKey',
	registry.String('', _("""The Cleverbot.io API App_key String
	(required)"""), private=True))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
