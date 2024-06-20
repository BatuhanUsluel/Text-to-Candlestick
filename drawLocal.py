import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
from draw import generate_data_from_text, render_character_to_image, extract_candlestick_data_from_image
import numpy as np

def plot_candlestick(data):
    # Increase the figure size for better visibility
    fig, ax = plt.subplots(figsize=(40, 8))  # You can adjust the size as needed
    candlestick_ohlc(ax, data, width=0.3, colorup='g', colordown='r', alpha=0.75)  # Adjust the width of the candlesticks

    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.set_title('Candlestick Chart for the Alphabet')
    plt.xticks(np.arange(0, len(data), step=50), rotation=90)  # Adjust ticks if necessary
    plt.show()

# Generate and plot the candlestick chart for a given character
char = 'A'
image = render_character_to_image(char)
data = extract_candlestick_data_from_image(image)
plot_candlestick(data)

# Generate the candlestick data for the whole alphabet
# alphabet = 'abc'
# combined_data = np.empty((0, 5))
# offset = 0

# for char in alphabet:
#     image = render_character_to_image(char)
#     data = extract_candlestick_data_from_image(image, offset)
#     if data.size > 0:
#         combined_data = np.vstack([combined_data, data])
#     offset += image.shape[1] + 10  # Add a gap of 10 pixels between characters

# plot_candlestick(combined_data)