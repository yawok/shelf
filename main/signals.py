from io import BytesIO
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from . import models
from django.contrib.auth.signals import user_logged_in

THUMBNAIL_SIZE = (300, 300)
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=models.ProductImage)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info(f"Generating thumbnail for product {instance.product.id}")
    image = Image.open(instance.image)
    image = image.convert("RGB")
    image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

    temp_thumb = BytesIO()
    image.save(temp_thumb, "JPEG")
    temp_thumb.seek(0)

    instance.thumbnail.save(
        instance.image.name, ContentFile(temp_thumb.read()), save=False
    )
    temp_thumb.close()


@receiver(user_logged_in)
def merge_basket_if_found(sender, user, request, **kwargs):
    anonymous_basket = getattr(request, "basket", None)
    if anonymous_basket:
        try:
            logged_in_basket = models.Basket.objects.get(
                user=user, status=models.Basket.OPEN
            )
            for line in anonymous_basket.basketline_set.all():
                line.basket = logged_in_basket
                line.save()
            anonymous_basket.delete()
            request.basket = logged_in_basket
            logger.info(f"Merged basket with id: {logged_in_basket.id}")
        except models.Basket.DoesNotExist:
            anonymous_basket.user = user
            anonymous_basket.save()
            logger.info(f"Assigned user to basket with id: {anonymous_basket.id}")


@receiver(post_save, sender=models.OrderLine)
def orderLine_to_order_status(sender, instance, **kwargs):
    if not instance.order.lines.filter(status__lt=models.OrderLine.SENT).exists():
        logger.info(f"All orders for {instance.order.id} have been processed. Marked as done.")
        instance.order.status = models.Order.DONE
        instance.order.save()
        
        