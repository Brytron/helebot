from pathlib import Path
from PIL import Image
import os
import random

pic_path = "wheresRyan_photos/"
def add_ryan(fguy, fvista, fout):
    """adds an image to another image"""
    guyimage = Image.open(fguy)
    vistaimage = Image.open(fvista)
    guyout = guyimage.convert("RGBA")
    outimage = vistaimage.convert("RGBA")
    guyout = guyout.resize((600,600))
    outimage = outimage.resize((1920,1080))
    position = (int((outimage.width-guyout.width)/2),outimage.height-guyout.height)
    outimage.paste(guyout,position,guyout)
    outimage.save(fout)

def add_fence(fguy, fvista, fout):
    """adds an image to another image"""
    guyimage = Image.open(fguy)
    vistaimage = Image.open(fvista)
    guyout = guyimage.convert("RGBA")
    outimage = vistaimage.convert("RGBA")
    guyout = guyout.resize((1920,550))
    outimage = outimage.resize((1920,1080))
    position = (int((outimage.width-guyout.width)/2),outimage.height-guyout.height)
    outimage.paste(guyout,position,guyout)
    outimage.save(fout)


def add_all (fguy_1, fguy_2, fguy_3, fvista, fout):
    """adds 3 images to a photo"""
    guy_image_1 = Image.open(fguy_1)
    guy_image_2 = Image.open(fguy_2)
    guy_image_3 = Image.open(fguy_3)

    guyout_1 = guy_image_1.convert("RGBA")
    guyout_2 = guy_image_2.convert("RGBA")
    guyout_3 = guy_image_3.convert("RGBA")
    guyout_1 = guyout_1.resize((500, 500))
    guyout_2 = guyout_2.resize((500, 500))
    guyout_3 = guyout_3.resize((500, 500))

    vista_image = Image.open(fvista)
    out_image = vista_image.convert("RGBA")
    out_image = out_image.resize((1920, 1080))

    position1 = (int((out_image.width - guyout_1.width) / 2), out_image.height - guyout_1.height)
    position2 = (int((out_image.width - guyout_2.width) / 4), out_image.height - guyout_2.height)
    position3 = (int((out_image.width - guyout_3.width) * 3 / 4), out_image.height - guyout_3.height)
    out_image.paste(guyout_1,position1,guyout_1)
    out_image.paste(guyout_2, position2, guyout_2)
    out_image.paste(guyout_3, position3, guyout_3)

    out_image.save(fout)


def test_addall():

    out = Path(pic_path + '/outputs/newimage.png')
    vpath = pic_path + '/vistas'

    random_filename = random.choice([
        x for x in os.listdir(vpath)
        if os.path.isfile(os.path.join(vpath, x))
    ])

    vista = Path(vpath + random_filename)

    guy1 = Path(pic_path + '/Member_photos/Brytron.png')
    guy2 = Path(pic_path + '/Member_photos/Congohunter.png')
    guy3 = Path(pic_path + '/Member_photos/Jet3010.png')

    add_all(guy1,guy2,guy3,vista,out)
