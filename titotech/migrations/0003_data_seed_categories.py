# titotech/migrations/0003_data_seed_categories.py
from django.db import migrations


def seed_categories_and_assign(apps, schema_editor):
    """
    1. Crea las categorías iniciales.
    2. Asigna 'Smartphones' a los 3 equipos existentes.
    3. Migra los 2 accesorios de titotech_accessory → titotech_products.
    """
    Category = apps.get_model('titotech', 'Category')
    Product  = apps.get_model('titotech', 'Product')

    # --- 1. Crear categorías ---
    smartphones, _ = Category.objects.get_or_create(
        slug='smartphones',
        defaults={
            'name':        'Smartphones',
            'description': 'Teléfonos inteligentes de última generación.',
            'is_active':   True,
        }
    )
    cases, _ = Category.objects.get_or_create(
        slug='cases',
        defaults={
            'name':        'Cases y Protectores',
            'description': 'Estuches y protectores de pantalla para equipos móviles.',
            'is_active':   True,
        }
    )
    chargers, _ = Category.objects.get_or_create(
        slug='cargadores',
        defaults={
            'name':        'Cargadores y Cables',
            'description': 'Cargadores rápidos y cables para todos los dispositivos.',
            'is_active':   True,
        }
    )
    audifonos, _ = Category.objects.get_or_create(
        slug='audifonos',
        defaults={
            'name':        'Audífonos',
            'description': 'Audífonos y auriculares inalámbricos y con cable.',
            'is_active':   True,
        }
    )

    # --- 2. Asignar 'Smartphones' a todos los productos existentes sin categoría ---
    Product.objects.filter(category__isnull=True).update(category=smartphones)

    # --- 3. Migrar accesorios de la tabla antigua a products ---
    TYPE_TO_CATEGORY = {
        'case':     cases,
        'screen':   cases,
        'charger':  chargers,
        'cable':    chargers,
        'earphone': audifonos,
    }

    with schema_editor.connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT name, type, compatibility, price, stock, is_active FROM titotech_accessory"
            )
            accessories = cursor.fetchall()
        except Exception:
            accessories = []

    for acc in accessories:
        name, acc_type, compatibility, price, stock, is_active = acc
        category = TYPE_TO_CATEGORY.get(acc_type, cases)
        Product.objects.create(
            category      = category,
            brand         = '',
            model         = name,
            storage       = '',
            ram           = '',
            color         = '',
            compatibility = compatibility or '',
            price         = price,
            stock         = stock,
            is_active     = is_active,
        )


def reverse_seed(apps, schema_editor):
    """Reversión: elimina las categorías y productos migrados."""
    Category = apps.get_model('titotech', 'Category')
    Product  = apps.get_model('titotech', 'Product')
    try:
        acc_cats = Category.objects.filter(slug__in=['cases', 'cargadores', 'audifonos'])
        Product.objects.filter(category__in=acc_cats, brand='').delete()
        Category.objects.filter(
            slug__in=['smartphones', 'cases', 'cargadores', 'audifonos']
        ).delete()
    except Exception:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('titotech', '0002_add_category_rename_tables'),
    ]

    operations = [
        migrations.RunPython(seed_categories_and_assign, reverse_seed),
    ]
