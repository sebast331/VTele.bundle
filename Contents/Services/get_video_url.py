__author__ = 'sebast'

import re
import json
import requests

class get_video_url:

    '''
        PARAMS:
            1: videoPlayer=
            2: additionalAdTargetingParams=
            3: startTime=
            4: refURL=
    '''
    URL_PLAYER = "http://c.brightcove.com/services/viewer/htmlFederated?&width=640&height=360&flashID=mainPlayer&bgcolor=%23000000&wmode=opaque&isVid=true&isUI=true&dynamicStreaming=true&autoStart=false&allowFullScreen=true&%40videoPlayer=%s&includeAPI=true&allowScriptAccess=always&showNoContentMessage=true&playerID=2852956699001&playerKey=AQ~~%2CAAAAkAV1KVk~%2C3a02lxSo0UDkABa1913QCmvnpLrAVqIT&playerType=MainPlayerVideo&templateLoadHandler=V.vp.mainPlayer.templateLoaded&templateReadyHandler=V.vp.mainPlayer.templateReady&templateErrorHandler=V.vp.mainPlayer.templateError&adServerURL=http%3A%2F%2Fd.adgear.com%2Fimpressions%2Fuint_nc%2Fasc%3D4430%2Ff%3D29%2Fchip%3Dd575787025470131d2a50024e87a30c2.xml%3F&additionalAdTargetingParams=%s&debuggerID=&startTime=%s&refURL=%s"
    URL2 = "http://c.brightcove.com/services/viewer/htmlFederated?&width=640&height=360&flashID=mainPlayer&bgcolor=%23000000&wmode=opaque&isVid=true&isUI=true&dynamicStreaming=true&autoStart=false&allowFullScreen=true&%40videoPlayer=4573468607001&includeAPI=true&allowScriptAccess=always&showNoContentMessage=true&playerID=2852956699001&playerKey=AQ~~%2CAAAAkAV1KVk~%2C3a02lxSo0UDkABa1913QCmvnpLrAVqIT&playerType=MainPlayerVideo&templateLoadHandler=V.vp.mainPlayer.templateLoaded&templateReadyHandler=V.vp.mainPlayer.templateReady&templateErrorHandler=V.vp.mainPlayer.templateError&adServerURL=http%3A%2F%2Fd.adgear.com%2Fimpressions%2Fuint_nc%2Fasc%3D4431%2Ff%3D29%2Fchip%3De22ca44025470131d2a00024e87a30c2.xml%3F&additionalAdTargetingParams=AG_P2%3Drpm-plus%26idbc%3D4573468607001%26pageURL%3Dhttp%25253A%25252F%25252Fauto.vtele.ca%25252Fvideos%25252Frpm-plus%25252Fle-metier-de-lettreur-et-marc-lachapelle-journaliste-automobile_85313.php&debuggerID=&startTime=1445954877558&refURL=http://vtele.ca/videos/scorpion/au-nom-du-pere_85353.php"
    USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53'
    REF_URL = "http://auto.vtele.ca/videos/rpm/ultra-mousse-et-lave-cire-disparu-la-scion-xd_84635_84605.php"

    def getParamJSON(self, source):
        strRegex = 'customKeyValue: (\{.+?\})'
        reMatch = re.search(strRegex, source, re.IGNORECASE)
        jsonMatch = json.loads(unicode(str.replace(reMatch.group(1), "'", '"')))
        return jsonMatch

    def getParamVideoPlayer(self):
        pass

    def getParamAdditionalAdTargetingPArams(self):
        #jsonMatch = getParamJSON(source)
        return ""
        #return urllib.quote(urllib.urlencode(jsonMatch), safe='')
        #return "additionalAdTargetingParams=AG_P2%3Dscorpion%26idbc%3D4578799607001%26pageURL%3D" + TEST_URL

    def getParamStartTime(self):
        pass

    def getParamRefURL(self):
        return self.REF_URL
        pass

    def getPageSource(self, url, user_agent=USER_AGENT):
        headers = {'User-Agent': user_agent, "referer": REF_URL}
        r = requests.get(url, headers=headers)
        return r.content
        # req = urllib2.Request(url, None, headers)
        # response = urllib2.urlopen(req)
        # return response.read()

    def getBestStreamURL(self,url):
        arrStreams = self.getStreamsURL(url)
        largerBitRate = 0
        for video in arrStreams:
            encodingRate = int(video["encodingRate"])
            if encodingRate > largerBitRate:
                bestVideoURL = video["defaultURL"]
                largerBitRate = encodingRate
        return bestVideoURL

    def getStreamsURL(self, url):
        arrStreams = []
        testPageSource = self.getPageSource(url)
        paramAdditonalAd = "" # getParamAdditionalAdTargetingPArams(testPageSource)
        paramVideoPlayer = self.getParamJSON(testPageSource)["idbc"]
        paramRefURL = self.getParamRefURL(testPageSource)
        #paramStartTime = str(int(time.mktime(datetime.datetime.now().timetuple()))) + "653"
        paramStartTime = "1445956838653"

        # Now we can retrieve the MP4 Player URL
        mp4Source = self.getPageSource(self.URL_PLAYER.replace("%s", paramVideoPlayer, 1).replace("%s", paramAdditonalAd, 1).replace("%s", paramStartTime, 1).replace("%s", paramRefURL))

        # Get all streams
        strRegex = '"renditions":(\[.+?\])'
        reMatch = re.search(strRegex, mp4Source)
        jsonMatch = json.loads(unicode(reMatch.group(1)))

        for video in jsonMatch:
            arrStreams.append({
                "encodingRate"  : int(video["encodingRate"]),
                "defaultURL"    : video["defaultURL"],
                "height"        : int(video["frameHeight"]),
                "width"         : int(video["frameWidth"]),
                "size"          : int(video["size"]),
                "videoCodec"    : video["videoCodec"]
            })

        return arrStreams