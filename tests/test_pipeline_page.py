"""Pipeline page on the UI standard: title + one line, four count cards, one
filter row, one main view (table by default or cards) with the map always
under it, following the filters; no investment
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
        for v in ('table', 'cards'):
            self.assertIn(f'data-view="{v}"', p)
        self.assertNotIn('data-view="map"', p)                                  # the map is not a view
        self.assertNotIn('data-pview="map"', p)
        self.assertIn('id="pipeline-map-container"', p)
        self.assertLess(p.index('id="btn-export-pipeline"'), p.index('id="pipeline-map-container"'))
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

    def test_view_switch(self):
        self.assertIn("const PIPE_VIEWS = ['table', 'cards'];", self.js)
        css = read('static', 'css', 'style.css')
        self.assertIn('#screen-pipeline [data-pview][hidden] { display: none !important; }', css)
        self.assertIn('#screen-pipeline #pipeline-map-container { height: 460px;', css)
        self.assertIn('#screen-pipeline #pipeline-map-container { height: 320px; }', css)

    def test_map_follows_filters_and_selection(self):
        f = self.js[self.js.index('function applyPipelineFilter'):self.js.index('let pipeSelectedId')]
        self.assertIn('marker.setMap(ids.has(project.id)', f)
        show = self.js[self.js.index('function pipeShowProject'):self.js.index('function pipelinePopupHTML')]
        self.assertIn("scrollIntoView", show)
        self.assertIn('pipeOpenOnMap(', show)
        self.assertIn('pipeMarkSelected();', self.js[self.js.index('function pipeOpenOnMap'):])
        self.assertNotIn("pipeSetView('map')", self.js)
        exp = read('static', 'js', 'main.js')
        exp = exp[exp.index('function exportPipeline'):]
        self.assertIn('filteredPipeline()', exp[:exp.index('\n}\n')])

    def test_markers_neutral_selected_blue(self):
        icon = self.js[self.js.index('function pipeMarkerIcon'):self.js.index('function pipeRestyleMarkers')]
        for t in ("'--text'", "'--text-2'", "'--text-3'"):
            self.assertIn(t, icon)
        self.assertNotIn('--action', icon)                                      # no blue: the open marker is black

    def test_updated_endpoint_same_plan(self):
        app = read('app.py')
        i = app.index('@app.route("/api/pipeline/updated")')
        self.assertIn('@tier_required("benchmarker")', app[i:i + 200])
        self.assertIn('@login_required', app[i:i + 200])


if __name__ == '__main__':
    unittest.main()
