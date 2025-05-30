# Generated by Django 5.2.1 on 2025-05-31 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AssetCategoryConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(choices=[('select', 'Display category selector'), ('fixed', 'Use fixed list of categories')], default='select', help_text='Determines if users select a category during assignment, or if a fixed list (defined below) is used.', max_length=10, verbose_name='Assignment Category Mode')),
                ('allowed_category_ids', models.JSONField(blank=True, default=list, help_text="List of Snipe-IT category IDs. Used when mode is 'fixed'. The asset's actual category must be in this list.", verbose_name='Allowed Asset Category IDs')),
            ],
            options={
                'verbose_name': 'Asset Category Configuration',
                'verbose_name_plural': 'Asset Category Configurations',
            },
        ),
    ]
