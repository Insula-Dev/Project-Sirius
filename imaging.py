# Imports
import time

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat


# Variables
card_scale = 2
bg_colour = (66, 141, 255)
grey_colour = (40, 40, 40)
theme_colour = (50,200,200)
alt_colour = (180, 80, 250)
text_colour = (255, 252, 252)
main_font = ImageFont.truetype("Resources/NHaasGroteskTXPro-55Rg.ttf", 28*card_scale)
sub_font = ImageFont.truetype("Resources/NHaasGroteskTXPro-55Rg.ttf", 18*card_scale)


# Functions
def add_corners(image, radius):
	"""???	Warning: clunky"""

	circle = Image.new('L', (radius * 2, radius * 2), 0)
	draw = ImageDraw.Draw(circle)
	draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
	alpha = Image.new('L', image.size, "white")
	w, h = image.size
	alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
	alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
	alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
	alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
	image.putalpha(alpha)

	return image

def mask_circle_solid(pil_img, background_colour, blur_radius, offset=0):
	"""???

	From https://note.nkmk.me/en/python-pillow-square-circle-thumbnail/

	Warning: clunky"""

	background = Image.new(pil_img.mode, pil_img.size, background_colour)

	offset = blur_radius * 2 + offset
	mask = Image.new("L", pil_img.size, 0)
	draw = ImageDraw.Draw(mask)
	draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
	mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
	return Image.composite(pil_img, background, mask)

def get_picture(url):
	# Request profile picture and save it as card.png
	with requests.get(url) as request:
		with open("card.png", "wb") as file:
			file.write(request.content)

	image = None # To let card get closed
	with Image.open("card.png") as picture:
		image = picture
	return image

def generate_level_card(profile_picture_url, name, rank, percentage, server_picture=None):
	"""Generates the level card."""

	global text_colour
	global theme_colour

	# Prepare the profile picture using PIL
	profile_picture = get_picture(profile_picture_url)
	profile_picture = profile_picture.resize((150*card_scale, 150*card_scale), Image.NEAREST)  # Simplify? Size?
	bg_colour = tuple(ImageStat.Stat(profile_picture).median) # Makes background colour the median of the profile picture

	# Prepare the card
	card = Image.new(mode="RGBA", size=(500*card_scale, 200*card_scale), color=bg_colour)
	card = add_corners(card, 15*card_scale)

	# Give the profile picture a border
	pfp_border = Image.new("RGB", (152*card_scale, 152*card_scale), grey_colour)  # Make RGBA
	pfp_border.paste(profile_picture, (1, 1))
	pfp_border = mask_circle_solid(pfp_border, bg_colour, 2)
	#pfp_border.show()

	# Add the profile picture to the card
	card.paste(pfp_border, (25*card_scale, 25*card_scale))

	# Add the text to the card
	drawn = ImageDraw.Draw(card)
	if bg_colour[0] > 150 and bg_colour[1] > 150 and bg_colour[2] > 150: # Makes text dark if background if background is "light"
		text_colour = (0, 0, 0)
		theme_colour = (74, 60, 232)
	drawn.text((200*card_scale, 25*card_scale), "Level: " + str(rank), text_colour, font=main_font)
	drawn.text((200*card_scale, 55*card_scale), name, text_colour, font=sub_font)
	drawn.text((200*card_scale, 78*card_scale), str(percentage) + "%", theme_colour, font=sub_font)

	# Add the progress bar to the card
	bar_background = Image.new(mode="RGBA", size=(275*card_scale, 30*card_scale), color=grey_colour)
	#bar_background = add_corners(bar_background, 10)  # Make round-cornered
	bar_overlay = Image.new(mode="RGBA", size=(round(265 * card_scale * percentage / 100), 20*card_scale), color=alt_colour)
	#bar_overlay = add_corners(bar_overlay, 10)  # Make round-cornered
	card.paste(bar_background, (200*card_scale, 100*card_scale))
	card.paste(bar_overlay, (205*card_scale, 105*card_scale))
	#card.show()

	# Adds server profile picture if provided
	if server_picture != None:
		server_picture = get_picture(server_picture)
		server_picture = server_picture.resize((30 * card_scale, 30 * card_scale), Image.NEAREST)
		server_picture = mask_circle_solid(server_picture, bg_colour, 2)
		#server_picture.show()
		card.paste(server_picture, (445 * card_scale, 25 * card_scale))
	card.save("card.png")


"""
Problems:

- Gif profile pictures
- Make card.png a variable instead of a file
- add_corners and mask_circle_solid are a clunky heuristic
- pfp is not centred laterally or vertically on card
- Make card_size a variable and base the sizes off it
"""


if __name__ == '__main__':
	im = get_picture("https://cdn.discordapp.com/icons/755420029482303488/a_c96342be77385d12d99d8b07c1d622d0.webp?size=96")
	im.show()
	#generate_level_card("https://cdn.discordapp.com/guilds/834213187468394517/users/258284765776576512/avatars/5e3a063c3b7bcb5366d514cf08ad9272.webp?size=80","Arun",1,20)

	# Average 0.12635878966666664 for scale 2
	# Average 0.10261608966666663 for scale 1