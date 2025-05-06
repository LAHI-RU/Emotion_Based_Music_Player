from PIL import Image, ImageDraw, ImageFont
import os

# Create the directory if it doesn't exist
if not os.path.exists("static/img"):
    os.makedirs("static/img")

# Create a blank image with a green background (Spotify colors)
img = Image.new('RGB', (250, 250), color = (29, 185, 84))
d = ImageDraw.Draw(img)

# Add text with default font
font = ImageFont.load_default()

# Center the text
text = "Music Player"
text_width = d.textlength(text, font=font)
text_position = ((250 - text_width) // 2, 120)

# Draw the text
d.text(text_position, text, fill=(255, 255, 255), font=font)

# Save the image
img.save('static/img/default-album.png')

print("Default album image created in static/img/default-album.png")