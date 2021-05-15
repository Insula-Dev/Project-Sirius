from PIL import Image, ImageDraw, ImageFilter, ImageFont
import requests
"""
width = 400
height = 300

img  = Image.new( mode = "RGB", size = (width, height), color = (200, 40, 200) )
img.show()
"""
bg_colour = (20,20,30)

def mask_circle_solid(pil_img, background_color, blur_radius, offset=0): # From https://note.nkmk.me/en/python-pillow-square-circle-thumbnail/
    background = Image.new(pil_img.mode, pil_img.size, background_color)

    offset = blur_radius * 2 + offset
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    return Image.composite(pil_img, background, mask)
def makeRankCard(profile_url,rank):
    with requests.get(profile_url) as r:
        img_data = r.content
    profilePic = Image.open("Untitled.png")
    profilePic.show()

    card = Image.new(mode="RGB",size=(500,200),color=bg_colour)
    card.show()
    profilePic = mask_circle_solid(profilePic, bg_colour, 1)

    card.paste(profilePic,(20,20))
    card.show()

    drawn = ImageDraw.Draw(card)
    font = font = ImageFont.truetype("./arial.ttf", 30)
    drawn.text((160, 20),"Rank: "+str(rank),(255,255,255),font=font)
    card.show()
    return card