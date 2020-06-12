Subscene Plus Kodi addon
========================

Subscene plus is a kodi addon intended to facilitate downloading subtitles from subscene.com. Subscene.com does not provide an API. Hence, subscene plus works by automatically parsing the HTML files and following download links.

TV-shows are not currently tested, but give it a try, it might work.

How to setup:
=============
Clone the repo and store the contents of *service.subtitles.subsceneplus* in a zip file with the version number added to it.
```bash
git clone https://github.com/Cih2001/KodiSubsceneAddon.git
cd KodiSubsceneAddon/
VER=$(cat service.subtitles.subsceneplus/addon.xml | grep version | grep -v "<" | sed -r "s/.*\"(.*)\"/\1/g")
zip -r service.subtitles.subsceneplus-$VER.zip service.subtitles.subsceneplus/
```
and install the zip archive (with a file name similar to service.subtitles.subsceneplus-1.0.59.zip) in Kodi.

Official repository:  
* https://github.com/Cih2001/KodiSubsceneAddon

Big shoutout to:  
* https://github.com/amet/service.subtitles.demo/
* https://github.com/amet/service.subtitles.opensubtitles
* https://github.com/manacker/service.subtitles.subscene
