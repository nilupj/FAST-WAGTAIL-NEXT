
from django.http import JsonResponse
from django.db.models import Q
from .models import DrugPage, DrugCategory

def drugs_index(request):
    """Get all drugs listing"""
    try:
        drugs = DrugPage.objects.live().order_by('title')
        
        data = []
        for drug in drugs:
            drug_data = {
                'id': drug.id,
                'title': drug.title,
                'slug': drug.slug,
                'generic_name': drug.generic_name,
                'brand_names': drug.brand_names,
                'drug_class': drug.drug_class,
                'image': drug.image.get_rendition('fill-800x500').url if drug.image else None,
                'categories': [{'name': cat.name, 'slug': cat.slug} for cat in drug.categories.all()],
            }
            data.append(drug_data)
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def drug_detail(request, slug):
    """Get a single drug by slug"""
    try:
        drug = DrugPage.objects.live().get(slug=slug)
        
        drug_data = {
            'id': drug.id,
            'title': drug.title,
            'slug': drug.slug,
            'generic_name': drug.generic_name,
            'brand_names': drug.brand_names,
            'drug_class': drug.drug_class,
            'overview': drug.overview,
            'uses': drug.uses,
            'dosage': drug.dosage,
            'side_effects': drug.side_effects,
            'warnings': drug.warnings,
            'interactions': drug.interactions,
            'storage': drug.storage,
            'pregnancy_category': drug.pregnancy_category,
            'image': drug.image.get_rendition('fill-800x500').url if drug.image else None,
            'categories': [{'name': cat.name, 'slug': cat.slug} for cat in drug.categories.all()],
            'view_count': drug.view_count,
        }
        
        # Update view count
        drug.view_count += 1
        drug.save()
        
        return JsonResponse(drug_data)
    except DrugPage.DoesNotExist:
        return JsonResponse({'message': 'Drug not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def drugs_search(request):
    """Search drugs by query string"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse([], safe=False)
    
    try:
        drugs = DrugPage.objects.live().filter(
            Q(title__icontains=query) |
            Q(generic_name__icontains=query) |
            Q(brand_names__icontains=query) |
            Q(drug_class__icontains=query)
        ).order_by('title')
        
        data = []
        for drug in drugs:
            drug_data = {
                'id': drug.id,
                'title': drug.title,
                'slug': drug.slug,
                'generic_name': drug.generic_name,
                'brand_names': drug.brand_names,
                'drug_class': drug.drug_class,
                'image': drug.image.get_rendition('fill-800x500').url if drug.image else None,
            }
            data.append(drug_data)
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def drug_categories(request):
    """Get all drug categories"""
    try:
        categories = DrugCategory.objects.all().order_by('name')
        
        data = []
        for category in categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'drug_count': category.drugs.live().count(),
            }
            data.append(category_data)
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
