library(tesseract)
library(dplyr)
library(png)
library(shape)
library(magick)

img <- readPNG('C:/Users/Tim/Desktop/1ST.ALAMEDAEARLYSHIFT.140227-MAN_1.png')

eng <- tesseract("eng")
text <- tesseract::ocr('C:/Users/Tim/Desktop/1ST.ALAMEDAEARLYSHIFT.140227-MAN.pdf')
text <- tesseract::ocr_data('C:/Users/Tim/Desktop/1ST.ALAMEDAEARLYSHIFT.140227-MAN.pdf')
cat(text)

bbox <- text$bbox[2]
coords <- as.integer(unlist(strsplit(bbox,',')))

#Set up the plot area
#plot(0:5100, 0:6600, type='n', main="Plotting Over an Image", xlab="x", ylab="y")
emptyplot(xlim = c(0, 5100), ylim = c(0,6600), asp = 1, frame.plot = FALSE)
rasterImage(img, 0, 0, 5100, 6600)
rectange <- rect(coords[1], coords[2], coords[3], coords[4])

# use magick to draw over image
"https://cran.r-project.org/web/packages/magick/vignettes/intro.html#drawing_and_graphics"

# border removal idea
"https://stackoverflow.com/questions/47775622/r-border-removal-for-ocr"
"https://stackoverflow.com/questions/48641646/remove-lines-of-particular-size-from-image"
"https://stackoverflow.com/questions/33949831/whats-the-way-to-remove-all-lines-and-borders-in-imagekeep-texts-programmatic"

# magick test
volct_img <- image_read('C:/Users/Tim/Desktop/1ST.ALAMEDAEARLYSHIFT.140227-MAN_1.png') %>%
  image_quantize(colorspace = "gray") %>%
  image_negate() 

img <- image_read('C:/Users/Tim/Desktop/test.png')
img_data <- ocr(img, engine = tesseract('eng', options = list(tessedit_char_whitelist = '0123456789.-',
                                                              tessedit_pageseg_mode = 'auto',
                                                              textord_tabfind_find_tables = '1',
                                                              textord_tablefind_recognize_tables = '1')))
cat(img_data)