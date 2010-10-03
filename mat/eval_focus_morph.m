function e = eval_focus_morph(file, se)

if isstr(file), 
    im = im2double(imread(file));
else
    im = file;
end
if size(im,3) > 1,
    img = rgb2gray(im);
else
    img = im2double(im);
end


img = img(340-50:340+50, 300-50:300+50);

go = imopen(img, se);
%gc = imclose(img, s);
%gm = (gc+go)/2;
dif = go-img; 
dif = dif(5:end-5, 5:end-5);

e = std(dif(:));
%e
imshow(dif+0.5), drawnow