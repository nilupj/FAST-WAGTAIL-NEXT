from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wagtail.models import Page
from news.models import NewsPage, NewsCategory, NewsIndexPage
from wagtail.images.models import Image

class Command(BaseCommand):
    help = 'Populate news articles for testing'

    def handle(self, *args, **options):
        # Get or create news index page
        home_page = Page.objects.get(slug='home')

        try:
            news_index = NewsIndexPage.objects.get(slug='news')
        except NewsIndexPage.DoesNotExist:
            news_index = NewsIndexPage(
                title='Health News',
                slug='news',
                intro='<p>Stay updated with the latest health news and medical breakthroughs.</p>'
            )
            home_page.add_child(instance=news_index)
            news_index.save_revision().publish()

        # Create categories
        categories = [
            {'name': 'Fitness', 'slug': 'fitness', 'description': 'Exercise and physical activity news'},
            {'name': 'Mental Health', 'slug': 'mental-health', 'description': 'Mental wellness and psychology updates'},
            {'name': 'Nutrition', 'slug': 'nutrition', 'description': 'Diet and nutrition information'},
            {'name': 'Medical Research', 'slug': 'medical-research', 'description': 'Latest medical research findings'},
            {'name': 'Public Health', 'slug': 'public-health', 'description': 'Public health policies and updates'},
            {'name': 'Health Tips', 'slug': 'health-tips', 'description': 'Practical advice for a healthier life'}
        ]

        for cat_data in categories:
            category, created = NewsCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Sample news articles
        news_articles = [
            {
                'title': 'Self-Care Guide for People With HIV',
                'subtitle': 'Comprehensive strategies for maintaining health and wellbeing',
                'summary': 'Attention deficit hyperactivity disorder (ADHD) in children is a difference in brain development that can affect their ability to focus and self-control.',
                'body': '''
                <p>Living with HIV requires a comprehensive approach to self-care that addresses both physical and mental health needs. This guide provides essential strategies for maintaining optimal health while managing HIV.</p>

                <h2>Daily Health Management</h2>
                <p>Consistent medication adherence is crucial for viral suppression. Work closely with your healthcare team to establish a routine that fits your lifestyle.</p>

                <h2>Nutrition and Exercise</h2>
                <p>A balanced diet rich in fruits, vegetables, and lean proteins supports immune function. Regular exercise can improve both physical and mental health outcomes.</p>

                <h2>Mental Health Support</h2>
                <p>Living with HIV can present emotional challenges. Seek support through counseling, support groups, or trusted friends and family members.</p>
                ''',
                'category': 'medical-research',
                'featured': True,
                'source': 'Medical Journal Review'
            },
            {
                'title': 'Finding the Best Sleep Positions for You',
                'subtitle': 'Optimize your sleep quality with proper positioning',
                'summary': 'Sleep position affects both sleep quality and overall health. Learn which positions work best for different health conditions and comfort preferences.',
                'body': '''
                <p>Your sleep position plays a crucial role in sleep quality, back health, and overall wellbeing. Understanding the benefits and drawbacks of different positions can help you make informed choices.</p>

                <h2>Back Sleeping</h2>
                <p>Sleeping on your back maintains natural spine alignment and reduces pressure on joints. This position is ideal for those with back pain or acid reflux.</p>

                <h2>Side Sleeping</h2>
                <p>Side sleeping, particularly on the left side, can improve circulation and reduce snoring. It's recommended for pregnant women and those with sleep apnea.</p>

                <h2>Finding Your Ideal Position</h2>
                <p>Consider your health conditions, comfort preferences, and any recommendations from healthcare providers when choosing your sleep position.</p>
                ''',
                'category': 'fitness',
                'featured': True,
                'source': 'Sleep Research Institute'
            },
            {
                'title': 'Magnesium for Depression',
                'subtitle': 'Exploring the role of minerals in mental health',
                'summary': 'Research suggests magnesium deficiency may be linked to depression. Understanding this connection can inform treatment approaches.',
                'body': '''
                <p>Magnesium is an essential mineral that plays a role in over 300 enzymatic reactions in the body, including those affecting mood and brain function.</p>

                <h2>The Magnesium-Depression Connection</h2>
                <p>Studies have shown that people with depression often have lower magnesium levels. Supplementation may help improve symptoms in some individuals.</p>

                <h2>Dietary Sources</h2>
                <p>Include magnesium-rich foods like leafy greens, nuts, seeds, and whole grains in your diet to support mental health naturally.</p>

                <h2>Consultation is Key</h2>
                <p>Always consult with healthcare providers before starting any supplementation regimen, especially if you're currently taking medication for depression.</p>
                ''',
                'category': 'mental-health',
                'featured': False,
                'source': 'Nutritional Psychiatry Research'
            },
            {
                'title': 'New Guidelines for Heart Disease Prevention',
                'subtitle': 'Updated recommendations for cardiovascular health',
                'summary': 'Medical associations release new guidelines focusing on lifestyle modifications and early intervention strategies for heart disease prevention.',
                'body': '''
                <p>The latest guidelines for heart disease prevention emphasize a comprehensive approach that includes lifestyle modifications, regular screening, and early intervention strategies.</p>

                <h2>Key Lifestyle Factors</h2>
                <p>Regular physical activity, a heart-healthy diet, stress management, and adequate sleep form the foundation of cardiovascular health.</p>

                <h2>Screening Recommendations</h2>
                <p>New guidelines recommend earlier and more frequent screening for certain high-risk populations, enabling earlier detection and intervention.</p>

                <h2>Personalized Approach</h2>
                <p>Healthcare providers are encouraged to develop personalized prevention plans based on individual risk factors and lifestyle preferences.</p>
                ''',
                'category': 'public-health',
                'featured': False,
                'source': 'American Heart Association'
            },
            {
                'title': 'Breakthrough in Alzheimer\'s Research',
                'subtitle': 'New therapeutic targets show promise in clinical trials',
                'summary': 'Researchers identify novel therapeutic pathways that could lead to more effective treatments for Alzheimer\'s disease and other forms of dementia.',
                'body': '''
                <p>Recent advances in Alzheimer's research have identified new therapeutic targets that show significant promise in early clinical trials.</p>

                <h2>Novel Therapeutic Approaches</h2>
                <p>Researchers are exploring treatments that target multiple pathways involved in neurodegeneration, offering hope for more comprehensive treatment options.</p>

                <h2>Early Intervention</h2>
                <p>Studies suggest that earlier intervention, before significant cognitive decline occurs, may be key to preserving brain function.</p>

                <h2>Future Implications</h2>
                <p>These breakthroughs could lead to new treatment protocols that significantly improve outcomes for patients with Alzheimer's disease.</p>
                ''',
                'category': 'medical-research',
                'featured': True,
                'source': 'Neurological Research Institute'
            },
            {
                'title': 'Plant-Based Nutrition for Athletic Performance',
                'subtitle': 'How plant-based diets can enhance sports performance',
                'summary': 'Growing evidence supports the benefits of plant-based nutrition for athletes, including improved recovery and sustained energy levels.',
                'body': '''
                <p>Plant-based nutrition is gaining recognition among athletes and sports nutritionists for its potential to enhance performance and recovery.</p>

                <h2>Performance Benefits</h2>
                <p>Plant-based diets can provide sustained energy, reduce inflammation, and support faster recovery between training sessions.</p>

                <h2>Nutritional Considerations</h2>
                <p>Athletes following plant-based diets should pay attention to protein quality, vitamin B12, iron, and omega-3 fatty acids to optimize performance.</p>

                <h2>Success Stories</h2>
                <p>Many elite athletes have successfully adopted plant-based diets while maintaining or improving their competitive performance.</p>
                ''',
                'category': 'nutrition',
                'featured': False,
                'source': 'Sports Nutrition Journal'
            },
            {
                'title': 'Common Showering and Bathing Mistakes',
                'slug': 'common-showering-and-bathing-mistakes',
                'subtitle': 'Expert dermatologists share what you might be doing wrong',
                'summary': 'Learn about the common mistakes people make while showering and bathing that could be affecting their skin health.',
                'body': '<p>Many people don\'t realize that their daily bathing habits could be damaging their skin. Here are some common mistakes to avoid:</p><h2>1. Water Temperature Too Hot</h2><p>Hot water can strip your skin of natural oils, leading to dryness and irritation. Dermatologists recommend using lukewarm water instead.</p><h2>2. Showering Too Long</h2><p>Long showers can dry out your skin. Try to limit your showers to 5-10 minutes.</p><h2>3. Using Harsh Soaps</h2><p>Many commercial soaps contain harsh chemicals that can disrupt your skin\'s natural pH balance. Look for gentle, pH-balanced cleansers.</p><h2>4. Not Moisturizing After</h2><p>Applying moisturizer while your skin is still damp helps lock in moisture.</p><h2>5. Over-Exfoliating</h2><p>Exfoliating too frequently can damage your skin barrier. Limit exfoliation to 2-3 times per week.</p>',
                'category': 'health-tips',
                'source': 'Health Research Institute',
                'featured': True,
            },
        ]

        for article_data in news_articles:
            try:
                category = NewsCategory.objects.get(slug=article_data['category'])
            except NewsCategory.DoesNotExist:
                category = None

            # Check if article already exists
            article_slug = article_data.get('slug', article_data['title'].lower().replace(' ', '-').replace("'", ""))
            if not NewsPage.objects.filter(slug=article_slug).exists():
                article = NewsPage(
                    title=article_data['title'],
                    subtitle=article_data.get('subtitle', ''),
                    summary=article_data.get('summary', ''),
                    body=article_data.get('body', ''),
                    category=category,
                    featured=article_data.get('featured', False),
                    source=article_data.get('source', '')
                )

                news_index.add_child(instance=article)
                article.save_revision().publish()

                self.stdout.write(f'Created news article: {article.title}')

        self.stdout.write(self.style.SUCCESS('Successfully populated news articles'))