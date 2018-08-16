class Node(object):

    def __init__(self, node_id, hardware, image, images, usb, raw):
        self.id = node_id
        self.hardware = hardware
        self.default_image = image
        self.images = list(images)
        self.usb = usb
        self.raw = raw
        if self.default_image and (self.default_image not in images):
            self.images.append(self.default_image)

    def get_id(self):
        return self.id

    def get_images(self):
        return self.images

    def get_hardware(self):
        return self.hardware

    def get_usb(self):
        return self.usb

    def is_raw(self):
        return self.raw

    def get_default_image(self):
        return self.default_image

    def __repr__(self):
        return '%s:%s(%s)/%s'%(self.id,self.hardware,self.usb,str(self.images))

    def __str__(self):
        return '%s:%s'%(self.id,self.hardware)
