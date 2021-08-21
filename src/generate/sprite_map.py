"""
sprite_map.py

Creates a sprite map (grid) from all images
in a folder.

Requires
---------
* Install `imagemagick`
* Create folders names 'temp', 'images', and
'sprite_maps'.

"""

import os

SOURCE_DIR = "../../data/images"
OUTPUT_DIR = "../../data/sprite_maps"
MAP_LAYOUT = [5, 8]
IMAGE_SIZE = [400, 400]


def folder_to_sprite(source_dir: str,
                     output_path: str,
                     layout: (int, int),
                     image_size: (int, int)):
    """
    Converts a folder of images into a single grid.
    """

    # create temporary folder to store resized images
    temp_path = "./temp"
    os.makedirs(temp_path, exist_ok=True)

    # create output folder
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # get all images in directory
    input_files = os.path.join(source_dir, '*')

    image_size_str = 'x'.join(map(str, image_size))
    resize_command = f"mogrify -resize {image_size_str}! -quality 100 -path " \
                     f"{temp_path} {input_files}"
    layout_str = 'x'.join(map(str, layout))
    layout_command = f"montage -mode concatenate -tile {layout_str} " \
                     f"{os.path.join(temp_path, '*')} {output_path}"

    # execute command
    exit_code = os.system(f"{resize_command} && {layout_command}")
    if exit_code != 0:
        exit(1)

    # remove temp folder
    os.system(f'rm -rf {temp_path}')


def main():
    image_dirs = os.listdir(SOURCE_DIR)
    for image_dir in image_dirs:
        _source_dir = os.path.join(SOURCE_DIR, image_dir)
        _output_path = f"{os.path.join(OUTPUT_DIR, image_dir)}.jpeg"
        folder_to_sprite(_source_dir, _output_path, MAP_LAYOUT, IMAGE_SIZE)


if __name__ == '__main__':
    main()
