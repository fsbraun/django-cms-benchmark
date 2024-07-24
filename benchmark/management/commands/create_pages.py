from cms.models import Page
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = """Create pages for benchmarking

+ P1
| + P2
| | + P3-0
| | + P3-1
| | ...
| | + P3-8
| | + P3-9
| + P9-0
| | + P10-0
| |   + P11-0
| + P9-1
| | + P10-1
| |   + P11-1
| ...
| + P9-8
| | + P10-8
| |   + P11-8
| + P9-9
| | + P10-9
| |   + P11-9
| + P1 (recursive)
| + P4 (recursive)
| + P6 (recursive)
+ P4
| + P5-0
| + P5-1
| ...
| + P5-8
| + P5-9
+ P6
| + P7-0
| + P8-0
| + P7-1
| + P8-1
| ...
| + P7-8
| + P8-8
| + P7-9
| + P8-9
"""
    def add_arguments(self, parser):
        parser.add_argument(
            "--levels",
            type=int,
            default=3,
            help="Recursion depth when generating pages"
        )

    def handle(self, *args, **options):
        from django.contrib.auth.models import User

        from cms.api import create_page

        user = User.objects.first()

        def create_one_level(target=None):
            defaults = {
                'template': 'bootstrap5.html',
                'language': 'en',
                'created_by': user,
            }
            p1 = create_page('P1', in_navigation=True, parent=target, **defaults)
            if target is None:
                p1.set_as_homepage()
            p4 = create_page('P4', in_navigation=True, parent=target, **defaults)
            p6 = create_page('P6', in_navigation=False, parent=target, **defaults)
            p2 = create_page('P2', in_navigation=True, parent=p1, **defaults)
            for i in range(10):
                p3 = create_page(f'P3-{i}', in_navigation=True, parent=p2, **defaults)
                p5 = create_page(f'P5-{i}', in_navigation=True, parent=p4, **defaults)
                p7 = create_page(f'P7-{i}', in_navigation=True, parent=p6, **defaults)
                p8 = create_page(f'P8-{i}', in_navigation=True, parent=p6, **defaults)
                p9 = create_page(f'P9-{i}', in_navigation=True, parent=p1, **defaults)
                p10 = create_page(f'P10-{i}', in_navigation=True, parent=p9, **defaults)
                p11 = create_page(f'P11-{i}', in_navigation=True, parent=p10, **defaults)
            return [p1, p3, p5, p7, p8, p11]

        def create_pages(level, parents=None, max_level=5):
            if parents is None:
                parents = [None]
            for parent in parents:
                new = create_one_level(target=parent)
                if level < max_level:
                    create_pages(level + 1, new, max_level)

        levels = options.get("levels", 5)
        existing_pages = Page.objects.count()
        create_pages(0, max_level=levels)
        new_pages = Page.objects.count() - existing_pages

        print("Created", new_pages, "pages in", levels, "levels")
        print("Total pages", Page.objects.count())
