"""Brand page on the UI standard: back, logo tile, name, one line (hotels,
keys, destinations), a Destination select filtering the page, four compact
cards, About in three lines with Read more, the hotels table (inline bars,
status as text) in place of the BAR-by-hotel chart, the group's pipeline
projects linked to the Pipeline.

    python3 -m unittest tests.test_brand_page -v
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


class BrandPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html = read('templates', 'index.html')
        cls.page = html[html.index('<section class="screen" id="screen-brand">'):]
        cls.page = cls.page[:cls.page.index('</section>')]
        cls.js = read('static', 'js', 'main.js')

    def test_layout(self):
        p = self.page
        for i in ('brand-back-btn', 'brand-detail-logo', 'brand-detail-name', 'brand-detail-line', 'brand-dest-select',
                  'brand-about-more', 'brand-hotels-table', 'brand-pipe-card', 'brand-pipe-open'):
            self.assertIn(f'id="{i}"', p)
        self.assertIn('kpi-compact', p)
        for col in ('name', 'city', 'category', 'keys', 'bar_mad', 'occupancy', 'status'):
            self.assertIn(f'data-bcol="{col}"', p)
        for gone in ('chart-brand-revpar', 'brand-cities-row', 'Present in', 'brand-about-card'):
            self.assertNotIn(gone, p + self.js[self.js.index('function showBrandDetail'):self.js.index('function renderBrandHotelsTable')])

    def test_scope_and_pipeline(self):
        js = self.js
        scope = js[js.index('function renderBrandScope'):js.index('async function renderBrandPipeline')]
        self.assertIn("`${nDest} destination${nDest !== 1 ? 's' : ''}`", scope)
        self.assertIn("label: 'BAR (median)', kind: 'adr'", scope)
        pipe = js[js.index('async function renderBrandPipeline'):js.index('function renderBrandHotelsTable')]
        self.assertIn('pipeBrandGroup(p) === bg', pipe)
        self.assertIn("openPipelineForGroup(brandDetailGroup)", js)
        table = js[js.index('function renderBrandHotelsTable'):]
        table = table[:table.index('\n}\n')]
        self.assertIn('inlineBar(h.bar_mad, maxBar', table)
        self.assertNotIn('getSegmentBadgeHtml', table)

    def test_about_three_lines(self):
        css = read('static', 'css', 'style.css')
        self.assertIn('-webkit-line-clamp: 3;', css[css.index('.brand-about-text {'):][:400])


if __name__ == '__main__':
    unittest.main()
