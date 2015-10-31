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

    # You have to open an object container to produce the icons you want to appear on this page.
    oc = ObjectContainer()

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

    # Add each TV Show in the object container
    for video in arrEmissions:
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
        if "Saison".lower() in season_title.lower():
            saison = str(season.xpath('./@href')).split('/')[-2]
            oc.add(DirectoryObject(key=Callback(ShowEpisodes, site_url=site_url, saison=saison, title=title + ' - ' + season_title), title=season_title))

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
        return ObjectContainer(header="Empty", message=u"Aucun vidéo disponible")
    else:
        return oc


#########################################################################################################################
# the command below is helpful when looking at logs to determine which function is being executed
# ALSO SAYS IT HELPS THE DESIGNER CREATE A "REST-like API" BUT I DO NOT KNOW WHAT EXACTLY THAT MEANS. I AM THINKING IT
# ALLOWS ACCESS DIRECTLY TO THE FUNCTION FROM OUTSIDE OF THE CODE
@route(PREFIX + '/showrss')

# This function shows a basic loop to go through an xml rss feed and pull the data for all the videos or shows listed
# there
def ShowRSS(title):

    # define an object container and pass the title in from the function above
    oc = ObjectContainer(title2=title)

    # This is the data parsing API to pull elements from an RSS feed.
    xml = RSS.FeedFromURL(url)
    # enter a for loop to return an object for every entry in the feed
    for item in xml.entries:
        # Pull the data that is available in the form of link, title, date and description
        url = item.link
        title = item.title
        # The date is not always in the correct format so it is always best to return use Datetime.ParseDate to make sure it is correct
        date = Datetime.ParseDate(item.date)
        desc = item.description
        # Return an object for each item you loop through.  This produces an icon or video name for each entry to the screen.
        # It is important to ensure you are reading these attributes in to the correct name.  See the Framework Documentation
        # for a complete list of objects and the attributes that can be returned with each.
        oc.add(
            VideoClipObject(
                url = url,
                title = title,
                summary = description,
                # Resource.ContentsOfURLWithFallback test the icon to make sure it is valid or returns the fallback if not
                thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),
                originally_available_at = date
            )
        )

    # This code below is helpful to show when a source is empty
    if len(oc) < 1:
        #Log('still no value for objects')
        return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")

    return oc