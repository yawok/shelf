from django.core.management.base import BaseCommand
from collections import Counter
import csv
import os.path
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from main import models


class Command(BaseCommand):
    help = "Import products in Shelf"
    
    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=open)
        parser.add_argument('image_basedir', type=str)

    def handle(self, *args, **options):
        self.stdout.write("Importing products")
        c = Counter()
        reader = csv.DictReader(options.pop('csvfile'))
        for row in reader:
            product, created = models.Product.objects.get_or_create(
                name=row['name'],
                price=row['price']
            )
            product.description = row['description']
            product.slug = slugify(row['name'])
            for import_tag in row['tags'].split('|'):
                tag, tag_created = models.ProductTag.objects.get_or_create(
                    name=import_tag
                )
                product.tags.add(tag)
                c['tags'] += 1
                if tag_created:
                    c['tags_created'] += 1
            with open(
                os.path.join(
                    options['image_basedire'],
                    row['image_filename']
                ), 'rb'
            ) as f:
                image = models.ProductImage(
                    product=product,
                    image=ImageFile(f, name=row['image_filename']),
                )
                image.save()
                c['images'] += 1
            product.save()
            c['products'] += 1
            if created:
                c['products_created'] += 1
        self.stdout.write(
            f"Products prcessed={c['products']} (created{c['products_created']})"
        )
        self.stdout.write(
            f"Tags processed={c['tags_created']} (created{c['tags_created']})"
        )
        self.stdout.write(
            f"Images processed {c['images']}"
        )   