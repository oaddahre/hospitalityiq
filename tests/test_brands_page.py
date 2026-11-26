"""Brands on the UI standard: title + one line, four compact cards, one row
of controls (search, segment control, sort, Table | Cards, export), a
sortable table (logo + name, hotels, keys, market share bar, BAR, occupancy,
Rooms RevPAR, pipeline linked to the Pipeline filtered on the group), cards
without descriptions or coloured pills; no market-share chart or insight cards.

    python3 -m unittest tests.test_brands_page -v
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


class BrandsPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html = read('templates', 'index.html')
        cls.page = html[html.index('<section class="screen" id="screen-brands">'):]
        cls.page = cls.page[:cls.page.index('</section>')]
        js = read('static', 'js', 'main.js')
        cls.js = js[js.index('// ─── Brands screen'):js.index('// ─── Brand detail')]

    def test_layout(self):
        p = self.page
        self.assertIn('<h1 class="k-title">Brands</h1>', p)
        self.assertEqual(p.count('class="kpi-card"'), 4)
        for i in ('brands-search', 'brands-seg-pills', 'brands-sort', 'brands-view', 'btn-export-brands', 'brands-comp-table', 'brands-cards-grid'):
            self.assertIn(f'id="{i}"', p)
        self.assertIn('data-view="table" aria-pressed="true">Table</button>', p)
        for col in ('brand_group', 'hotels', 'total_keys', 'market_share_keys_pct', 'bar_mad', 'avg_occupancy', 'avg_revpar', 'pipeline_keys'):
            self.assertIn(f'data-bccol="{col}"', p)
        for gone in ('brands-market-share-wrap', 'brni-', 'Rank</th>'):
            self.assertNotIn(gone, p)

    def test_table_and_cards(self):
        js = self.js
        self.assertIn('inlineBar(b.market_share_keys_pct, maxShare', js)
        self.assertIn('limitedBadge(', js)
        self.assertIn('data-pipe-group=', js)
        self.assertIn('function openPipelineForGroup', js)
        cards = js[js.index('function renderBrandsCards'):js.index('function openPipelineForGroup')]
        for gone in ('BRAND_DESCRIPTIONS', 'pillHtml', 'SEGMENT_FAMILY'):
            self.assertNotIn(gone, cards)
        self.assertIn("initialsTile(initials, size, gap, 'var(--bg)', 'var(--text-2)')", js)   # neutral initials tile


if __name__ == '__main__':
    unittest.main()
