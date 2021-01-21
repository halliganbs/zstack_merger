import random
import pandas as pd
import numpy as np
import re # REEEE
import glob
import tifffile

from ipyfilechooser import FileChooser
from ipywidgets import *
from progress.bar import Bar

def make_filechooser(title='Choose File'):
    fc = FileChooser()
    fc.show_hidden = True
    fc.use_dir_icons = True
    fc.show_only_dirs = True
    fc.title = title
    return fc


def merge_images(channels, output):
    """
    Merges zstacks of images
    params:
        channels - dict {str: [str]} final image name : [filenames]
    returns True
    """
    bar = Bar('Merging Images: ', max=len(channels.keys()))
    for key in channels.keys():
        name = f'{output}/{key}.tif'
        with tifffile.TiffWriter(name) as stack:
            for filename in channels[key]:
                stack.save(
                    tifffile.imread(filename),
                    photometric='minisblack', 
                    contiguous=True
                )
        bar.next()
    bar.finish()

def make_wells(files):
    """
    sorts images by wellId
    """
    well_reg = r'.*_(A[0-9]{2})_.*'
    wells = {}
    for f in files:
        entry = re.match(well_reg, f)
        key = entry.group(1)
        if key in wells.keys():
            wells[key].append(f)
        else:
            wells[key] = [f]
    return wells
        
def make_fields(wells):
    """
    sorts images in wells to images in wellId_fieldId
    """
    f_reg = r'.*_T[0-9]{4}(F[0-9]{3}).*'
    fields = {} # keys: wellID_FieldID
    for w in wells.keys():
        for a in wells[w]:
            wl = re.match(f_reg, a)
            fk = f'{w}_{wl.group(1)}' # wellID_fieldId
            if fk in fields.keys():
                fields[fk].append(a)
            else:
                fields[fk] = [a]
    return fields

def make_channels(fields):
    """
    sorts wellId_fieldId to  wellId_fieldId_channelNum (1-3) typically
    """
    c_reg = r'.*(C[0-9]{2})\.tif'
    channels = {}
    for f in fields.keys():
        for i in fields[f]:
            c = re.match(c_reg, i)
            ck = f'{f}_{c.group(1)}'
            if ck in channels.keys():
                channels[ck].append(i)
            else:
                channels[ck] = [i]
    return channels

def sort_images(files):
    """
    sorts images into final images in a dict
    params:
        files - list of filenames
    return:
        channels - dict of image names and list of filenames
    """
    w = make_wells(files)
    f = make_fields(w)
    c = make_channels(f)
    return c

def order_images(channels):
    """
    makes sure that all zstacks are in the correct order
    """
    bar = Bar('Verifying Z-Stack',max=len(channels.keys()))
    for keys in channels.keys():
        channels[keys].sort()
        bar.next()
    bar.finish()