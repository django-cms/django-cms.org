from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.contrib.image.models import ImageMixin
from djangocms_frontend.models import FrontendUIItem
from easy_thumbnails.files import get_thumbnailer


# Create your models here.
class SquareThumbnailMixin:
    THUMBNAIL_SIZE = 140
    use_automatic_scaling = True
    use_crop = True
    use_upscale = True

    @cached_property
    def get_thumbnail_options(self):
        if self.rel_image and getattr(self, "keep_full_image", False):
            if self.rel_image.width > self.rel_image.height:

                thumbnail_options = self.get_size(self.THUMBNAIL_SIZE, None)
            else:
                thumbnail_options = self.get_size(None, self.THUMBNAIL_SIZE)
            if self.rel_image.subject_location:
                thumbnail_options["subject_location"] = self.rel_image.subject_location
        else:
            thumbnail_options = self.get_size(self.THUMBNAIL_SIZE, self.THUMBNAIL_SIZE)
        return thumbnail_options

    @cached_property
    def img_src(self):
        # image can be empty, for example when the image is removed from filer
        # in this case we want to return an empty string to avoid #69
        if not hasattr(self, self.image_field):
            return ""

        thumbnail_options = self.get_thumbnail_options
        try:
            thumbnailer = get_thumbnailer(self.rel_image)
            url = thumbnailer.get_thumbnail(thumbnail_options).url
        except ValueError:
            # get_thumbnailer() raises this if it can't establish a `relative_name`.
            # This may mean that the filer image has been deleted
            url = ""
        return url

    @property
    def img_width(self):
        return self.get_thumbnail_options["size"][0]

    @property
    def img_height(self):
        return self.get_thumbnail_options["size"][1]


class Person(ImageMixin, SquareThumbnailMixin, FrontendUIItem):
    image_field = "picture"
    THUMBNAIL_SIZE = 140

    class Meta:
        proxy = True
        verbose_name = _("Person")

    def get_short_description(self):
        return self.config.get("name", "-")


class Feature(FrontendUIItem):
    class Meta:
        proxy = True
        verbose_name = _("Feature")

    def get_short_description(self):
        return self.config.get("feature", "-")


class CaseStudyProfile(FrontendUIItem):
    class Meta:
        proxy = True
        verbose_name = _("Case study profile")

    def get_short_description(self):
        return self.config.get("client", "-")


class PromoCard(ImageMixin, SquareThumbnailMixin, FrontendUIItem):
    class Meta:
        proxy = True
        verbose_name = _("Promo card")

    image_field = "image"
    keep_full_image = True
    THUMBNAIL_SIZE = 240

    def get_short_description(self):
        return self.config.get("title", "-")
