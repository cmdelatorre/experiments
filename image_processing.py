import cv2
import numpy as np


# A Mask is a 2D matrix (8-bit pixel values), an image whose pixels are either
# 255 (all bits are 1) or 0 (all bits are 0) where non-zero elements indicate
# the pixels that belong to the mask (the pixel with value 255 are said to be
# "included" in the mask, while the others are "excluded" or out of the mask).
#
# When a Mask is created from another image, it means that the mask has the same
# height and width as the other image.
# Masks are typically used to identify or mark regions of an image. And since
# the pixel values are all 1's or 0's, it is easy to operate them using logical
# (bitwise) operations.


def mask_by_pixel_value(image, low, high, filter_conf=None):
    """
    Create a Mask including the pixels whose values in the given image are
    within [low, high].

    if a filter_conf tuple is given, a morphological transformation is performed
    on the mask. In this case, the tuple must be a sequence of arguments for the
    cv2.morphologyEx function: at least the type of a morphological operation
    and kernel.
    http://docs.opencv.org/modules/imgproc/doc/filtering.html#cv2.morphologyEx

    For example, in an RGB image, mask[x, y] is set to 255 (all bits to 1) if
    image[x, y, z] is within the 3D box specified by low and high, else 0 is set

    """
    mask = cv2.inRange(image, low, high)
    if filter_conf is not None:
        mask = cv2.morphologyEx(mask, *filter_conf)
    return mask


def dark_mask(image, limit=5, filter_conf=None):
    """
    Create a Mask with the dark pixels of the image.

    Uses mask_by_pixel_value. The limit kwarg is used to determine the maximum
    pixel value considered dark (default is 5).

    """
    return mask_by_pixel_value(image,
                               np.array([0, 0, 0]),
                               np.array([limit, limit, limit]),
                               filter_conf=filter_conf)


def masked_merge(target, extra, mask, invert_mask=False):
    """
    Use the mask to create a "window" in the target image where the extra image
    is shown.

    Warning: the given images are modified.

    """
    inv_mask = cv2.bitwise_not(mask)
    if invert_mask:
        aux = mask
        mask = inv_mask
        inv_mask = aux
    # Apply the mask to the extra image (setting to 0 the pixels outside the
    # mask).
    extra = cv2.bitwise_and(extra, extra, mask=mask)
    # Create a "window" in the target image, with the shape of the mask: pixels
    # within the mask are set to 0.
    target = cv2.bitwise_and(target, target, mask=inv_mask)
    # Adding the two images will result in the extra image appearing in the
    # window created on the target image.
    return target + extra