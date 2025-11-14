from django.contrib import admin
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from .models import NewsCategory

class NewsCategoryAdmin(SnippetViewSet):
    model = NewsCategory
    menu_label = 'News Categories'
    icon = 'tag'
    add_to_admin_menu = True
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')

# Register your models here.
