# titotech/migrations/0003_data_seed_categories.py

from django.db import migrations


def seed_categories_and_assign(apps, schema_editor):
    """
    Crea las categorías iniciales y asigna Smartphones
    a cualquier producto existente sin categoría.
    """

    Category = apps.get_model("titotech", "Category")
    Product = apps.get_model("titotech", "Product")

    smartphones, _ = Category.objects.get_or_create(
        slug="smartphones",
        defaults={
            "name": "Smartphones",
            "description": "Teléfonos inteligentes de última generación.",
            "is_active": True,
        },
    )

    Category.objects.get_or_create(
        slug="cases",
        defaults={
            "name": "Cases y Protectores",
            "description": "Estuches y protectores de pantalla para equipos móviles.",
            "is_active": True,
        },
    )

    Category.objects.get_or_create(
        slug="cargadores",
        defaults={
            "name": "Cargadores y Cables",
            "description": "Cargadores rápidos y cables para todos los dispositivos.",
            "is_active": True,
        },
    )

    Category.objects.get_or_create(
        slug="audifonos",
        defaults={
            "name": "Audífonos",
            "description": "Audífonos y auriculares inalámbricos y con cable.",
            "is_active": True,
        },
    )

    Product.objects.filter(
        category__isnull=True
    ).update(
        category=smartphones
    )


def reverse_seed(apps, schema_editor):
    Category = apps.get_model("titotech", "Category")

    Category.objects.filter(
        slug__in=[
            "smartphones",
            "cases",
            "cargadores",
            "audifonos",
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("titotech", "0002_add_category_rename_tables"),
    ]

    operations = [
        migrations.RunPython(
            seed_categories_and_assign,
            reverse_seed,
        ),
    ]