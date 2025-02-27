from PIL import Image
import os

def text_to_binary(text):
    return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

def binary_to_text(binary):
    byte_array = bytearray(int(binary[i:i + 8], 2) for i in range(0, len(binary), 8))
    return byte_array.decode('utf-8')

def difference(original, new, outputPath, lsb_count):
    imageFinal = Image.open(new)
    imageInitial = Image.open(original)
    pixelsFinal = imageFinal.load()
    pixelsInitial = imageInitial.load()
    imageDiff = Image.new('RGB', imageFinal.size)
    pixelsDiff = imageDiff.load()

    for y in range(imageFinal.height):
        for x in range(imageFinal.width):
            rf,gf,bf = pixelsFinal[x, y]
            ri,gi,bi = pixelsInitial[x, y]
            rd = 255-abs(rf - ri)*pow(2,8-lsb_count)
            gd = 255-abs(gf - gi)*pow(2,8-lsb_count)
            bd = 255-abs(bf - bi)*pow(2,8-lsb_count)
            pixelsDiff[x, y] = (rd, gd, bd)

    imageDiff.save(outputPath)


def encode_text(image_path, text, output_path, lsb_count):
    """Encodes text into the specified least significant bits of each color channel in an image."""
    if lsb_count < 1 or lsb_count > 8:
        raise ValueError("lsb_count must be between 1 and 8")

    # Open the image
    image = Image.open(image_path)
    pixels = image.load()

    # Convert text to binary
    binary_text = text_to_binary(text)

    # Calculate the message length in bits and convert it to a 32-bit binary string
    message_length = len(binary_text)
    binary_length = format(message_length, '032b')

    # Prepend the binary length to the binary text
    binary_data = binary_length + binary_text

    binary_index = 0
    data_length = len(binary_data)

    for y in range(image.height):
        for x in range(image.width):
            if binary_index < data_length:
                # Get pixel data and unpack RGB values
                r, g, b = pixels[x, y]

                # Encode data bits into the specified least significant bits of each color channel
                if binary_index < data_length:
                    r = (r & ~((1 << lsb_count) - 1)) | int(binary_data[binary_index:binary_index + lsb_count], 2)
                    binary_index += lsb_count
                if binary_index < data_length:
                    g = (g & ~((1 << lsb_count) - 1)) | int(binary_data[binary_index:binary_index + lsb_count], 2)
                    binary_index += lsb_count
                if binary_index < data_length:
                    b = (b & ~((1 << lsb_count) - 1)) | int(binary_data[binary_index:binary_index + lsb_count], 2)
                    binary_index += lsb_count

                # Update the pixel with the modified values
                pixels[x, y] = (r, g, b)

                if binary_index >= data_length:
                    break
        if binary_index >= data_length:
            break

    # Save the encoded image
    image.save(output_path)


def decode_text(image_path, lsb_count):
    """Decodes text from the specified least significant bits of each color channel in an image."""
    if lsb_count < 1 or lsb_count > 8:
        raise ValueError("lsb_count must be between 1 and 8")

    # Open the image
    image = Image.open(image_path)
    pixels = image.load()

    binary_data = ''

    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]

            # Extract the specified least significant bits of each color channel
            binary_data += format(r & ((1 << lsb_count) - 1), f'0{lsb_count}b')
            binary_data += format(g & ((1 << lsb_count) - 1), f'0{lsb_count}b')
            binary_data += format(b & ((1 << lsb_count) - 1), f'0{lsb_count}b')

    # Extract the first 32 bits to get the message length
    binary_length = binary_data[:32]
    message_length = int(binary_length, 2)  # Convert from binary to integer

    # Extract the message bits using the decoded message length
    message_bits = binary_data[32:32 + message_length]

    # Convert binary to text and print it
    decoded_text = binary_to_text(message_bits)
    return decoded_text  # Return the decoded text if needed


with open("text.txt", "r") as f:
    text = f.read()

    # Encode and process for 'IMG_7661.png'
    encode_text('IMG_7661.png', text, 'encoded_image_cat_2.png', 2)
    with open("encoded_image_cat_2.txt", "w") as f_cat_2:
        f_cat_2.write(decode_text("encoded_image_cat_2.png", 2))
    os.remove('encoded_image_cat_2.png')  # Delete image file

    encode_text('IMG_7661.png', text, 'encoded_image_cat_4.png', 4)
    with open("encoded_image_cat_4.txt", "w") as f_cat_4:
        f_cat_4.write(decode_text("encoded_image_cat_4.png", 4))
    os.remove('encoded_image_cat_4.png')  # Delete image file

    encode_text('IMG_7661.png', text, 'encoded_image_cat_6.png', 6)
    with open("encoded_image_cat_6.txt", "w") as f_cat_6:
        f_cat_6.write(decode_text("encoded_image_cat_6.png", 6))
    os.remove('encoded_image_cat_6.png')  # Delete image file

    # Encode and process for 'IMG_6416.png'
    encode_text('IMG_6416.png', text, 'encoded_image_city_2.png', 2)
    with open("encoded_image_city_2.txt", "w") as f_city_2:
        f_city_2.write(decode_text("encoded_image_city_2.png", 2))
    os.remove('encoded_image_city_2.png')  # Delete image file

    encode_text('IMG_6416.png', text, 'encoded_image_city_4.png', 4)
    with open("encoded_image_city_4.txt", "w") as f_city_4:
        f_city_4.write(decode_text("encoded_image_city_4.png", 4))
    os.remove('encoded_image_city_4.png')  # Delete image file

    encode_text('IMG_6416.png', text, 'encoded_image_city_6.png', 6)
    with open("encoded_image_city_6.txt", "w") as f_city_6:
        f_city_6.write(decode_text("encoded_image_city_6.png", 6))
    os.remove('encoded_image_city_6.png')  # Delete image file

    # Encode and process for 'IMG_7690.png'
    encode_text('IMG_7690.png', text, 'encoded_image_sky_2.png', 2)
    with open("encoded_image_sky_2.txt", "w") as f_sky_2:
        f_sky_2.write(decode_text("encoded_image_sky_2.png", 2))
    os.remove('encoded_image_sky_2.png')  # Delete image file

    encode_text('IMG_7690.png', text, 'encoded_image_sky_4.png', 4)
    with open("encoded_image_sky_4.txt", "w") as f_sky_4:
        f_sky_4.write(decode_text("encoded_image_sky_4.png", 4))
    os.remove('encoded_image_sky_4.png')  # Delete image file

    encode_text('IMG_7690.png', text, 'encoded_image_sky_6.png', 6)
    with open("encoded_image_sky_6.txt", "w") as f_sky_6:
        f_sky_6.write(decode_text("encoded_image_sky_6.png", 6))
    os.remove('encoded_image_sky_6.png')  # Delete image file

