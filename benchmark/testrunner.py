from django.test.runner import DiscoverRunner


class MyTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        return None

    def teardown_databases(self, old_config, **kwargs):
        return None

