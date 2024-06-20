import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import json
import os
import requests

FONT_URL = 'https://raw.githubusercontent.com/matomo-org/travis-scripts/master/fonts/Verdana.ttf'
FONT_PATH = 'tmp/verdana.ttf'

def download_font():
    if not os.path.exists(FONT_PATH):
        response = requests.get(FONT_URL)
        with open(FONT_PATH, 'wb') as f:
            f.write(response.content)

def render_character_to_image(char, font_size=40):
    # Use a truetype font
    # font = ImageFont.truetype("verdana.ttf", font_size)
    # font = ImageFont.load_default()
    download_font()
    font = ImageFont.truetype(FONT_PATH, font_size)

    # Determine the size required for the character
    dummy_img = Image.new('L', (1, 1), 255)  # Dummy image to calculate text size
    draw = ImageDraw.Draw(dummy_img)
    # text_size = draw.textbbox((10, 10), "Hello, World!", font=font)
    text_size = draw.textbbox((10, 10), char, font=font)
    text_width = text_size[2] - text_size[0]
    text_height = text_size[3]
    # text_width, text_height = draw.textbbox(char, font=font)

    # Create an image large enough to hold the character
    image = Image.new('L', (text_width + 10, text_height + 10), 255)  # Add some padding around the character
    draw = ImageDraw.Draw(image)

    # Draw the character centered in the image
    draw.text(((image.width - text_width) // 2, (image.height - text_height) // 2), char, font=font, fill=0)

    # Display the image
    # image.show()
    # Convert image to an array for analysis
    image_array = np.array(image)

    # Find columns that contain dark pixels
    non_empty_columns = np.where(image_array.min(axis=0) < 128)[0]
    if non_empty_columns.any():
        # Crop the image to the min and max non-empty columns
        cropped_image = image_array[:, non_empty_columns.min():non_empty_columns.max() + 1]
        return cropped_image
    else:
        return image_array  # Return the original if no dark pixels are found


def extract_candlestick_data_from_image(image, offset=0):
    height, width = image.shape
    candlestick_data = []

    for i in range(width):
        column = image[:, i]
        black_pixels = np.where(column < 128)[0]
        if black_pixels.size > 0:
            # Find continuous segments of black pixels
            segments = np.split(black_pixels, np.where(np.diff(black_pixels) > 1)[0] + 1)
            
            if len(segments) == 3:
                middle_segment = segments[1]
                open_ = middle_segment[0] / height
                close = middle_segment[-1] / height
            else:
                longest_segment = max(segments, key=len)
                open_ = longest_segment[0] / height
                close = longest_segment[-1] / height
            
            high = np.max(black_pixels) / height
            low = np.min(black_pixels) / height
            
            candlestick_data.append([i + offset, 1-close, 1-high, 1-low, 1-open_])
            # candlestick_data.append([i + offset, open_, high, low, close])
        else:
            # Neutral values for columns with no black pixels
            candlestick_data.append([i + offset, 0.5, 0.5, 0.5, 0.5])

    return np.array(candlestick_data)

def generate_data_from_text(text):
    combined_data = np.empty((0, 5))
    offset = 0
    for char in text:
        image = render_character_to_image(char)
        data = extract_candlestick_data_from_image(image, offset)
        if data.size > 0:
            combined_data = np.vstack([combined_data, data])
        offset += image.shape[1] + 3
    return combined_data

def lambda_handler(event, context):
    print(event)
    alphabet = event['queryStringParameters'].get('text', 'abc')
    print("Alphabet: ", alphabet)
    combined_data = generate_data_from_text(alphabet)
    combined_data_list = combined_data.tolist()

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps({'data': combined_data_list})
    }