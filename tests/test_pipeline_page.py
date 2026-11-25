"""Pipeline page on the UI standard: title + one line, four count cards, one
filter row, one main view (table by default, cards, map), no investment
chart or card, neutral stage pills, no category colours.

    python3 -m unittest tests.test_pipeline_page -v
"""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


class PipelinePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html = read('templates', 'index.html')
        cls.page = html[html.index('<section class="screen" id="screen-pipeline">'):]
        cls.page = cls.page[:cls.page.index('</section>')]
        js = read('static', 'js', 'main.js')
        cls.js = js[js.index('// ─── Pipeline screen'):js.index('// ─── Editorial / News screen')]

    def test_layout(self):
        p = self.page
        self.assertIn('<h1 class="k-title">Pipeline</h1>', p)
        for i in ('pkpi-total', 'pkpi-keys', 'pkpi-soon', 'pkpi-uc'):
            self.assertIn(f'id="{i}"', p)
        self.assertEqual(p.count('class="k-kpi"'), 4)
        for stage in ('all', 'Planning', 'Under Construction', 'soon', 'Opened'):
            self.assertIn(f'data-stage="{stage}"', p)
        for v in ('table', 'cards', 'map'):
            self.assertIn(f'data-view="{v}"', p)
        self.assertIn('id="pipe-city-filter"', p)
        self.assertIn('id="pipe-group-filter"', p)
        self.assertIn('id="pipe-search"', p)
        self.assertIn('data-psort="expected_opening" class="num" aria-sort="ascending"', p)   # default sort

    def test_removed(self):
        p = self.page
        for gone in ('Investment by City', 'chart-pipeline-city', 'pkpi-inv', 'Est. Investment', '<canvas', 'pipe-table-toggle'):
            self.assertNotIn(gone, p)
        self.assertNotIn('renderPipelineCharts', read('static', 'js', 'main.js'))

    def test_no_category_colour(self):
        for text in (self.page, self.js):
            self.assertNotRegex(text, r'pill--(blue|green|orange|violet|sky)|--cat-[1-5]|familyDot\(')
            self.assertNotIn('getSegmentBadgeHtml', text)
        self.assertIn("'<span class=\"k-pill k-pill--solid\">Under construction</span>'", self.js)
        self.assertIn("'<span class=\"k-pill\">Planning</span>'", self.js)

    def test_markers_neutral_selected_blue(self):
        icon = self.js[self.js.index('function pipeMarkerIcon'):self.js.index('function pipeRestyleMarkers')]
        for t in ("'--action'", "'--text'", "'--text-3'"):
            self.assertIn(t, icon)

    def test_updated_endpoint_same_plan(self):
        app = read('app.py')
        i = app.index('@app.route("/api/pipeline/updated")')
        self.assertIn('@tier_required("benchmarker")', app[i:i + 200])
        self.assertIn('@login_required', app[i:i + 200])


if __name__ == '__main__':
    unittest.main()
