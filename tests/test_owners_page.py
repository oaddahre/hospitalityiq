"""Owners on the UI standard: the list (title + one line, four counts, one
filter row, one sortable table, owner type as plain text) and the owner page
(the Brand page's structure).

    python3 -m unittest tests.test_owners_page -v
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


HTML = read('templates', 'index.html')
PAGE = HTML[HTML.index('<section class="screen" id="screen-owners">'):]
PAGE = PAGE[:PAGE.index('</section>')]
JS = read('static', 'js', 'main.js')


class OwnersList(unittest.TestCase):
    def test_layout(self):
        lst = PAGE[:PAGE.index('screen-owner-detail')]
        self.assertIn('<h1 class="k-title">Owners</h1>', lst)
        self.assertEqual(lst.count('class="kpi-card"'), 4)
        for i in ('owners-search', 'owners-type', 'owners-sort', 'owners-table', 'owners-count'):
            self.assertIn(f'id="{i}"', lst)
        for gone in ('pill--blue', 'pill--green', 'pill--orange', 'owner-card'):
            self.assertNotIn(gone, lst)

    def test_table(self):
        js = JS[JS.index('function renderOwnersTable'):JS.index("document.getElementById('owners-search')")]
        self.assertIn('OWNER_TYPE_TEXT(o.type)', js)                  # type as plain text
        self.assertNotIn('ownerTypeBadge', js)
        self.assertIn('inlineBar(o.total_keys', js)


if __name__ == '__main__':
    unittest.main()
