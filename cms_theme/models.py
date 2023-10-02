from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.contrib.image.models import ImageMixin
from djangocms_frontend.models import FrontendUIItem
from easy_thumbnails.files import get_thumbnailer


# Create your models here.


class Person(ImageMixin, FrontendUIItem):
    image_field = "picture"

    class Meta:
        proxy = True
        verbose_name = _("Person")

    @cached_property
    def img_src(self):
        # image can be empty, for example when the image is removed from filer
        # in this case we want to return an empty string to avoid #69
        if not self.picture:
            return ""

        thumbnail_options = {
            "size": (settings.FRONTEND_PORTRAIT_SIZE, settings.FRONTEND_PORTRAIT_SIZE),
            "crop": True,
            "upscale": True,
            "subject_location": self.rel_image.subject_location
            if self.rel_image
            else (),
        }

        try:
            thumbnailer = get_thumbnailer(self.rel_image)
            url = thumbnailer.get_thumbnail(thumbnail_options).url
        except ValueError:
            # get_thumbnailer() raises this if it can't establish a `relative_name`.
            # This may mean that the filer image has been deleted
            url = ""
        return url

    def get_short_description(self):
        return self.config.get("name", "-")
