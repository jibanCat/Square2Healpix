import itertools
import numpy as np
import healpy as hp 
import matplotlib
#matplotlib.use("TkAgg")

def determine_nside(pix_size):
    # pixel size for healpix
    square_gen = (2**i for i in itertools.count())
    print('[Info] Checking the best nside for the input pixel size {} rad^2...'.format(pix_size))

    for i,nside in enumerate(square_gen):
        # 2 * pix_size, because if only pix_size some cases would 
        # have missing pixels in the HEALPix array
        if 2 * pix_size > 4 * np.pi / hp.nside2npix(nside):
            nside = 2**(i - 1)
            return nside
        elif i > 20: raise Exception('[Error] Too large nside, try to reduce the image array size!')


def cart_healpix(cartview, nside):
    '''read in an matrix and return a healpix pixelization map'''
    # Generate a flat Healpix map and angular to pixels
    healpix = np.zeros(hp.nside2npix(nside), dtype=np.double)
    hptheta = np.linspace(0, np.pi, num=cartview.shape[0])[:, None]
    hpphi = np.linspace(-np.pi, np.pi, num=cartview.shape[1])
    pix = hp.ang2pix(nside, hptheta, hpphi)

    # re-pixelize
    healpix[pix] = np.fliplr(np.flipud(cartview))

    return healpix

def save(output_filename, healpix, nside, write_alm=False):
    if write_alm == False:
        hp.write_map(output_filename, healpix, column_names=['same as input'], column_units=['same as input'])
    else:
        alms = hp.map2alm(healpix)
        ls, ms = hp.Alm.getlm(lmax=3 * nside - 1, i=np.arange(len(alms)))
        with open(output_filename, 'w') as file:
            for l,m,i,r in zip(ls, ms, alms.real, alms.imag):
                file.write('{} {} {} {}\n'.format(l, m, i, r))

def main(image_path, deg):
    '''
    give a image_path, deg of the side of a square, 
    return original image array and its healpix conterpart with
    square putting in the center of the sphere.
    '''
    # loading image
    image_array = np.loadtxt(image_path, )
    print('[Info] Checking input image array size...')
    #### later modify this line
    xsize = np.sqrt(len(image_array)).astype(np.int)
    if xsize**2 != len(image_array):
        raise Exception('[Error] Wrong input square size! Must be a perfect square.')

    #### Get expected Nside ####
    # pixel size for given data
    pix_size = (deg * deg) * (np.pi / 180)**2 / xsize / xsize # rad^2 / pix
                
    # expected nside            
    nside = determine_nside(pix_size)            
    ############################

    #### Insert square into cartesian projection ####
    # size of cartesian projection should be the same pixel size 
    # of user's input
    h = np.pi # height of cartview
    w = 2 * h # width  of cartview
    num = w * h / pix_size

    # number of pixels on width and height
    num_pix_h = np.sqrt(num / 2).astype(np.int)
    num_pix_w = (num_pix_h * 2).astype(np.int)

    # setting the numpy slicing 
    lower_h = num_pix_h // 2 - xsize // 2
    upper_h = lower_h + xsize
    lower_w = num_pix_w // 2 - xsize // 2
    upper_w = lower_w + xsize

    # making blank cartview projection 
    cartview = np.zeros((num_pix_h, num_pix_w)) 

    # locate the center of the image
    cartview[lower_h:upper_h, lower_w:upper_w] = image_array.reshape((xsize, xsize))
    #################################################

    # healpix conversion
    print('[Info] Converting a cartview projection to a HEALPix array.')
    healpix = cart_healpix(cartview, nside)
    return image_array, healpix, xsize
