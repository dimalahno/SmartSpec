from django.test import TestCase
from django.urls import reverse

class SimplePageTests(TestCase):
    def test_index_status_code(self):
        resp = self.client.get(reverse('specs:index'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'SmartSpec')
