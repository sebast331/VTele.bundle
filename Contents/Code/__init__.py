# Plugin title and path
TITLE    = 'VTELE'
PREFIX   = '/video/vtele'

# ART and ICON
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

# Base URLs
URL_BASE = "http://vtele.ca"
URL_VTELE = "http://vtele.ca/videos/"

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
    oc.add(InputDirectoryObject(key=Callback(TVShows, title=u"Resultats de recherche: "), title="Rechercher", summary=u"Rechercher une emission"))

    return oc

@route(PREFIX + '/shows')
def TVShows(title, titleRegex=None, query=""):
    # You have to open an object container to produce the icons you want to appear on this page.
    oc = ObjectContainer(title2 = unicode(title + query))

    # List the shows
    html = HTML.ElementFromURL(URL_VTELE)
    arrEmissions = []
    for video in html.xpath('//*[@id="skinWrap"]/div[3]/div/div/div[2]/div/div/div[1]/ul[2 <= position() and position() <= 3]/li/a'):
        arrEmissions.append(
            {
                "url": video.xpath('./@href'),
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
            oc.add(DirectoryObject(key=Callback(ShowSeason, url=video['url'], title=video['title']), title=video['title']))

    return oc

###################################################################################################
# Displays a particular show given the show URL
#   @param url: string,
@route(PREFIX + '/showseason')
def ShowSeason(url, title):
    oc = ObjectContainer(title2=unicode(title))
    html = HTML.ElementFromURL(url)

    # Site de l'emission
    site_url = html.xpath('//nav[@class="subSubMenu"]/a[last()]/@href')
    for season in html.xpath('//nav[@class="subSubMenu"]/a'):
        season_title = season.xpath('./text()')[0]
        # Only display "Saisons" and "Derniers Episodes"
        if u"saison" in season_title.lower():
            saison = str(season.xpath('./@href')).split('/')[-2]
            oc.add(DirectoryObject(key=Callback(ShowEpisodes, site_url=site_url, saison=saison, title=title + ' - ' + season_title), title=season_title))
        elif u"derni?res" in season_title.lower():
            saison = "derniers"
            oc.add(DirectoryObject(key=Callback(ShowEpisodes, site_url=site_url, saison=saison, title=title + ' - ' + season_title), title=season_title))
        elif u"exclusivit?" in season_title.lower():
            # TODO: Add Exclusivite Web to the menu
            pass
    return oc

@route(PREFIX + '/showepisodes')
def ShowEpisodes(title, site_url, saison):
    oc = ObjectContainer(title2=title)
    url = site_url + "episodes/" + saison + "/tous.php"
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
            #Log("ShowEpisodes VideoURL: " + video_url)

            oc.add(
                EpisodeObject(
                    url = video_url,
                    title = title,
                    summary = full_description,
                    thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON))
                )
            )
        else:
            # Video not available
            pass

    if len(oc) == 0:
        return ObjectContainer(header="Empty", message=u"Aucun vid?o disponible")
    else:
        return oc