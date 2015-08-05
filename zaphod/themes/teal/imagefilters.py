from pyramid_frontend.images.filters import Filter
from pyramid_frontend.images.utils import is_white_background, pad_image


class CreatorProfileFilter(Filter):
    """
    If an image is against a white background, add some padding, otherwise
    don't. Used on the creator's profile page.
    """
    def filter(self, im):
        should_pad = is_white_background(im)
        w, h = im.size
        if should_pad:
            im = pad_image(im, (int(w * 1.1), int(h * 1.1)))
        return im
