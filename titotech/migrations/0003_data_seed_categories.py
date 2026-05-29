# titotech/migrations/0003_data_seed_categories.py
from django.db import migrations


def seed_categories_and_assign(apps, schema_editor):
    """
    1. Crea las categorías iniciales.
    2. Asigna Smartphones a los productos existentes.
    3. Si existe la tabla antigua titotech_accessory,
       migra sus datos a titotech_products.
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

    cases, _ = Category.objects.get_or_create(
        slug="cases",
        defaults={
            "name": "Cases y Protectores",
            "description": "Estuches y protectores de pantalla para equipos móviles.",
            "is_active": True,
        },
    )

    chargers, _ = Category.objects.get_or_create(
        slug="cargadores",
        defaults={
            "name": "Cargadores y Cables",
            "description": "Cargadores rápidos y cables para todos los dispositivos.",
            "is_active": True,
        },
    )

    audifonos, _ = Category.objects.get_or_create(
        slug="audifonos",
        defaults={
            "name": "Audífonos",
            "description": "Audífonos y auriculares inalámbricos y con cable.",
            "is_active": True,
        },
    )

    Product.objects.filter(category__isnull=True).update(
        category=smartphones
    )

    TYPE_TO_CATEGORY = {
        "case": cases,
        "screen": cases,
        "charger": chargers,
        "cable": chargers,
        "earphone": audifonos,
    }

    connection = schema_editor.connection

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'titotech_accessory'
            );
            """
        )

        table_exists = cursor.fetchone()[0]

        if not table_exists:
            return

        cursor.execute(
            """
            SELECT
                name,
                type,
                compatibility,
                price,
                stock,
                is_active
            FROM titotech_accessory
            """
        )

        accessories = cursor.fetchall()

    for acc in accessories:
        name, acc_type, compatibility, price, stock, is_active = acc

        Product.objects.create(
            category=TYPE_TO_CATEGORY.get(acc_type, cases),
            brand="",
            model=name,
            storage="",
            ram="",
            color="",
            compatibility=compatibility or "",
            price=price,
            stock=stock,
            is_active=is_active,
        )


def reverse_seed(apps, schema_editor):
    Category = apps.get_model("titotech", "Category")
    Product = apps.get_model("titotech", "Product")

    acc_cats = Category.objects.filter(
        slug__in=["cases", "cargadores", "audifonos"]
    )

    Product.objects.filter(
        category__in=acc_cats,
        brand=""
    ).delete()

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