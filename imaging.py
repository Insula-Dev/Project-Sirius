import math

import PIL.Image
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import requests
"""
width = 400
height = 300

img  = Image.new( mode = "RGB", size = (width, height), color = (200, 40, 200) )
img.show()
"""
#bg_colour = (20,20,30)
bg_colour = (66,141,255)
grey_colour = (40,40,40)
theme_colour = (74,60,232)
alt_colour = (180,80,250)
text_colour = (255,252,252)

def mask_circle_solid(pil_img, background_color, blur_radius, offset=0): # From https://note.nkmk.me/en/python-pillow-square-circle-thumbnail/
    background = Image.new(pil_img.mode, pil_img.size, background_color)

    offset = blur_radius * 2 + offset
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
    return Image.composite(pil_img, background, mask)

def add_corners(self, im, rad=100):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, "white")
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def makeRankCard(profile_url,rank,percentage_to_rank,name=""):
    with requests.get(profile_url) as r:
        img_data = r.content
    with open('card.png', 'wb') as img:
        img.write(img_data)
    profilePic = Image.open("card.png")
    profilePic = profilePic.resize((150,150),PIL.Image.NEAREST)
    #profilePic.show()

    card = Image.new(mode="RGB",size=(500,200),color=bg_colour)
    card = add_corners(card,card,rad=15)
    #card.show()
    #ppBorder = mask_circle_solid(Image.new("RGB",(160,160),grey_colour),bg_colour,1)
    profilePic = mask_circle_solid(profilePic, bg_colour, 1)

    #card.paste(ppBorder,(15,15))
    card.paste(profilePic,(20,20))
    #card.show()

    drawn = ImageDraw.Draw(card)
    mainFont = ImageFont.truetype("./comic.ttf", 28)
    subFont = ImageFont.truetype("./comic.ttf", 18)
    drawn.text((180, 20),"Rank: "+str(math.floor(rank)),text_colour,font=mainFont)
    drawn.text((180, 50), name, text_colour, font=subFont)
    drawn.text((180, 80), str(percentage_to_rank)+"%", theme_colour, font=subFont)
    #card.show()

    print("Percentage to rank "+str(percentage_to_rank))
    barBackground = Image.new(mode="RGB", size=(310, 30), color=grey_colour)
    #barBackground = add_corners(barBackground, barBackground, rad=10)
    barOverlay = Image.new(mode="RGB", size=(round(300*percentage_to_rank/100), 20), color=alt_colour)
    #barOverlay = add_corners(barOverlay, barOverlay, rad=10)
    card.paste(barBackground,(175,105))
    card.paste(barOverlay,(180,110))
    card.save("card.png")

if __name__ == '__main__':
    makeRankCard("https://cdn.discordapp.com/avatars/258284765776576512/72490d3f18dafda1528ad68fa421d1dc.webp?size=128",3)