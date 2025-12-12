from django.core.management.base import BaseCommand
from api.models import Category, Manufacturer, Product, Price
from datetime import date

class Command(BaseCommand):
    

    def handle(self, *args, **options):
        self.stdout.write('Populating database...')


        cat_elec, _ = Category.objects.get_or_create(code="ELEC", name="Electronics", defaults={"description": "Gadgets and devices"})
        cat_cloth, _ = Category.objects.get_or_create(code="CLOTH", name="Clothing", defaults={"description": "Apparel"})
        cat_books, _ = Category.objects.get_or_create(code="BOOK", name="Books", defaults={"description": "Reads"})

        man_apple, _ = Manufacturer.objects.get_or_create(code="APPLE", name="Apple Inc")
        man_samsung, _ = Manufacturer.objects.get_or_create(code="SAMSUNG", name="Samsung Electronics")
        man_nike, _ = Manufacturer.objects.get_or_create(code="NIKE", name="Nike")
        man_pub, _ = Manufacturer.objects.get_or_create(code="PUB", name="Publisher Inc")


        products_data = [
            {
                "code": "IPHONE13",
                "name": "iPhone 13",
                "category": cat_elec,
                "manufacturer": man_apple,
                "short_descr": "Latest Apple phone",
                "price": 30000.00
            },
            {
                "code": "S21",
                "name": "Samsung Galaxy S21",
                "category": cat_elec,
                "manufacturer": man_samsung,
                "short_descr": "Samsung Flagship",
                "price": 28000.00
            },
            {
                "code": "TSHIRT",
                "name": "White T-Shirt",
                "category": cat_cloth,
                "manufacturer": man_nike,
                "short_descr": "Cotton t-shirt",
                "price": 500.00
            },
            {
                "code": "PYBOOK",
                "name": "Learning Python",
                "category": cat_books,
                "manufacturer": man_pub,
                "short_descr": "Best book for python",
                "price": 1200.00
            }
        ]

        for p_data in products_data:
            product, created = Product.objects.get_or_create(
                code=p_data["code"],
                defaults={
                    "name": p_data["name"],
                    "category": p_data["category"],
                    "manufacturer": p_data["manufacturer"],
                    "short_descr": p_data["short_descr"]
                }
            )
            
            if not product.prices.exists():
                Price.objects.create(
                    product=product,
                    pdate=date.today(),
                    pprice=p_data["price"],
                    qtty=100
                )
                self.stdout.write(f'Created product: {product.name}')
            else:
                self.stdout.write(f'Product already exists: {product.name}')

        self.stdout.write(self.style.SUCCESS('Successfully populated database'))
