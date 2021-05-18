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
bg_colour = (81,86,95)
grey_colour = (40,40,40)
theme_colour = (90,40,220)

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

def makeRankCard(profile_url,rank,percentage_to_rank):
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
    profilePic = mask_circle_solid(profilePic, bg_colour, 1)

    card.paste(profilePic,(20,20))
    #card.show()

    drawn = ImageDraw.Draw(card)
    font = ImageFont.truetype("./comic.ttf", 28)
    drawn.text((180, 20),"Rank: "+str(math.floor(rank)),(230,230,255),font=font)
    #card.show()

    print("Percentage to rank "+str(percentage_to_rank))
    barBackground = Image.new(mode="RGB", size=(300, 20), color=grey_colour)
    #barBackground = add_corners(barBackground, barBackground, rad=10)
    barOverlay = Image.new(mode="RGB", size=(round(300*percentage_to_rank/100), 20), color=theme_colour)
    #barOverlay = add_corners(barOverlay, barOverlay, rad=10)
    card.paste(barBackground,(180,110))
    card.paste(barOverlay,(180,110))
    card.save("card.png")

if __name__ == '__main__':
    makeRankCard("https://cdn.discordapp.com/avatars/258284765776576512/72490d3f18dafda1528ad68fa421d1dc.webp?size=128",3)