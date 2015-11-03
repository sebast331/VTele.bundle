# Plugin title and path
TITLE = 'VTELE'
PREFIX = '/video/vtele'

# ART and ICON
ART = 'art-default.jpg'
ICON = 'icon-default.png'

# Base URLs
URL_BASE = "http://vtele.ca"
URL_VTELE = "http://vtele.ca/videos/"


# Show Type DICT
class TYPE_SHOW:
    DEFAULT = 0
    SQ = 1

    @staticmethod
    def get_show_type(url):
        url = url.lower()
        if "sq.vtele.ca" in url:
            return TYPE_SHOW.SQ
        else:
            return TYPE_SHOW.DEFAULT


def Start():
    # Copy-paste from template file
    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    EpisodeObject.thumb = R(ICON)
    EpisodeObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)


###################################################################################################
# Displays the main menu
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
    oc = ObjectContainer()

    oc.add(DirectoryObject(key=Callback(TVShows, title=u"Toutes les emissions"), title=u"Toutes les emissions"))
    oc.add(InputDirectoryObject(key=Callback(TVShows, title=u"Resultats de recherche: "), title="Rechercher",
                                summary=u"Rechercher une emission"))

    return oc


@route(PREFIX + '/shows')
def TVShows(title, titleRegex=None, query=""):
    # You have to open an object container to produce the icons you want to appear on this page.
    oc = ObjectContainer(title2=unicode(title + query))

    # List the shows
    html = HTML.ElementFromURL(URL_VTELE)
    arrEmissions = []
    for video in html.xpath('//div[@class="span3 emissions"]/div/a'):
        arrEmissions.append(
            {
                "url": video.xpath('./@href')[0].replace("emissions", "videos"),
                "title": video.xpath('./text()')[0]
            }
        )
    arrEmissions = sorted(arrEmissions, key=lambda k: k['title'])

    # Query is the result of a search and should be the regex
    if (query != ""):
        titleRegex = query.lower()

    # Add each TV Show in the object container
    for video in arrEmissions:
        if (titleRegex == None or Regex(titleRegex).search(video['title'].lower())):
            oc.add(
                DirectoryObject(key=Callback(ShowSeason, url=video['url'], title=video['title'], show_type=TYPE_SHOW.get_show_type(video['url'])), title=video['title']))

    return oc


###################################################################################################
# Displays a particular show given the show URL
#   @param url: string,
@route(PREFIX + '/showseason')
def ShowSeason(url, title, show_type):
    oc = ObjectContainer(title2=unicode(title))

    # Some emissions requires different XPATH
    if int(show_type) == TYPE_SHOW.SQ:
        return ShowEpisodes(title=title, site_url="http://sq.vtele.ca", saison="", show_type=show_type)
    else:
        # Site de l'emission
        html = HTML.ElementFromURL(url)
        site_url = html.xpath('//nav[@class="subSubMenu"]/a[last()]/@href')
        for season in html.xpath('//nav[@class="subSubMenu"]/a'):
            season_title = season.xpath('./text()')[0]
            # Only display "Saisons" and "Derniers Episodes"
            if u"saison" in season_title.lower():
                saison = str(season.xpath('./@href')).split('/')[-2]
                oc.add(DirectoryObject(
                    key=Callback(ShowEpisodes, site_url=site_url, saison=saison, title=title + ' - ' + season_title, show_type=show_type),
                    title=season_title))
            elif u"derni" in season_title.lower():
                saison = "derniers"
                oc.add(DirectoryObject(
                    key=Callback(ShowEpisodes, site_url=site_url, saison=saison, title=title + ' - ' + season_title, show_type=show_type),
                    title=season_title))
            elif u"exclusivi" in season_title.lower():
                # TODO: Add Exclusivite Web to the menu
                pass
    return oc


@route(PREFIX + '/showepisodes')
def ShowEpisodes(title, site_url, saison, show_type):
    oc = ObjectContainer(title2=unicode(title))

    # Some emissions requires different XPATH
    if int(show_type) == TYPE_SHOW.SQ:
        # SQ - no seasons, only videos spread in multiple pages
        html = HTML.ElementFromURL(site_url + '/episodes')
        arrPages = html.xpath('//div[@class="pagination"]/a/@href')
        for pageUrl in arrPages:
            htmlVideo = HTML.ElementFromURL(site_url + pageUrl)
            for video in htmlVideo.xpath('//ul[@id="episodes-list"]//a'):
                video_url = video.xpath('./@href')
                if len(video_url) > 0:
                    video_url = video_url[0]
                    description = "\n".join(video.xpath('./div[2]/p/text()'))
                    thumb = video.xpath('./div/img/@src')[0]
                    title = video.xpath('./div[2]/h2/text()')[0]
                    date_time = video.xpath('./div[2]/h3/text()')[0]
                    full_description = date_time + "\n" + description

                    oc.add(
                        EpisodeObject(
                            url=video_url,
                            title=title,
                            summary=full_description,
                            thumb=Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON))
                        )
                    )
    else:
        url = site_url + "episodes/" + saison + "/tous.php"
        Log("* ELSE ShowEpisodes URL => " + unicode(url))
        html = HTML.ElementFromURL(url)
        for video in html.xpath('//div[@class="mainWrapInner"]/div/div/section/div/div[2]/h3/a/../../..'):
            video_url = video.xpath('./div/a[2]/@href')
            if len(video_url) > 0:
                video_url = video_url[0]
                description = "\n".join(video.xpath('./div[2]/p[2]/text()'))
                thumb = video.xpath('./div[1]/a[1]/img/@src')[0]
                title = video.xpath('./div[2]/h3/a/text()')[0]
                date_time = video.xpath('./div[2]/span/text()')[0]
                full_description = date_time + "\n" + description

                # DEBUG
                # Log("ShowEpisodes VideoURL: " + video_url)

                oc.add(
                    EpisodeObject(
                        url=video_url,
                        title=title,
                        summary=full_description,
                        thumb=Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON))
                    )
                )
            else:
                # Video not available
                pass

    if len(oc) == 0:
        return ObjectContainer(header="Empty", message=u"Aucun video disponible")
    else:
        return oc
