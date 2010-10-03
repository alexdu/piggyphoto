import piggyphoto, pygame
import os
import time
import Image, ImageFilter, ImageChops, ImageStat
from collections import deque

def eval_focus(file, s=5):
    im = Image.open(file).convert("L")
    w,h = im.size
    box = (w/2 - 200, h/2 - 200, w/2 + 200, h/2 + 200)
    im = im.crop(box)
    imf = im.filter(ImageFilter.MedianFilter(s))
    d = ImageChops.subtract(im, imf, 1, 100)
    return ImageStat.Stat(d).stddev[0]
    

def quit_pressed():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False

def show(file):
    picture = pygame.image.load(file)
    picture = pygame.transform.scale(picture, (1056,704))
    main_surface.blit(picture, (0, 0))
    pygame.display.flip()

C = piggyphoto.camera()
C.leave_locked()
C.capture_preview('preview.jpg')

picture = pygame.image.load("preview.jpg")
pygame.display.set_mode(picture.get_size())
main_surface = pygame.display.get_surface()


Q = deque()
k = 1


#raw_input()


looking_for_peak = True

while not quit_pressed():
    C.capture_preview('preview.jpg')
    show("preview.jpg")
    f = eval_focus("preview.jpg")
    Q.append(f)
    if len(Q) > 20: 
        Q.popleft()
        
    F = max(Q)
    pygame.display.set_caption("Focus: %.4g / %.4g / %s" % (f, F, looking_for_peak))
    
    if len(Q) == 20:
        if looking_for_peak:
            if f < F * 0.8:
                looking_for_peak = False
        else:
            if f > F * 0.98:
                C.capture_image("snap%d.jpg" % k)
                show("snap%d.jpg" % k)
                k = k + 1
                Q = deque()
                time.sleep(1)
                looking_for_peak = True
