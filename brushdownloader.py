#!/usr/bin/env python
# Author: Philipp Tkachev
# Copyright 2013 Philipp Tkachev
# License: GPL v3
# Version 0.1
# GIMP plugin to download brushes from ProGimp.RU

from gimpfu import *
import os, time, urllib2, json

gettext.install("gimp20-python", gimp.locale_directory, unicode = True)


def echo(*args):
  """Print the arguments on standard output"""
  print "echo:", args

def build_req(url):
	req = urllib2.Request(url)
	req.add_header('Referer', 'http://www.progimp.ru/')
	req.add_header('User-agent', ("Gimp/%d.%d.%d" % gimp.version) )
	return req

def get_file_name(openUrl):
	if 'Content-Disposition' in openUrl.info():
		# If the response has Content-Disposition, try to get filename from it
		cd = dict(map(
			lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
			openUrl.info()['Content-Disposition'].split(';')))
		if 'filename' in cd:
			filename = cd['filename'].strip("\"'")
			if filename: return filename
	# if no filename was found above, parse it out of the final URL.
	return os.path.basename(urlparse.urlsplit(openUrl.url)[2])

def download_tags():
	#tags = {"Small":"small", "Middle-size":"mid", "Big size":"big"}
	tags = ["", "Small", "Middle-size", "Big size"]
	tags_n = (("", "Small"), ("Middle-size", "Big size"))
	return tags_n
	
def download_brushes(image,    path, size) :
	#tags = ",".join(size)
	page = 1
	rpc_url = "http://www.progimp.ru/rpc.php?p=get.brushes&filter=%s&pg=%s" %  (size , page)
	gimp.progress_init("Looking up for new brushes...")
	
	rpc_req = build_req(rpc_url)
	pg_url = urllib2.urlopen(rpc_req)
	if pg_url:
		res = pg_url.read()
		br_list = json.loads(res)
		if br_list[u'brushes']:
			br_list_len = len( br_list[u'brushes'])
			p = 0.0
			for cbr in br_list[u'brushes']:
				p = p + 1.0
				pdb.gimp_progress_update(p / br_list_len )
				pdb.gimp_progress_set_text("Getting... " + cbr[u'name'])
				brush_file_path = path + os.sep  + cbr[u'file']
				if os.path.isfile(brush_file_path) :
					pdb.gimp_progress_set_text(cbr[u'name']+" already exists!")
				else:
					get_brush_url = "http://www.progimp.ru/downloads/brushes/%s/get/" % cbr[u'id']
					get_brush_req = build_req(get_brush_url)
					get_brush_resp = urllib2.urlopen(get_brush_req)
					fd = open(brush_file_path, "wb")
					if fd:
						fd.write(get_brush_resp.read())
						
					else:
						echo("can't open file")
				
				
	else:
		print 'something went wrong'
	time.sleep(0.5)	
	pdb.gimp_brushes_refresh()

register(
    proc_name = ("python-fu-download-brushes"),
    blurb = _("BRUSHES DOWNLOADER PLUGIN\n\n\nIf you have some questions about the plugin, write it here: \nhttp://www.zoonman.com/projects/gimp-plugins/brushes-downloader/ "),
    help = ("Download brushes."),
    author = ("Philipp Tkachev"),
    copyright = ("Philipp Tkachev"),
    date = ("2013"),
    label = _("Download brushes"),
    imagetypes=("*"),
    params=[
        (PF_IMAGE, "image", _("Image"), None),
        #(PF_OPTION, "tags", _("Tags"), 0, download_tags() ),
        (PF_DIRNAME, "path", _("Save Brushes to this Directory"), (gimp.directory + os.sep + 'brushes') ),
        (PF_RADIO, "size", _("size"), "", ((_('Any'),""),(_('Small'),'small'),(_('Middle'),'mid'),(_('Big'),'big'))),
       
		],
    results=[],
    function=(download_brushes),
    menu=("<Toolbox>/Tools"),
    domain=("gimp20-python", gimp.locale_directory)
)

main()
