from os import path
from os import remove as rm_file
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont


def fetch_random_nature_image(width=1080, height=1920):
    """
    Fetches a random nature image from Unsplash.

    Parameters:
        width (int): The desired width of the image.
        height (int): The desired height of the image.

    Returns:
        PIL.Image.Image: The fetched image.
    """
    url = f"https://source.unsplash.com/featured/{width}x{height}/?nature"
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        return img

    return print(f"Failed to fetch image. Status code: {response.status_code}")


def download_font(url, save_path):
    """
    Downloads a font file from the specified URL and saves it to the given path,
    only if the font file does not already exist in the path.

    Parameters:
        url (str): The URL of the font file to download.
        save_path (str): The path to save the downloaded font file.
    """

    if not path.exists(save_path):
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=128):
                    f.write(chunk)
            print(f"Font downloaded successfully at: {save_path}")
        else:
            print(f"Failed to download font from {url}")
    else:
        print(f"Font already exists at: {save_path}")


def generate_random_quote():
    """
    Generates a random quote and author using the quotable API.

    Returns:
        tuple: A tuple containing a random quote and its author.
    """
    try:
        response = requests.get("http://api.quotable.io/random?minLength=150")
        if response.status_code == 200:
            data = response.json()
            return (data["content"], data["author"])
        else:
            print(f"Failed to fetch quote. Status code: {response.status_code}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None, None


def add_quote_and_author(
    image,
    quote,
    author,
    quote_font_path,
    author_font_path,
    quote_font_size=60,
    author_font_size=40,
    font_color=(255, 255, 255),
    padding=50,
    opacity=0.6,
    corner_radius=20,
    text_box_padding=20,
):
    """
    Adds a quote and author to the given image with a black translucent box behind the text.

    Parameters:
        image (PIL.Image.Image): The image to add text to.
        quote (str): The quote text to be added.
        author (str): The author text to be added.
        font_path (str): The path to the font file.
        quote_font_size (int): The font size for the quote text.
        author_font_size (int): The font size for the author text.
        font_color (tuple): The RGB color of the text (default is white).
        padding (int): Padding between the image border and the text.
        opacity (float): Opacity of the translucent box (default is 0.6).
        corner_radius (int): Radius of the rounded corners of the box (default is 20).
        text_box_padding (int): Padding between the text and the translucent box.

    Returns:
        PIL.Image.Image: The image with the added text and translucent box.
    """
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # Load fonts
    quote_font = ImageFont.truetype(quote_font_path, quote_font_size)
    author_font = ImageFont.truetype(author_font_path, author_font_size)

    # Calculate max quote width based on image width and padding
    max_quote_width = width - 2 * (padding + text_box_padding)

    # Wrap quote text to fit within max_quote_width
    wrapped_quote = ""
    words = quote.split()
    line = ""
    for word in words:
        if draw.textsize(line + word, font=quote_font)[0] <= max_quote_width:
            line += word + "  "
        else:
            wrapped_quote += line + "\n"
            line = word + "  "
    wrapped_quote += line  # Add the last line

    # Calculate text dimensions
    wrapped_quote_width, wrapped_quote_height = draw.textsize(
        wrapped_quote, font=quote_font
    )
    author_width, author_height = draw.textsize(author, font=author_font)

    # Calculate text positions
    wrapped_quote_position = (
        (width - wrapped_quote_width) // 2,
        (height - wrapped_quote_height - author_height - 2 * padding) // 2 + padding,
    )
    author_position = (
        (width - author_width) // 2,
        (height + wrapped_quote_height + author_height + padding) // 2,
    )

    # Calculate box dimensions
    box_left = padding
    box_top = wrapped_quote_position[1] - padding
    box_right = width - padding
    box_bottom = author_position[1] + author_height + padding

    # Create an overlay with the same size as the original image
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))

    # Draw rounded rectangle on the overlay
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        [(box_left, box_top), (box_right, box_bottom)],
        fill=(0, 0, 0, int(255 * opacity)),
        outline=None,
        width=0,
        radius=corner_radius,
    )

    # Alpha composite the overlay with the image
    image = Image.alpha_composite(image.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(image)

    draw.multiline_text(
        (wrapped_quote_position[0], wrapped_quote_position[1] - text_box_padding),
        wrapped_quote,
        font=quote_font,
        fill=font_color,
    )

    draw.text(author_position, f"- {author}", font=author_font, fill=font_color)

    return image


def save_nature_image_with_quote(output_path="output_image.png"):
    """
    Fetches a random nature image from Unsplash, generates a random quote and author,
    adds the quote and author to the image using the specified font, and saves the resulting image.

    Parameters:
        output_path (str): The path to save the resulting image.
    """
    image = fetch_random_nature_image()

    quote_font_url = "https://github.com/google/fonts/raw/main/ofl/indieflower/IndieFlower-Regular.ttf"
    quote_font_path = "IndieFlower-Regular.ttf"
    download_font(quote_font_url, quote_font_path)

    author_font_url = "https://github.com/georgmartius/lpzrobots/raw/master/ode_robots/osg/data/fonts/times.ttf"
    author_font_path = "times.ttf"
    download_font(author_font_url, author_font_path)

    quote, author = generate_random_quote()

    image_with_text = add_quote_and_author(
        image, quote, author, quote_font_path, author_font_path
    )
    image_with_text = image_with_text.convert("RGB")

    image_with_text.save(output_path)
    print(f"Image with quote saved successfully at: {output_path}")
