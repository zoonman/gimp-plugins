#!/usr/bin/env python
# Author: Philipp Tkachev
# Copyright 2013 Philipp Tkachev
# License: GPL v3
# Version 0.1
# GIMP plugin to download brushes from ProGimp.RU

from gimpfu import *
import os, time, urllib2, json

gettext.install("gimp20-python", gimp.locale_directory, unicode = True)

def echo(args):
	"""Print the arguments on standard output"""
	pdb.gimp_progress_set_text(args)

def build_req(url):
	req = urllib2.Request(url)
	req.add_header('Referer', 'http://www.progimp.ru/')
	req.add_header('User-agent', ("Gimp/%d.%d.%d" % gimp.version) )
	return req

def download_tags():
	#tags = {"Small":"small", "Middle-size":"mid", "Big size":"big"}
	tags = ["", "Small", "Middle-size", "Big size"]
	tags_n = (("", "Small"), ("Middle-size", "Big size"))
	return tags_n
	
def download_brushes( path, size) :
	#tags = ",".join(size)
	page = 1
	total_pages = 1
	p = 0.0
	while page <= total_pages:
		rpc_url = "http://www.progimp.ru/rpc.php?p=get.brushes&filter=%s&pg=%s" %  (size , page)
		gimp.progress_init("Looking up for new brushes...")
		rpc_req = build_req(rpc_url)
		pg_url = urllib2.urlopen(rpc_req)
		if pg_url:
			res = pg_url.read()
			br_list = json.loads(res)
			if br_list[u'pages']:
				total_pages = br_list[u'pages']
			if br_list[u'brushes']:
				br_list_len = float( br_list[u'brushes_total'])
				for cbr in br_list[u'brushes']:
					p = p + 1.0
					pdb.gimp_progress_update(p / br_list_len )
					echo("Getting... " + cbr[u'name'])
					brush_file_path = path + os.sep  + cbr[u'file']
					if os.path.isfile(brush_file_path) :
						echo(cbr[u'name']+" already exists!")
					else:
						get_brush_url = "http://www.progimp.ru/downloads/brushes/%s/get/" % cbr[u'id']
						fd = open(brush_file_path, "wb")
						if fd:
							get_brush_req = build_req(get_brush_url)
							get_brush_resp = urllib2.urlopen(get_brush_req)
							total_size = get_brush_resp.info().getheader('Content-Length').strip()
							total_size = int(total_size)
							bytes_so_far = 0
							chunk_size = 4096
							while 1:
								chunk = get_brush_resp.read(chunk_size)
								if not chunk:
									break
								else:
									fd.write(chunk)
									bytes_so_far += len(chunk)
									echo("Downloading " + cbr[u'name']+ ", %0.2f%% done" % round(100*float(bytes_so_far)/total_size, 2))
									fd.flush()
							echo("Downloading " + cbr[u'name']+ " complete!")		
							fd.close()		
						else:
							echo("Can't open file")
			page += 1				
		else:
			echo("Can't connect to the Cloud!")
			break
	time.sleep(0.1)	
	pdb.gimp_brushes_refresh()

register(
	proc_name = ("python-fu-download-brushes"),
	blurb = _("BRUSHES DOWNLOADER PLUGIN\n\n\nIf you have some questions about the plugin, write it here: \nhttp://www.zoonman.com/projects/gimp-plugins/brushes-downloader/ "),
	help = ("Download brushes."),
	author = ("Philipp Tkachev"),
	copyright = ("Philipp Tkachev"),
	date = ("2013"),
	label = _("Download brushes"),
	imagetypes=(""),
	params=[
		(PF_DIRNAME, "path", _("Save Brushes to this Directory"), (gimp.directory + os.sep + 'brushes') ),
		(PF_RADIO, "size", _("Size"), "", ((_('Any'),""),(_('Small'),'small'),(_('Middle'),'mid'),(_('Big'),'big'))),
	],
	results=[],
	function=(download_brushes),
	menu=("<Image>/Tools/GimpCloud"),
	domain=("gimp20-python", gimp.locale_directory)
)

main()
