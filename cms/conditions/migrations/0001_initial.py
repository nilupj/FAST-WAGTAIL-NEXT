from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailimages', '0001_squashed_0021'),
        ('wagtailcore', '0083_workflowcontenttype'),
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConditionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=80, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Condition Category',
                'verbose_name_plural': 'Condition Categories',
            },
        ),
        migrations.CreateModel(
            name='ConditionIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('intro', wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                'verbose_name': 'Condition Index Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ConditionListingPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('intro', wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                'verbose_name': 'Condition Listing Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ConditionPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('also_known_as', models.CharField(blank=True, max_length=255)),
                ('overview', wagtail.fields.RichTextField()),
                ('symptoms', wagtail.fields.RichTextField()),
                ('causes', wagtail.fields.RichTextField()),
                ('diagnosis', wagtail.fields.RichTextField()),
                ('treatments', wagtail.fields.RichTextField()),
                ('prevention', wagtail.fields.RichTextField()),
                ('complications', wagtail.fields.RichTextField(blank=True)),
                ('risk_factors', wagtail.fields.RichTextField(blank=True)),
                ('specialties', models.CharField(blank=True, max_length=255)),
                ('prevalence', models.CharField(blank=True, max_length=255)),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('categories', models.ManyToManyField(blank=True, related_name='conditions', to='conditions.conditioncategory')),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'verbose_name': 'Condition Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='RelatedConditionsOrderable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_conditions', to='conditions.conditionpage')),
                ('related_condition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='conditions.conditionpage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]