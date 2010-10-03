function c = eval_contrast(filename)

im = imread(filename); 
g = rgb2gray(im(340-100:340+100, 512-100:512+100, :));
imshow(g)
f = fspecial('sobel');
gf = imfilter(g,f) + imfilter(g,f');
c = prctile(gf(:),99);