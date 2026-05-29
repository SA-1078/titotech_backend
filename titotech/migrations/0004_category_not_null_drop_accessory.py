# titotech/migrations/0004_category_not_null_drop_accessory.py
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    - Hace category NOT NULL en titotech_products
      (ya todos los productos tienen una categoría asignada por 0003)
    - Elimina la tabla titotech_accessory (los datos ya fueron migrados a titotech_products)
    """

    dependencies = [
        ('titotech', '0003_data_seed_categories'),
    ]

    operations = [
        # 1. Hacer category obligatorio (NOT NULL)
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products',
                to='titotech.category',
                verbose_name='Categoría',
            ),
        ),
        # 2. Eliminar la tabla titotech_accessory con SQL directo
        #    (el modelo ya no existe en el código, pero la tabla sigue en la BD)
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS titotech_accessory;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
