import Image, ImageFilter, ImageChops, ImageStat
import time

def estimate(file, s=5):
    """Estimates the amount of focus of an image file.
    Returns a real number: lower values indicate better focus.
    """
    im = Image.open(file).convert("L")
    w,h = im.size
    box = (w/2 - 50, h/2 - 50, w/2 + 50, h/2 + 50)
    im = im.crop(box)
    imf = im.filter(ImageFilter.MedianFilter(s))
    d = ImageChops.subtract(im, imf, 1, 100)
    return ImageStat.Stat(d).stddev[0]

if __name__ == "__main__":
    t = time.time()
    print eval_focus("preview.jpg")
    print time.time()-t
