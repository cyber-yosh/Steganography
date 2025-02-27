import cv2
from PIL import Image
import numpy as np

def calculate_psnr(cover_path, stego_path):
    cover_image = cv2.imread(cover_path)
    stego_image = cv2.imread(stego_path)

    if cover_image is None or stego_image is None:
        raise ValueError("One or both image paths are invalid or the files do not exist.")

    # Ensure both images have the same dimensions
    if cover_image.shape != stego_image.shape:
        raise ValueError("Cover image and stego image must have the same dimensions.")

    # Calculate the Mean Squared Error (MSE)
    mse = np.mean((cover_image - stego_image) ** 2)

    if mse == 0:
        return float('inf')  # PSNR is infinite if MSE is zero (images are identical)

    # Calculate PSNR
    max_pixel_value = 255.0  # Maximum value for a pixel in 8-bit images
    psnr = 20 * np.log10(max_pixel_value / np.sqrt(mse))

    return psnr

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