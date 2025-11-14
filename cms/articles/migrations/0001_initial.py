from django.db import migrations, models
import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields
import wagtail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailimages', '0001_squashed_0021'),
        ('wagtailcore', '0083_workflowcontenttype'),
        ('taggit', '0004_alter_taggeditem_content_type_alter_taggeditem_tag'),
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleAuthor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('credentials', models.CharField(blank=True, max_length=255)),
                ('bio', models.TextField(blank=True)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'verbose_name': 'Article Author',
                'verbose_name_plural': 'Article Authors',
            },
        ),
        migrations.CreateModel(
            name='ArticleCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=80, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Article Category',
                'verbose_name_plural': 'Article Categories',
            },
        ),
        migrations.CreateModel(
            name='ArticleIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('intro', wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                'verbose_name': 'Article Index Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ArticleListingPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('intro', wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                'verbose_name': 'Article Listing Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ArticlePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('summary', models.TextField(blank=True)),
                ('body', wagtail.fields.RichTextField()),
                ('featured', models.BooleanField(default=False)),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='articles.articleauthor')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='articles.articlecategory')),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),

            ],
            options={
                'verbose_name': 'Article Page',
            },
            bases=('wagtailcore.page',),
        ),
    ]