from imgurpython.helpers.error import ImgurClientRateLimitError, ImgurClientError
from imgurpython import ImgurClient
from jinja2 import Template
import re

from .. import helpers

class imgur(object):

    Client = None
    Valid = None

    def configure(conf, registry, _):
        conf.newGlobal('ClientID',
            registry.String("", _("""imgur Client ID""")))

        conf.newGlobal('ClientSecret',
            registry.String("", _("""imgur Client secret""")))

        conf.newGlobal('Template',
            registry.String(
            "^ {%if section %}[{{section}}] {% endif -%}{%- if title -%} "
            "{{title}} :: {% endif %}[{{type}}] ({{width}}x{{height}}) "
            "{{file_size}} :: {{view_count}} views :: {%if nsfw == None %}not "
            "sure if safe for work{% elif nsfw == True %}✗ NOT Safe for Work!"
            "{% else %}✓ Safe for Work{% endif %}",
            _("""imgur Image Template""")))

        conf.newGlobal('AlbumTemplate',
            registry.String(
            "^ {%if section %}[{{section}}] {% endif -%}{%- if title -%} "
            "{{title}} :: {% endif %}{{image_count}} images :: {{view_count}} "
            "views :: {%if nsfw == None %}not sure if safe for work"
            "{% elif nsfw == True %}✗ NOT Safe for Work!{% else %}"
            "✓ Safe for Work{% endif %}", _("""imgur Album Template""")))

    def addHandlers(self):
        self.handlers["i.imgur.com"] = imgur.handlerImage
        self.handlers["imgur.com"] = imgur.handler
        imgur.initialize(self)

    def initialize(self):
        """
        Check if imgur client id or secret are set, and if so initialize
        imgur API client
        """
        if imgur.Valid is None:
            imgur.Valid = re.compile(r"[a-z0-9]+")

        if imgur.Client is None:
            ClientID = self.registryValue("handlers.imgur.ClientID")
            ClientSecret = self.registryValue("handlers.imgur.ClientSecret")

            if ClientID and ClientSecret:
                self.log.info("Linkifier imgur: enabling imgur handler")

                try:
                    imgur.Client = ImgurClient(ClientID, ClientSecret)
                except ImgurClientError as e:
                    self.log.error("Linkifier imgur: imgur client error: %s" % e.error_message)
            else:
                print("KEYS NOT ADDED IMGUR")

    def isValid(input):
        """
        Tests if input matches the typical imgur id,
        which seems to be alphanumeric. Images, galleries,
        and albums all share their format in their identifier.
        """
        return imgur.Valid.match(input, re.IGNORECASE) is not None

    def handler(self, url, info):
        """
        Queries imgur API for additional information about imgur links.
        This handler is for any imgur.com domain.
        """

        isGallery = info.path.startswith("/gallery/")
        if info.path.startswith("/a/"):
            return imgur.handlerAlbum(self, url, info)
        else:
            return imgur.handlerImage(self, url, info)

    def handlerAlbum(self, url, info):
        """
        Handles retrieving information about albums from the imgur API.

        imgur provides the following information about albums:
        https://api.imgur.com/models/album
        """
        if imgur.Client:
            AlbumID = info.path.split("/a/")[1]

            """ If there is a query string appended, remove it """
            if "?" in AlbumID:
                AlbumID = AlbumID.split("?")[0]

            if imgur.isValid(AlbumID):
                self.log.info("Linkifier imgur: found imgur album id %s" % AlbumID)
                try:
                    album = imgur.Client.get_album(AlbumID)
                    if album:
                        return Template(self.registryValue("handlers.imgur.AlbumTemplate")).render({
                            "title": album.title,
                            "section": album.section,
                            "view_count": "{:,}".format(album.views),
                            "image_count": "{:,}".format(album.images_count),
                            "nsfw": album.nsfw
                        })

                    else:
                        self.log.error("Linkifier imgur: imgur album API returned unexpected results!")

                except ImgurClientRateLimitError as e:
                    self.log.error("Linkifier imgur: imgur rate limit error: %s" % e.error_message)
                except ImgurClientError as e:
                    self.log.error("Linkifier imgur: imgur client error: %s" % e.error_message)
            else:
                self.log.info("Linkifier imgur: unable to determine album id for %s" % url)

    def handlerImage(self, url, info):
        """
        Handles retrieving information about images from the imgur API.

        Used for both direct images and imgur.com/some_ImageID_here type links, as
        they're both single images.
        """
        if imgur.Client:
            """
            If there is a period in the path, it's a direct link to an image. If not, then
            it's a imgur.com/some_ImageID_here type link
            """
            lpath = info.path.lstrip("/")
            ImageID = lpath.split(".")[0] if "." in info.path else lpath

            if imgur.isValid(ImageID):
                self.log.info("Linkifier imgur: found image id %s" % (ImageID))
                try:
                    image = imgur.Client.get_image(ImageID)
                    if image:
                        readable_file_size = helpers.getReadableFileSize(image.size)
                        return Template(self.registryValue("handlers.imgur.Template")).render({
                            "title": image.title,
                            "type": image.type,
                            "nsfw": image.nsfw,
                            "width": image.width,
                            "height": image.height,
                            "view_count": "{:,}".format(image.views),
                            "file_size": readable_file_size,
                            "section": image.section
                        })
                    else:
                        self.log.error("Linkifier imgur: imgur API returned unexpected results!")
                except ImgurClientRateLimitError as e:
                    self.log.error("Linkifier imgur: imgur rate limit error: %s" % e.error_message)
                except ImgurClientError as e:
                    self.log.error("Linkifier imgur: imgur client error: %s" % e.error_message)
            else:
                self.log.error("Linkifier imgur: error retrieving image id for %s" % url)
