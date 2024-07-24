import time
from unittest.mock import patch

from cms.api import create_page
from django.db import connection
from django.test.utils import CaptureQueriesContext

from cms.models import PageContent
from cms.test_utils.testcases import CMSTestCase
from cms.toolbar.toolbar import CMSToolbar
from cms.toolbar.utils import get_object_preview_url
from menus.menu_pool import menu_pool

from django.template import Template, Context


class MenuPerfTestCase(CMSTestCase):
    def setUp(self):
        if PageContent.admin_manager.current_content().first() is None:
            create_page("Home", "bootstrap5.html", "en")

    def test_00_num_pages(self):
        from cms.models import Page

        print(f"Total pages: {Page.objects.count()}")
        print("------------------")

    def test_10_get_nodes(self):
        print("Build nodes.")
        print("-------------")

        if not menu_pool.discovered:
            menu_pool.discover_menus()
        from djangocms_alias.cms_menus import AliasDisableMenu
        if AliasDisableMenu in menu_pool.modifiers:
            menu_pool.modifiers.remove(AliasDisableMenu)
        menu_pool.clear(all=True)

        with CaptureQueriesContext(connection), self.login_user_context(self.get_superuser()):
            ...  # do your thing
            first_query = len(connection.queries)

            url = get_object_preview_url(PageContent.admin_manager.current_content().first())
            request = self.get_request(url)
            request.toolbar = CMSToolbar(request)

            renderer = menu_pool.get_renderer(request)
            start_time = time.process_time()
            # cProfile.runctx('nodes = renderer.get_nodes()', globals(), locals())
            nodes = renderer.get_nodes()
            end_time = time.process_time()
            last_query = len(connection.queries)
            print(f"Total nodes:          {len(nodes)}")
            print(f"Total queries:        {last_query - first_query}")
            print(f"Total process time:   {(end_time - start_time)*1000:5.0f}ms")
            with self.assertNumQueries(0):
                start_time = time.process_time()
                renderer.get_nodes()
                end_time = time.process_time()
            print(f"Process time (cache): {(end_time - start_time)*1000:5.0f}ms")
            # pprint(connection.queries[first_query:last_query], width=180)
        print()

    def test_20_show_menu(self):
        print("Show menu (nodes are cached).")
        print("------------------------------")

        if not menu_pool.discovered:
            menu_pool.discover_menus()
        from djangocms_alias.cms_menus import AliasDisableMenu
        if AliasDisableMenu in menu_pool.modifiers:
            menu_pool.modifiers.remove(AliasDisableMenu)
        menu_pool.clear(all=True)

        with self.login_user_context(self.get_superuser()):
            page_content = PageContent.admin_manager.current_content().first()
            url = get_object_preview_url(page_content)
            request = self.get_request(url)
            request.toolbar = CMSToolbar(request)

        renderer = menu_pool.get_renderer(request)
        renderer.get_nodes()  # Fill cache

        # 1. Get cache key
        t = Template("{% load menu_tags %}{% show_menu 0 100 100 100 %}")
        c = Context({"request": request})
        start_time = time.process_time()
        with CaptureQueriesContext(connection) as context:
            with patch("menus.templatetags.menu_tags.cut_after") as cut_levels:
                result = t.render(c)
        end_time = time.process_time()
        print(f"Total process time:  {(end_time - start_time)*1000:.0f}ms")
        print(f"Calls cut_levels:    {cut_levels.call_count}")
        print(f"Queries:             {len(context.captured_queries)}")
        print(f"Generated menu size: {len(result)//1024}kB")
        print()
        # print(str(result)[:100])

    def test_30_show_menu2(self):
        print("Show page preview including menu.")
        print("----------------------------------")

        with self.login_user_context(self.get_superuser()):
            page_content = page_content = PageContent.admin_manager.current_content().first()
            url = get_object_preview_url(page_content) if page_content else "/"

            first_query = len(connection.queries)
            with CaptureQueriesContext(connection):
                with patch("menus.templatetags.menu_tags.cut_after") as cut_levels:
                    start_time = time.time()
                    self.client.get(url)
                    end_time = time.time()
            last_query = len(connection.queries)
        print(f"Total time:         {(end_time - start_time)*1000:.0f}ms")
        print(f"Calls cut_levels:   {cut_levels.call_count}")
        print(f"Queries:            {last_query - first_query}")
        # if last_query - first_query < 100:
        #     for i in range(first_query, last_query):
        #         print(i-first_query+1, connection.queries[i]["sql"])
        #         print()
        print()
