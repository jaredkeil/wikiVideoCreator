import cv2
from wiki_movie.utils import make_directory


def maxsize_pad(img_path, save_path, width=1920, height=1080):
    """
    Save image of max size within width x height, keeping aspect ratio.
    Adds black border on unused pixels to fill out shape.
    """
    im = cv2.imread(img_path)

    old_size = im.shape[:2]  # old_size is in (height, width) format
    ratio = min(float(width) / im.shape[1],
                float(height) / im.shape[0])
    new_size = tuple([int(x*ratio) for x in old_size])
    # new_size is in (width, height) format

    im = cv2.resize(im, (new_size[1], new_size[0]))

    delta_w = width - new_size[1]
    delta_h = height - new_size[0]

    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)

    black = [0, 0, 0]  # color used in border

    new_im = cv2.copyMakeBorder(im, top, bottom, left, right,
                                cv2.BORDER_CONSTANT, value=black)

    cv2.imwrite(save_path, new_im)


def resize_subdirectory(s_img_dir, resized_images_dir):
    file_names = [x.parts[-1] for x in s_img_dir.glob('*')
                  if x.is_file() and x.parts[-1][0] != '.']

    for file_name in file_names:
        try:
            maxsize_pad(str(s_img_dir / file_name),
                        str(resized_images_dir / file_name))
        except Exception as e:
            print(f'{e} saving resized image {file_name}, e')


def resize_image_directory(img_dir, out_dir):
    """
    img_dir (Path) -- directory to recursively search, resize images
    out_dir (Path) -- directory to save resized images in new subdirectories
    """
    for p in img_dir.iterdir():
        if p.is_dir():
            make_directory(out_dir / p.name)
            resize_subdirectory(p, out_dir / p.name)
