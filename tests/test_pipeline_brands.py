"""Pipeline: every project shows its brand group's logo tile (the Brands
page's local logos and initials tiles, never a remote image) and the brand
opens that group's page on Brands without the card's own click.

    python3 -m unittest tests.test_pipeline_brands -v
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


class PipelineBrands(unittest.TestCase):
    def setUp(self):
        self.js = read('static', 'js', 'main.js')

    def test_every_pipeline_view_uses_the_brand_tile(self):
        for fn in ('function pipelinePopupHTML', 'function renderPipelineCards', 'function renderPipelineTableView',
                   'async function renderHotelPipeline'):
            body = self.js[self.js.index(fn):]
            body = body[:body.index('\n}\n')]
            self.assertIn('pipeBrandHtml(p, ', body, fn)
            self.assertNotIn('fmt.esc(p.brand)', body, fn)

    def test_local_logos_only_and_own_click(self):
        tile = self.js[self.js.index('function pipeBrandTile'):self.js.index('function pipeOpenBrand')]
        self.assertNotIn('brandfetch', tile)
        self.assertNotIn('getBrandLogoImg', tile)
        self.assertIn('LOCAL_BRAND_LOGOS[bg]', tile)
        self.assertIn('BRAND_CUSTOM_LOGOS[bg]', tile)
        self.assertIn("initialsTile('?'", tile)                              # no group stored: neutral tile
        self.assertIn('if (!pipeHasBrandPage(bg)) return `<span', tile)    # no page: no link
        opener = self.js[self.js.index('function pipeOpenBrand'):]
        self.assertIn('e.stopPropagation()', opener[:300])
        self.assertIn('showBrandDetail(el.dataset.brandGroup', opener[:400])
        css = read('static', 'css', 'style.css')
        self.assertIn('.pipe-brand-link:focus-visible { outline: 2px solid var(--action)', css)


if __name__ == '__main__':
    unittest.main()
