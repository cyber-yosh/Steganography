import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import sys

def text_to_binary(text):
    return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

def binary_to_text(binary):
    byte_array = bytearray(int(binary[i:i + 8], 2) for i in range(0, len(binary), 8))
    return byte_array.decode('utf-8')

def sobel_filter(image):
    # Apply Sobel filter to get edge gradients
    sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    sobel_magnitude = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
    return sobel_magnitude

def find_continuous_length_horizontal2(sobel_binary, x, y, threshold=1):
    height, width = sobel_binary.shape
    if not (0 <= y < height and 0 <= x < width):
        return -1
    length = 0
    # Traverse horizontally to the right
    for i in range(x, width):
        if sobel_binary[y, i] >= threshold:  # Check if pixel is part of an edge (1)
            length += 1
        else:
            break

    return length

def embed_message(message, img_path, num_bits, output_path):
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    img_gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    coords = []
    coords.append([0, 0])
    sobel_mask = sobel_filter(img_gray)
    _, sobel_binary = cv2.threshold(sobel_mask, 50, 255, cv2.THRESH_BINARY)

    message_binary = text_to_binary(message)
    x_coord_placeholder = format(0, '012b')  # 12-bit binary for x
    y_coord_placeholder = format(0, '012b')

    height, width, channels = img.shape
    total_bits = 0

    for y in range(height):
        x=0
        if y==0:
            x+=24
        if len(message_binary) == 0:
            break
        while x < width:
            if len(message_binary) == 0:
                break
            #continuous_length = find_continuous_length_horizontal(sobel_mask, x, y)
            continuous_length = find_continuous_length_horizontal2(sobel_binary, x, y)
            if continuous_length == -1:
                raise "Error: Cannot Fit Message Into Image"
            if continuous_length >=(8-num_bits)*12:
                #store the coordinates for later use
                coords.append([y, x])
                #message length
                message_length = continuous_length*3*num_bits-40
                if message_length > len(message_binary):
                    message_length = len(message_binary)
                message_length_bits = format(message_length, '016b')
                #create binary data representation for this patch of high variance
                binary_data = x_coord_placeholder + y_coord_placeholder + message_length_bits + message_binary[:message_length]
                message_binary = message_binary[message_length:]
                binary_index = 0
                for z in range(x, x + continuous_length):
                    b, g, r = img[y, z]

                    # Modify the LSBs of the Blue channel (b)
                    if binary_index < len(binary_data):
                        bits = int(binary_data[binary_index:binary_index + num_bits], 2)  # Get num_bits bits to embed
                        mask = (1 << num_bits) - 1  # Create mask for num_bits LSBs
                        b = np.uint8((b & (~mask & 0xFF)) | (bits & mask))  # Clear the LSBs and set the new bits
                        binary_index += num_bits

                    # Modify the LSBs of the Green channel (g)
                    if binary_index < len(binary_data):
                        bits = int(binary_data[binary_index:binary_index + num_bits], 2)  # Get num_bits bits to embed
                        mask = (1 << num_bits) - 1  # Create mask for num_bits LSBs
                        g = np.uint8((g & (~mask & 0xFF)) | (bits & mask))  # Clear the LSBs and set the new bits
                        binary_index += num_bits

                    # Modify the LSBs of the Red channel (r)
                    if binary_index < len(binary_data):
                        bits = int(binary_data[binary_index:binary_index + num_bits], 2)  # Get num_bits bits to embed
                        mask = (1 << num_bits) - 1  # Create mask for num_bits LSBs
                        r = np.uint8((r & (~mask & 0xFF)) | (bits & mask))  # Clear the LSBs and set the new bits
                        binary_index += num_bits

                        # Move to the next bit
                    # Update the pixel with the modified color channels
                    img[y, z] = (b, g, r)
                x+=continuous_length

            else:
                x+=1
    coords.append([0, 0])
    for coord_index in range(0, len(coords) - 1):
        curr_x = coords[coord_index][1]
        curr_y = coords[coord_index][0]
        next_x = coords[coord_index + 1][1]
        next_y = coords[coord_index + 1][0]

        x_coord_binary = format(next_x, '012b')
        y_coord_binary = format(next_y, '012b')
        binary_data = x_coord_binary + y_coord_binary
        binary_index = 0

        for z in range(curr_x, curr_x + 8):
            b, g, r = img[curr_y, z]

            # Blue channel
            if binary_index < len(binary_data):
                old_b = b
                bits = int(binary_data[binary_index:binary_index + num_bits], 2)
                mask = (1 << num_bits) - 1
                b = np.uint8((b & (~mask & 0xFF)) | bits)
                binary_index += num_bits

            # Green channel
            if binary_index < len(binary_data):
                old_g = g
                bits = int(binary_data[binary_index:binary_index + num_bits], 2)
                mask = (1 << num_bits) - 1
                g = np.uint8((g & (~mask & 0xFF)) | bits)
                binary_index += num_bits

            # Red channel
            if binary_index < len(binary_data):
                old_r = r
                bits = int(binary_data[binary_index:binary_index + num_bits], 2)
                mask = (1 << num_bits) - 1
                r = np.uint8((r & (~mask & 0xFF)) | bits)
                binary_index += num_bits

            img[curr_y, z] = (b, g, r)
    cv2.imwrite(output_path+".png", img)
    return img


# And in the decode function:
def decode_message(cv_image, num_bits=2):
    message = ""
    curr_x, curr_y = 0, 0

    while True:
        binary_message = ""
        bits_collected = 0

        # Ensure coordinates are within bounds
        if curr_y >= cv_image.shape[0] or curr_x >= cv_image.shape[1]:
            break

        bits_per_pixel = 3 * num_bits
        pixels_needed_for_metadata = (40 + bits_per_pixel - 1) // bits_per_pixel

        if curr_x + pixels_needed_for_metadata >= cv_image.shape[1]:
            break

        # Collect the next 40 bits for metadata
        for z in range(curr_x, curr_x + pixels_needed_for_metadata):
            pixel = cv_image[curr_y, z]
            for channel in range(3):
                if bits_collected >= 40:
                    break
                mask = (1 << num_bits) - 1
                bits = pixel[channel] & mask
                binary_message += format(bits, f'0{num_bits}b')
                bits_collected += num_bits

        # Extract metadata
        next_x = int(binary_message[:12], 2)
        next_y = int(binary_message[12:24], 2)
        message_length = int(binary_message[24:40], 2)

        if curr_y == 0 and curr_x == 0:
            curr_x = next_x
            curr_y = next_y
            continue

        # Calculate pixels needed for full message
        total_bits_needed = 40 + message_length
        pixels_needed = (total_bits_needed + bits_per_pixel - 1) // bits_per_pixel

        # Check if we have enough space to read the message
        if curr_x + pixels_needed > cv_image.shape[1]:
            break

        # Collect the actual message bits
        binary_message = ""
        bits_collected = 0
        for z in range(curr_x, curr_x + pixels_needed):
            pixel = cv_image[curr_y, z]
            for channel in range(3):
                if bits_collected >= total_bits_needed:
                    break
                mask = (1 << num_bits) - 1
                bits = pixel[channel] & mask
                binary_message += format(bits, f'0{num_bits}b')
                bits_collected += num_bits

        # Append the extracted message
        message += binary_message[40:40 + message_length]

        # Stop if we reach the end of the message
        if next_x == 0 and next_y == 0:
            break

        # Update coordinates for the next block
        curr_x, curr_y = next_x, next_y

    # Convert the binary message to text
    return binary_to_text(message)

x= embed_message("Hello World ! ™", "IMG_7661.png", 2, "ENCODED_IMG")
print(decode_message(x, 2))