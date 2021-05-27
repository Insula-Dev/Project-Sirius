# Imports
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont


# Variables
bg_colour = (66, 141, 255)
grey_colour = (40, 40, 40)
theme_colour = (74, 60, 232)
alt_colour = (180, 80, 250)
text_colour = (255, 252, 252)
main_font = ImageFont.truetype("Resources/NHaasGroteskTXPro-55Rg.ttf", 28)
sub_font = ImageFont.truetype("Resources/NHaasGroteskTXPro-55Rg.ttf", 18)


# Functions
def add_corners(image, radius):
	"""???

	Warning: clunky"""

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

def mask_circle_solid(pil_img, background_color, blur_radius, offset=0):
	"""???

	From https://note.nkmk.me/en/python-pillow-square-circle-thumbnail/

	Warning: clunky"""

	background = Image.new(pil_img.mode, pil_img.size, background_color)

	offset = blur_radius * 2 + offset
	mask = Image.new("L", pil_img.size, 0)
	draw = ImageDraw.Draw(mask)
	draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
	mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
	return Image.composite(pil_img, background, mask)

def generate_rank_card(profile_picture_url, name, rank, percentage):
	"""Generates the rank card."""

	# Request profile picture and save it as card.png
	with requests.get(profile_picture_url) as request:
		with open("card.png", "wb") as file:
			file.write(request.content)

	# Prepare the profile picture using PIL
	with Image.open("card.png") as profile_picture:
		profile_picture = profile_picture.resize((150, 150), Image.NEAREST)  # Simplify? Size?

	# Prepare the card
	card = Image.new(mode="RGBA", size=(500, 200), color=bg_colour)
	card = add_corners(card, 15)

	# Give the profile picture a border
	pfp_border = Image.new("RGB", (152, 152), grey_colour)  # Make RGBA
	pfp_border.paste(profile_picture, (1, 1))
	pfp_border = mask_circle_solid(pfp_border, bg_colour, 2)

	# Add the profile picture to the card
	card.paste(pfp_border, (25, 25))

	# Add the text to the card
	drawn = ImageDraw.Draw(card)
	drawn.text((200, 25), "Rank: " + str(rank), text_colour, font=main_font)
	drawn.text((200, 55), name, text_colour, font=sub_font)
	drawn.text((200, 78), str(percentage) + "%", theme_colour, font=sub_font)

	# Add the progress bar to the card
	bar_background = Image.new(mode="RGBA", size=(275, 30), color=grey_colour)
	#bar_background = add_corners(bar_background, 10)  # Make round-cornered
	bar_overlay = Image.new(mode="RGBA", size=(round(265 * percentage / 100), 20), color=alt_colour)
	#bar_overlay = add_corners(bar_overlay, 10)  # Make round-cornered
	card.paste(bar_background, (200, 100))
	card.paste(bar_overlay, (205, 105))
	card.save("card.png")


# Main body
if __name__ == "__main__":
	generate_rank_card("https://i.redd.it/s9biyhs4lix61.jpg", "IkelosOne", 68, 12)


"""
Problems:

- Gif profile pictures
- Make card.png a variable instead of a file
- add_corners and mask_circle_solid are a clunky heuristic
- pfp is not centred laterally or vertically on card
- Make card_size a variable and base the sizes off it
"""
