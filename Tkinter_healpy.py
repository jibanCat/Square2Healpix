import sys
if sys.version_info[0] > 2:
    from tkinter import *
    import tkinter.filedialog as tkFileDialog
else: 
    from Tkinter import *
    import tkFileDialog

from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from image2healpix import *
import matplotlib
#matplotlib.use("TkAgg")

def select_image():
    global panelA, panelB, entry1

    path = tkFileDialog.askopenfilename()

    try:
        deg = float(entry1.get())
        if not (0 < deg <= 180):
            print('Please enter a valid number between 0 - 180 deg.')    
    except ValueError:
        print('Please enter a valid number between 0 - 180 deg.')

    if len(path) > 0:
        image_array, healpix, xsize = main(path, deg)        

        # panel A
        image = image_array.reshape((xsize, xsize))
        image = (image - image.min()) / (image.max() - image.min()) * 255
        image = Image.fromarray(image.astype(np.uint8)).resize((400, 400))
        image = ImageTk.PhotoImage(image)

        # panel B
        project = hp.mollview(healpix, xsize=400, return_projected_map=True)
        #plt.close()

        project[project == -np.inf] = project.max()
        project = (project - project.min()) / (project.max() - project.min()) * 255
        project = Image.fromarray(project.astype(np.uint8))
        project = ImageTk.PhotoImage(project)

        print('[Info] Creating panels')
        # inital panel 
        if panelA is None or panelB is None:
            panelA = Label(image=image)        
            panelA.image = image
            panelA.grid(row=2, column=0, padx=10, pady=10)

            panelB = Label(image=project,)
            panelB.healpix = healpix
            panelB.nside   = hp.npix2nside(len(healpix))
            panelB.image = project
            panelB.grid(row=2, column=1, padx=10, pady=10)

        # or update the panels 
        else:
            panelA.configure(image=image)
            panelB.configure(image=project, )
            panelA.image = image
            panelB.image = project
            panelB.healpix = healpix
            panelB.nside   = hp.npix2nside(len(healpix))


def save_file():
    global panelB
    output_file = tkFileDialog.asksaveasfilename()
    if output_file is None:
        return 
    save('{}.fits'.format(output_file),
        panelB.healpix, write_alm=False)

def save_alm_file():
    global panelB
    output_file = tkFileDialog.asksaveasfilename()
    if output_file is None:
        return 
    print('[Info] Saving the alms file ... take a little while to convert image file to alms')
    save(output_file + '.fits',
         panelB.healpix, panelB.nside, write_alm=True)


root = Tk()
root.title = 'Square image to HEALPix'
panelA = None
panelB = None

Label1 = Label(root, text="deg of the square (0-180): ").grid(row=0, column=0, sticky=W)
Label2 = Label(root, text="sqaure image array (1-D): ").grid(row=0, column=1, sticky=W)
entry1 = Entry(root, )
entry1.grid(row=1, sticky=W)

# create button
save_button = Button(root, text="save the HEALPix map fits", command=save_file)
#save_button.pack(side="bottom", fill="both", expand=True, padx="2", pady="2")
save_button.grid(row=3, sticky=W)
save_alm_button = Button(root, text="save the HEALPix alm (l,m,re,im)", command=save_alm_file)
#save_alm_button.pack(side="bottom", fill="both", expand=True, padx="2", pady="2")
save_alm_button.grid(row=4, sticky=W)

button = Button(root, text="select", command=select_image)
#button.pack(side="bottom", fill="both", expand=True, padx="10", pady="10")
button.grid(row=1, column=1, sticky=W)

root.mainloop()