from __future__ import division, print_function
from __future__ import unicode_literals
import sys
from mp_io import mp_load_data
from mp_io import MP_FILE_EXTENSION, mp_save_data
from mp_base import mp_create_gti_from_condition, mp_root, mp_create_gti_mask
from mp_base import mp_cross_gtis


def mp_create_gti(fname, filter_expr):
    '''Creates a GTI list by using boolean operation on any of the data
    sections of the file'''
    # Necessary as nc variables are sometimes defined as array
    from numpy import *

    if filter_expr is None:
        sys.exit('Please specify a filter expression')
    data = mp_load_data(fname)

    # Map all entries of data to local variables
    locals().update(data)

    good = eval(filter_expr)

    gtis = mp_create_gti_from_condition(locals()['time'], good)

    outfile = mp_root(fname) + '_gti' + MP_FILE_EXTENSION
    mp_save_data({'GTI': gtis}, outfile)

    return gtis


def mp_apply_gti(fname, gti, outname=None):
    '''Applies a GTI list to the data contained in a file. File MUST have a
    GTI extension already, and an extension called `time`'''
    data = mp_load_data(fname)

    try:
        datagti = data['GTI']
        newgtis = mp_cross_gtis([gti, datagti])
    except:
        print ('Data have no GTI extension')
        newgtis = gti

    data['GTI'] = newgtis
    good = mp_create_gti_mask(data['time'], newgtis)
    data['time'] = data['time'][good]
    if outname is None:
        outname = fname.replace(MP_FILE_EXTENSION, '') + \
            '_gtifilt' + MP_FILE_EXTENSION
    mp_save_data(data, outname)

    return newgtis


if __name__ == '__main__':
    import argparse
    description = 'Creates lightcurves starting from event files. It is' + \
        ' possible to specify energy or channel filtering options'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("files", help="List of files", nargs='+')

    parser.add_argument("-f", "--filter", type=str, default=None,
                        help="Filter expression, that has to be a valid " +
                        "Python boolean operation on a data variable " +
                        "contained in the files")

    parser.add_argument("-c", "--create-only",
                        default=False, action="store_true",
                        help="If specified, creates GTIs withouth applying" +
                        "them to files (Default: False)")

    parser.add_argument("-o", "--overwrite",
                        default=False, action="store_true",
                        help="Overwrite original file (Default: False)")

    args = parser.parse_args()

    filter_expr = args.filter

    for fname in args.files:
        gtis = mp_create_gti(fname, filter_expr)
        if args.create_only:
            continue
        if args.overwrite:
            outname = fname
        else:
            # Use default
            outname = None
        mp_apply_gti(fname, gtis)
