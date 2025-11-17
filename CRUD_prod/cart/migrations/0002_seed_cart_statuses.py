from django.db import migrations

STATUSES = [
    'empty',
    'have_items',
    'purchased',
    'abandoned',
]

def create_statuses(apps, schema_editor):
    CartStatus = apps.get_model('cart', 'CartStatus')
    for status_code in STATUSES:
        CartStatus.objects.create(code=status_code)

def remove_statuses(apps, schema_editor):
    CartStatus = apps.get_model('cart', 'CartStatus')
    CartStatus.objects.filter(code__in=STATUSES).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_statuses, remove_statuses),
    ]
