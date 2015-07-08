from urllib.request import urlopen
from jinja2 import Template
import lxml.html

class default(object):

    def configure(conf, registry, _):
        conf.newGlobal('Template',
            registry.String(
                "^ {{title}}",
                _("""Template used for the Default Title Handler""")))

    def addHandlers(self):
        self.handlers["_"] = default.handler

    def handler(self, url, info):
        """
        Uses urllib and lxml to get the value of the <title>
        within the page requested.
        """

        return Template(self.registryValue("handlers.default.Template")).render({
            "title": lxml.html.parse(url).find(".//title").text
        })
