import math
from pathlib import Path
from typing import IO, Iterator, TypeAlias

from PIL import Image
from PIL.Image import Image as ImageType

StrOrPath: TypeAlias = str | Path


def find_optimal_dimensions(min_pixels: int) -> tuple[int, int]:
    """
    Finds the optimal image dimensions starting from a minimum required pixel count.
    """
    pixels_count = min_pixels
    while True:
        start_width = int(math.sqrt(pixels_count))
        for width in range(start_width, 0, -1):
            if pixels_count % width == 0:
                height = pixels_count // width
                return (height, width)
        pixels_count += 1


def file_to_image(
    file_path: StrOrPath,
    output_image_path: StrOrPath,
) -> None:
    """
    Encodes any file into a PNG image, ensuring optimal dimensions with no wasted space.
    """
    file: IO[bytes]
    with open(file_path, "rb") as file:
        file_data: bytes = file.read()

    file_size_bytes: bytes = len(file_data).to_bytes(8, "big")
    data_to_encode: bytes = file_size_bytes + file_data

    min_pixels_needed: int = math.ceil(len(data_to_encode) / 3)
    width, height = find_optimal_dimensions(min_pixels_needed)
    total_bytes_needed: int = width * height * 3
    padded_data: bytes = data_to_encode.ljust(total_bytes_needed, b'\x00')

    img: ImageType = Image.new("RGB", (width, height))
    pixels = img.load()

    byte_iterator: Iterator[int] = iter(padded_data)
    for y in range(height):
        for x in range(width):
            pixels[x, y] = (
                next(byte_iterator),
                next(byte_iterator),
                next(byte_iterator)
            )

    img.save(output_image_path, "PNG")


def image_to_file(
    image_path: StrOrPath,
    output_file_path: StrOrPath,
) -> None:
    """
    Decodes and restores the original file from an encoded image.
    """
    img: ImageType = Image.open(image_path)
    extracted_bytes: bytes = img.tobytes()

    if len(extracted_bytes) < 8:
        raise ValueError("Not enough data in image to parse file size.")

    file_size_bytes: bytes = extracted_bytes[:8]
    original_file_size: int = int.from_bytes(file_size_bytes, "big")

    file_data_start: int = 8
    file_data_end: int = file_data_start + original_file_size

    if len(extracted_bytes) < file_data_end:
        raise ValueError("Incomplete image data; cannot restore the full file.")

    file_data: bytes = extracted_bytes[file_data_start:file_data_end]

    file: IO[bytes]
    with open(output_file_path, "wb") as file:
        file.write(file_data)
