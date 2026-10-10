# Imports
import math
import time
from io import BytesIO
import random

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
	try:
		# Request profile picture and save it as card.png
		response = requests.get(url)
		response.raise_for_status()  # Raise an HTTPError for bad responses
		with open("card.png", "wb") as file:
			file.write(response.content)

		# Open the image file
		with Image.open("card.png") as picture:
			image = picture.copy()  # Copy the image to avoid closing it
		return image
	except requests.RequestException as e:
		print(f"Error downloading image: {e}")
		return None
	except IOError as e:
		print(f"Error opening image: {e}")
		return None

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

def lossy(image: Image.Image, quality: int = 10) -> Image.Image:
	"""Lossy compress the image badly. This is a joke function more than something useful."""

	# Save the image to a BytesIO object with lossy compression
	buffer = BytesIO()
	image.convert("RGB").save(buffer, format="JPEG", quality=quality)
	buffer.seek(0)

	# Open the compressed image from the BytesIO object
	compressed_image = Image.open(buffer)

	return compressed_image

def wave(
		image: Image.Image,
		horizontal_amplitude: int = 10,
		horizontal_wavelength: int = 100,
		vertical_amplitude: int = 5,
		vertical_wavelength: int = 150,
	) -> Image.Image:
		if horizontal_wavelength <= 0 or vertical_wavelength <= 0:
			raise ValueError("Wave wavelengths must be greater than zero")
		# Shift each row horizontally according to its y position.
		if horizontal_amplitude:
			horizontally_waved = Image.new("RGBA", image.size, (255, 255, 255, 0))
			for y in range(image.height):
				offset = round(horizontal_amplitude * math.sin(2 * math.pi * y / horizontal_wavelength))
				row = image.crop((0, y, image.width, y + 1))
				horizontally_waved.paste(row, (offset, y))
		else:
			horizontally_waved = image
	
		# Shift each column vertically according to its x position.
		if vertical_amplitude:
			vertically_waved = Image.new("RGBA", image.size, (255, 255, 255, 0))
			for x in range(image.width):
				offset = round(vertical_amplitude * math.sin(2 * math.pi * x / vertical_wavelength))
				column = horizontally_waved.crop((x, 0, x + 1, image.height))
				vertically_waved.paste(column, (x, offset))
			image = vertically_waved
		else:
			image = horizontally_waved

		return image

def wobble(image: Image.Image) -> Image.Image:
	"""Randomly waves image with moderate amplitude and wavelength and crops in to keep the central portion."""

	cropped_width = int(image.width // 1.2)
	cropped_height = int(image.height // 1.2)
	image = wave(image, horizontal_amplitude=random.randint(3, 7), horizontal_wavelength=random.randint(40, 80), vertical_amplitude=random.randint(3, 7), vertical_wavelength=random.randint(40, 80))
	image = wave(image, horizontal_amplitude=random.randint(3, 7), horizontal_wavelength=random.randint(40, 80), vertical_amplitude=random.randint(3, 7), vertical_wavelength=random.randint(40, 80))
	left = int((image.width - cropped_width) // 1.2)
	top = int((image.height - cropped_height) // 1.2)
	right = left + cropped_width
	bottom = top + cropped_height
	return image.crop((left, top, right, bottom))

def flagify(
		image: Image.Image
	) -> Image.Image:
	"""Turn an image into a flag with independently adjustable horizontal and vertical waves."""

	# Load the flagpost image
	try:
		flagpost = Image.open("flagpost.png")
	except FileNotFoundError:
		print("Error: flagpost.png not found.")
		return image

	# Resize image to be 1/3 the height of the flagpost
	desired_height = flagpost.height // 3
	image = image.resize((int(image.width * desired_height / image.height), desired_height), Image.NEAREST)

	# Paste the image onto a slightly larger canvas to accommodate the waving effect
	image_with_space_around = Image.new("RGBA", (image.width + 20, image.height + 20), (255, 255, 255, 0))
	image_with_space_around.paste(image, (10, 10))
	image = image_with_space_around

	# Create a new image with a white background
	flag_width = image.width + flagpost.width  # Add space for the flagpole (flagpost.png is 150px x 989px)
	flagged_image = Image.new("RGBA", (flag_width, flagpost.height), (255, 255, 255, 255))  # White background
	flagged_image.paste(flagpost, (10, 0), flagpost)  # Preserve flagpost transparency when compositing

	# Apply the wave effect
	image = wave(image, horizontal_amplitude=2, horizontal_wavelength=90, vertical_amplitude=7, vertical_wavelength=image.width//4)
	
	# Paste the flagpost, then overlay the waved image so the image is on top
	flagged_image.paste(image, (flagpost.width-60, 20), image)  # Use image alpha as mask so transparent pixels don't erase backdrop

	return flagged_image

def pixelate(image: Image.Image, pixel_size: int=10) -> Image.Image:
	# Resize the image to a smaller size and then scale it back up
	small = image.resize(
		(image.width // pixel_size, image.height // pixel_size),
		Image.NEAREST
	)
	pixelated = small.resize(image.size, Image.NEAREST)
	return pixelated

"""
Problems:

- Gif profile pictures
- Make card.png a variable instead of a file
- add_corners and mask_circle_solid are a clunky heuristic
- pfp is not centred laterally or vertically on card
- Make card_size a variable and base the sizes off it
"""


if __name__ == '__main__':
	im = get_picture("https://cdn.discordapp.com/guilds/834213187468394517/users/258284765776576512/avatars/5e3a063c3b7bcb5366d514cf08ad9272.webp?size=80")
	# im.show()
	card_image = Image.open("card.png")
	
	# Flagify the card.png image
	card_image = pixelate(card_image)
	card_image.show()

	# Test compressing the card.png image
	card_image = lossy(card_image, quality=2)


	card_image.close()

	# Average 0.12635878966666664 for scale 2
	# Average 0.10261608966666663 for scale 1