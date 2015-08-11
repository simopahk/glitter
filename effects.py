from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from math import sin, pi
import config

identifiers = [('default', 'Originaal'), ('f1', 'Filter #1'), ('f2', 'Filter #2'), ('f3', 'Filter #3'), ('f4', 'Filter #4'), ('f5', 'Filter #5'), ('f6', 'Filter #6')]

load_masks = [2, 1]
alphamasks = {}

(R, G, B, A) = (0, 1, 2, 3)

def setup(img):
    global alphamasks

    mask_sizes = ['original']

    if config.preview_basis == "preview" or config.thumbnail_basis == "preview":
        mask_sizes.append("preview")

    if config.thumbnail_basis == "thumbnail":
        mask_sizes.append("thumbnail")

    for mask_id in load_masks:
        masks = {}
        mask = Image.open("images/mask" + str(mask_id) + ".png").convert("L")

        for size in mask_sizes:
            imgsize = eval('img.' + size + '.size')

            if mask.size > imgsize:
                mask = mask.resize(imgsize, Image.ANTIALIAS)
            else:
                mask = mask.resize(imgsize)

            masks[size] = mask

        alphamasks[mask_id] = masks

def getmask(id, image, img):
    if image.size == img.original.size:
        return alphamasks[id]['original']
    elif image.size == img.preview.size:
        return alphamasks[id]['preview']
    else:
        return alphamasks[id]['thumbnail']


def default(image, img):
    return image

def f1(image, img):
    image = ImageEnhance.Brightness(image).enhance(1.1)

    bands = image.split()
    bands[R].paste(bands[R].point(lambda i: i + 2 ** ((255 - i) ** 0.25)))
    image = Image.merge(image.mode, bands)

    image = ImageEnhance.Contrast(image).enhance(1.15)

    bands = image.split()
    bands[G].paste(bands[G].point(lambda i: i * 0.9))
    image = Image.merge(image.mode, bands)

    return image

def f2(image, img):
    bands = image.split()

    bands[B].paste(bands[B].point(lambda i: (i + (255 - i) ** 0.5) * 0.9))
    bands[R].paste(bands[R].point(lambda i: i * 1.1))
    bands[G].paste(bands[G].point(lambda i: i * 1.1))
    image = Image.merge(image.mode, bands)

    layer = Image.new("RGBA", image.size, "#ffde00")
    image = Image.blend(image, layer, 0.1)

    blur = image.filter(ImageFilter.GaussianBlur(radius = 5))
    mask = getmask(1, image, img).point(lambda i: i + 60)
    image = Image.composite(image, blur, mask)

    image = ImageEnhance.Brightness(image).enhance(1.05)
    image = ImageEnhance.Contrast(image).enhance(1.4)

    return image

def f3(image, img):
    image = ImageEnhance.Brightness(image).enhance(1.05)
    image = ImageEnhance.Contrast(image).enhance(1.9)
    image = ImageEnhance.Color(image).enhance(0.8)
    image = ImageEnhance.Brightness(image).enhance(1.1)

    layer = Image.new("RGBA", image.size, "#07351a")
    image = Image.blend(image, layer, 0.3)
    image = ImageEnhance.Contrast(image).enhance(1.4)

    layer = Image.new("RGBA", image.size, "#0e5c2d")
    mask = getmask(1, image, img).point(lambda i: i + 90)
    image = Image.composite(image, layer, mask)

    return image

def f4(image, img):
    layer = ImageEnhance.Brightness(image).enhance(1.3)
    mask = getmask(1, image, img).point(lambda i: i)
    image = Image.composite(layer, image, mask)

    bands = image.split()
    bands[B].paste(bands[B].point(lambda i: i * 0.8))
    bands[R].paste(bands[R].point(lambda i: i * 0.65))
    bands[G].paste(bands[G].point(lambda i: i * 0.65))
    image = Image.merge(image.mode, bands)

    image = ImageEnhance.Contrast(image).enhance(2)
    image = ImageEnhance.Brightness(image).enhance(0.95)

    layer = Image.new("RGBA", image.size, "#000000")
    mask = getmask(2, image, img).point(lambda i: i + 200)
    image = Image.composite(image, layer, mask)

    layer = Image.new("RGBA", image.size, "#f0a515")
    layer = ImageEnhance.Brightness(layer).enhance(1.3)
    image = Image.blend(image, layer, 0.2)
    image = ImageEnhance.Contrast(image).enhance(1.3)

    return image

def f5(image, img):
    blur = image.filter(ImageFilter.GaussianBlur(radius = 6))
    mask = getmask(2, image, img).point(lambda i: i + 80)
    image = Image.composite(image, blur, mask)

    image = ImageEnhance.Brightness(image).enhance(1.3)
    image = ImageEnhance.Color(image).enhance(0.9)
    image = image.point(lambda i: i + 3 * sin((pi / 2) * (255 - i) / 255))

    bands = image.split()

    bands[B].paste(bands[B].point(lambda i: 1.1 * i))
    image = Image.merge(image.mode, bands)
    image = ImageEnhance.Contrast(image).enhance(1.3)

    return image

def f6(image, img):
    image = ImageEnhance.Contrast(image).enhance(1.7)
    layer = image.convert("L").convert("RGBA")
    image = Image.blend(image, layer, 0.5)

    bands = image.split()

    bands[R].paste(bands[R].point(lambda i: 1.25 * i))
    bands[G].paste(bands[G].point(lambda i: 1.25 * i))
    image = Image.merge(image.mode, bands)

    blur = image.filter(ImageFilter.GaussianBlur(radius = 7))
    mask = getmask(2, image, img).point(lambda i: i + 90)
    image = Image.composite(image, blur, mask)

    layer = Image.new("RGBA", image.size, "#000000")
    mask = getmask(1, image, img).point(lambda i: i + 180)
    image = Image.composite(image, layer, mask)

    return image