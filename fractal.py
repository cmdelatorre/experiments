from PIL import Image, ImageDraw
import math, colorsys, sys


dimensions = (1024, 1024)
scale = 2.0/(dimensions[0])
#center = (2.2, 1.5)       # Use this for Mandelbrot set
center = (1, 1)       # Use this for Julia set
iterate_max = 300
colors_max = 1000

# Calculate a tolerable palette
palette = [0] * colors_max
for i in range(colors_max):
    f = 1-abs((float(i)/colors_max-1)**15)
    r, g, b = colorsys.hsv_to_rgb(.33+f/3, 1-f/2, f)
    palette[i] = (int(r*255), int(g*255), int(b*255))

# Calculate the mandelbrot sequence for the point c with start value z
def iterate_mandelbrot(c, z = 0):
    for n in range(iterate_max + 1):
        z = z*z +c
        if abs(z) > 2:
            return n
    return None

# Draw our image
some_values = [0.5 + x/100.0 for x in range(20)]
a = 0.3

for i, b in enumerate(some_values):
    img = Image.new("RGB", dimensions)
    d = ImageDraw.Draw(img)


    for y in range(dimensions[1]):
        for x in range(dimensions[0]):
            c = complex(x * scale - center[0], y * scale - center[1])

            #n = iterate_mandelbrot(c)            # Use this for Mandelbrot set
            n = iterate_mandelbrot(complex(a, b), c)  # Use this for Julia set

            if n is None:
                v = 1
            else:
                v = n/iterate_max*1.0

            d.point((x, y), fill = palette[int(v * (colors_max-1))])

    del d
    img.save(str(i) + "-" + sys.argv[1])
    print(str(i) + "-" + sys.argv[1])
