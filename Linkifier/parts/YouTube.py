from urllib.parse import urlencode, urlparse, parse_qsl
import supybot.ircutils as ircutils
import requests
import json

from .. import helpers

class YouTube(object):

    def configure(conf, registry, _):
        conf.newGlobal('DeveloperKey',
            registry.String("",
            _("""Youtube Developer Key - required for the Youtube handler."""),
              private=True))
        conf.newGlobal('Template',
            registry.String(
                "^ {{logo}} {{title}} :: Duration: {{duration}} :: Views: {{view_count}}"
                " uploaded by {{channel_title}} :: {{like_count}} likes :: "
                "{{dislike_count}} dislikes :: {{favorite_count}} favorites",
                _("""Template used for YouTube title responses""")))

    def addHandlers(handlers):
        handlers["youtube.com"] = YouTube.handler
        handlers["www.youtube.com"] = YouTube.handler
        handlers["youtu.be"] = YouTube.handler
        handlers["m.youtube.com"] = YouTube.handler

    def handler(self, url, info, Template):
        """
        Uses the Youtube API to provide additional meta data about
        Youtube Video links posted.
        """
        developerKey = self.registryValue("handlers.YouTube.DeveloperKey")

        if not developerKey:
            self.log.error("Linkifier YouTube: DeveloperKey is Missing!")
            return ""

        VID = YouTube.getVIDfromURL(url, info)
        YTTemplate = Template(self.registryValue("handlers.YouTube.Template"))

        if VID:
            encopt = urlencode({
                "part": "snippet,statistics,contentDetails",
                "maxResults": 1,
                "key": developerKey,
                "id": VID
            })
            ApiURL = "https://www.googleapis.com/youtube/v3/videos?%s" % encopt

            self.log.info("Linkifier YouTube: requesting %s" % ApiURL)

            request = requests.get(ApiURL, headers={ "User-Agent": helpers.getUserAgent(self) })

            if request.status_code == requests.codes.ok:
                response = json.loads(request.text)

                if response:
                    try:
                        items = response["items"]
                        video = items[0]
                        snippet = video["snippet"]
                        statistics = video["statistics"]

                        duration = helpers.getSecondsFromDuration(video["contentDetails"]["duration"])
                        if duration > 0:
                            duration = helpers.getTimeFromSeconds(duration)
                        else:
                            duration = "LIVE"

                        title = YTTemplate.render({
                            "title": snippet["title"],
                            "duration": duration,
                            "view_count": "{:,}".format(int(statistics["viewCount"])),
                            "like_count": "{:,}".format(int(statistics["likeCount"])),
                            "dislike_count": "{:,}".format(int(statistics["dislikeCount"])),
                            "comment_count": "{:,}".format(int(statistics["commentCount"])),
                            "favorite_count": "{:,}".format(int(statistics["favoriteCount"])),
                            "channel_title": snippet["channelTitle"],
                            "logo": YouTube.getYouTubeLogo()
                        })

                    except IndexError as e:
                        self.log.error("Linkifier YouTube: IndexError parsing Youtube API JSON response: %s" % (str(e)))
                else:
                    self.log.error("Linkifier YouTube: Error parsing Youtube API JSON response")
            else:
                self.log.error("Linkifier YouTube: Youtube API HTTP %s: %s" % (request.status_code, request.text))

        if title:
            return title

    def getVIDfromURL(url, info):
        """
        Get YouTube video ID from URL
        """
        try:
            path = info.path
            domain = info.netloc
            video_id = ""

            if domain == "youtu.be":
                video_id = path.split("/")[1]
            else:
                parsed = parse_qsl(info.query)
                params = dict(parsed)

                if "v" in params:
                    video_id = params["v"]

            if video_id:
                return video_id
            else:
                self.log.error("Linkifier: error getting video id from %s" % url)

        except IndexError as e:
            self.log.error("Linkifier: error getting video id from %s (%s)" % (url, str(e)))

    def getYouTubeLogo():
        colored_letters = [
            "%s" % ircutils.mircColor("You", fg="red", bg="white"),
            "%s" % ircutils.mircColor("Tube", fg="white", bg="red")
        ]
        yt_logo = "".join(colored_letters)
        return yt_logo
