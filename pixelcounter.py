#!/usr/bin/env python
# Author: Philipp Tkachev
# Copyright 2013 Philipp Tkachev
# License: GPL v3
# Version 0.1
# GIMP plugin to download brushes from ProGimp.RU

from gimpfu import *
import os, time, urllib2, json

gettext.install("gimpcloud", (gimp.directory + os.sep + 'plug-ins' + os.sep + 'locale'), unicode=True)

def echo(args):
    """Print the arguments on standard output"""
    pdb.gimp_progress_set_text(args)

def gimprgb2rgb(c):
  ret=[]
  for i in range(len(c)):
    ret.append(int(c[i]))
  return ret

def pixel2rgb(pixel):
  ret=[]
  for i in range(len(pixel)):
    ret.append(ord(pixel[i]))
  return ret

def count_pixels(image, drawable, color):
    same_color=0
    diff_color=0
    g = gimp.pdb
    layers = image.layers
    width = g.gimp_image_width(image)
    height = g.gimp_image_height(image)
    gimp.progress_init(_("Size: %d x %d" % (width, height)))
    shadow = 0
    sample_rgb = gimprgb2rgb(color)
    for x in range(width/64+1):
        for y in range(height/64+1):
            pixel_tile =  drawable.get_tile2(FALSE, x, y)
            for tx in range(pixel_tile.ewidth):
                for ty in range(pixel_tile.eheight):
                    pixel = pixel_tile[tx, ty]
                    pixel_rgb = pixel2rgb(pixel)
                    #echo("%d " % pixel_rgb[0])
                    if pixel_rgb == sample_rgb:
                        same_color=same_color+1
                    else:
                        diff_color+=1
            echo("%d vs %d " % (same_color, diff_color))
    gimp.message("Matches: %d vs %d " % (same_color, diff_color))
    time.sleep(1)


register(
    proc_name="python-fu-pixels-counter",
    blurb=_(
        "PIXELS COUNTER PLUGIN\n\n\nIf you have some questions about the plugin, write it here: \nhttp://www.zoonman.com/projects/gimp-plugins/brushes-downloader/ "),
    help=_("Pixels counter."),
    author=_("Philipp Tkachev"),
    copyright=_("Philipp Tkachev"),
    date=("2014"),
    label=_("Pixels counter"),
    imagetypes="RGB*",
    params=[
        (PF_IMAGE, "image", _("Input image"), None),
        (PF_DRAWABLE, "drawable", _("Input layer"), None),
        (PF_COLOR, "color", _("Color"), (100,100,100)),
    ],
    results=[],
    function=(count_pixels),
    menu=("<Image>/Tools/GimpCloud"),
    domain=("gimp20-python", gimp.locale_directory)
)

main()
