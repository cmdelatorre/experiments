from models import Gallery, GalleriesManager


class DirectoryGallery(Gallery):
    def __init__(self, images_dir, mask_mode):
        super(DirectoryGallery, self).__init__()
        self.images_dir = images_dir
        self.mode = mode
        self.distance = distance
        self.data_src = data
        self.images = []
        self.height = height
        self.width = width
        self.current_index = 0
        self.current_image = None

    def load(self):
        #print('loading ' + self.data_src)
        for image_fname in os.listdir(self.data_src):
            fname = os.path.join(self.data_src, image_fname)
            _, file_extension = os.path.splitext(fname)
            if file_extension.lower() in ['.jpg', '.png']:
                bg_image = cv2.imread(fname)
                #print('\tloading: ' + image_fname)
                self.images.append(cv2.resize(bg_image, (self.width, self.height)))
        self.current_image = self.images[0]
        return self

class FractalManager(GalleriesManager):
    def register(self, images_dir, distance, mask_mode):
        pass