import blob
from pyro.vision import *


#This might not actaully be all that useful.
class CBitmap:
    """
    Wrapper with constructor and destructor for blob.bitmap struct
    """

    def __init__(self, width, height):
        self.bitmap = blob.bitmap()
        blob.Bitmap_init(self.bitmap, width, height)

    def __del__(self):
        blob.Bitmap_del(self.bitmap)

    def set(self, x, y, data):
        """
        data must be able to be cast to an unsigned char (single byte)
        """
        blob.Bitmap_set(self.bitmap, x, y, data)

    def get(self, x, y):
        return blob.Bitmap_get(self.bitmap, x, y)
   
    def width(self):
        return self.bitmap.width

    def height(self):
        return self.bitmap.height

    def loadFromPPM(self, filename, filter, threshhold):
        blob.Bitmap_del(self.bitmap)
        self.bitmap = blob.bitmap_from_ppm(filename, filter, threshold)

    def loadFromPGM(self, filename, filter, threshold):
        blob.Bitmap_del(self.bitmap)
        self.bitmap = blob.bitmap_from_pgm(filename, filter, threshold)
   
    def saveToPGM(self, filename, levels = 65535):
        """
        levels is the number of gray levels to represent.
        The default is the maximum.
        """
        blob.Bitmap_write_to_pgm(self.bitmap, filename, levels);
    

def bitmap_from_V4LGrabber(v4lgrab, filter, threshold):
    bmp = blob.bitmap_from_8bitBGRArray(v4lgrab.cbuf, v4lgrab.width, v4lgrab.height, filter, threshold)
    return bmp


    
if __name__ == '__main__':
    #Examples of how to use blob stuff.

    #make a bitmap from cap.ppm, filtering by brightness (luminosity)
    #with a threshold of .3 (everthing with a brightness of over .3 will be
    #true.

    bmp = blob.bitmap_from_ppm("cap.ppm", blob.FILTER_BRIGHTNESS, 0.3)

    #now save it to file.
    
    blob.Bitmap_write_to_pgm(bmp, "python.pgm", 1)

    blobdata = blob.Blobdata_init(bmp)

    #clean it up
    #blob.Bitmap_del(bmp)
