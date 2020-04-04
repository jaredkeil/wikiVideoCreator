import cv2

def maxsize_pad(im_path, save_path, desired_width=1920, desired_height=1080):
    """
    Creates new image of maximum size within shape(desired_width, desired_height),
    while maintaining aspect ratio. Adds black border on unused pixels to fill out shape.
    """
    im = cv2.imread(im_path)
    old_size = im.shape[:2] # old_size is in (height, width) format
    ratio = min(float(desired_width)/im.shape[1], float(desired_height)/im.shape[0])
    new_size = tuple([int(x*ratio) for x in old_size])
    # new_size should be in (width, height) format

    im = cv2.resize(im, (new_size[1], new_size[0]))

    delta_w = desired_width - new_size[1]
    delta_h = desired_height - new_size[0]
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)

    color = [0, 0, 0]
    new_im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT,
        value=color)
    cv2.imwrite(save_path, new_im)
