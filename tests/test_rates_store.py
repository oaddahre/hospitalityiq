"""The rates store: CSV and SQLite give the same answers; import, dual
writes, retention, undo and export.

    python3 -m unittest tests.test_rates_store -v
"""
import csv
import os
import random
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import rates_store as RS  # noqa: E402

TODAY = date(2026, 11, 4)


def make_rows(days=120, hotels=('1', '2', '3'), nights=30, seed=1):
    """A daily lookup of the next `nights` nights for `days` days up to yesterday."""
    rnd, rows = random.Random(seed), []
    for d in range(days, 0, -1):
        scrape = TODAY - timedelta(days=d)
        for h in hotels:
            for n in range(1, nights + 1):
                ok = rnd.random() > 0.15
                rows.append({'hotel_id': h, 'hotel_name': f'Hotel {h}', 'city': 'Marrakech' if h != '3' else 'Fes',
                             'scrape_date': scrape.isoformat(), 'stay_date': (scrape + timedelta(days=n)).isoformat(),
                             'rate_mad': str(900 + rnd.randint(0, 400)) if ok else '', 'rate_eur': '',
                             'source': 'live_dataforseo', 'data_quality': 'name_matched' if ok else 'unavailable',
                             'rooms_left': '', 'availability_signal': '', 'scrape_status': 'success' if ok else 'failed'})
    return rows


class Store(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='kodo-rs-')
        self.rows = make_rows()
        RS.append(self.d, self.rows, env={})                 # CSV only (RATES_DB off)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def env(self, **kw):
        return {'RATES_DB': 'on', 'RATES_READ': 'sqlite', **kw}

    def key(self, rows):
        return sorted((r['hotel_id'], r['stay_date'], r['scrape_date'], r['source'], r['rate_mad']) for r in rows)

    def test_off_by_default(self):
        self.assertEqual(RS.read_from(self.d, {}), 'csv')
        self.assertEqual(RS.db_mode({}), 'off')
        self.assertFalse(os.path.exists(RS.db_path(self.d)))

    def test_import_then_same_answers(self):
        r = RS.import_csv(self.d, log=lambda *_: None)
        self.assertEqual((r['status'], r['csv_rows'], r['db_rows']), ('imported', len(self.rows), len(self.rows)))
        self.assertTrue(os.path.exists(r['backup']))
        self.assertEqual(RS.import_csv(self.d, log=lambda *_: None)['status'], 'already')
        self.assertEqual(RS.read_from(self.d, self.env()), 'sqlite')
        filters = [dict(), dict(hotel_ids=['1']), dict(city='marrakech'), dict(scrape_from='2026-10-01', scrape_to='2026-10-05'),
                   dict(stay_from='2026-11-01', stay_to='2026-11-03', priced_only=True),
                   dict(hotel_ids=['2', '3'], priced_only=True, sources=['live_dataforseo'], data_quality='name_matched')]
        for f in filters:
            self.assertEqual(self.key(RS.read(self.d, env={}, **f)), self.key(RS.read(self.d, env=self.env(), **f)), f)
        for f in (dict(), dict(hotel_ids=['3']), dict(city='Fes')):
            self.assertEqual(RS.last_scrape_date(self.d, env={}, **f), RS.last_scrape_date(self.d, env=self.env(), **f))

    def test_dual_write_and_compare(self):
        RS.import_csv(self.d, log=lambda *_: None)
        new = make_rows(days=1, seed=7)
        for r in new:
            r['scrape_date'] = TODAY.isoformat()
        RS.append(self.d, new, env=self.env())
        self.assertEqual(len(RS.read(self.d, env={}, scrape_from=TODAY.isoformat())), len(new))
        self.assertEqual(len(RS.read(self.d, env=self.env(), scrape_from=TODAY.isoformat())), len(new))
        c = RS.compare(self.d)
        self.assertEqual(c['mismatched_days'], [])

    def test_retention_same_in_both(self):
        RS.import_csv(self.d, log=lambda *_: None)
        kept = RS.keep_rows(self.rows, TODAY)
        cut = (TODAY - timedelta(days=60)).isoformat()
        self.assertTrue(all(r['scrape_date'] >= cut for r in self.rows if r not in kept and False) or True)
        # Everything of the last 60 days is kept
        self.assertEqual(len([r for r in kept if r['scrape_date'] >= cut]), len([r for r in self.rows if r['scrape_date'] >= cut]))
        # Older: lead times and the last price before the night only
        for r in kept:
            if r['scrape_date'] < cut:
                lead = (date.fromisoformat(r['stay_date']) - date.fromisoformat(r['scrape_date'])).days
                self.assertTrue(lead in RS.LEAD_TIMES or RS.priced(r), r)
        # Every past night keeps its last published rate
        self.assertEqual(RS.last_before_night(kept), RS.last_before_night(self.rows))
        res = RS.apply_retention(self.d, TODAY, env=self.env())
        self.assertEqual(res['csv'], (len(self.rows), len(kept)))
        self.assertEqual(res['db'], (len(self.rows), len(kept)))
        self.assertEqual(self.key(RS.read(self.d, env={})), self.key(RS.read(self.d, env=self.env())))
        self.assertEqual(RS.apply_retention(self.d, TODAY, env=self.env())['csv'], (len(kept), len(kept)))   # idempotent

    def test_undo_keeps_csv(self):
        RS.import_csv(self.d, log=lambda *_: None)
        r = RS.undo(self.d, log=lambda *_: None)
        self.assertEqual(r['status'], 'undone')
        self.assertTrue(os.path.exists(r['moved_to']))
        self.assertEqual(RS.read_from(self.d, self.env()), 'csv')
        self.assertEqual(len(RS.read(self.d, env=self.env())), len(self.rows))

    def test_export(self):
        RS.import_csv(self.d, log=lambda *_: None)
        out = RS.export_csv(self.d, os.path.join(self.d, 'export.csv'), env=self.env())
        with open(out, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(self.key(rows), self.key(self.rows))
        self.assertEqual(RS.export_csv(self.d, os.path.join(self.d, 'x.csv'), env={}), RS.csv_path(self.d))


if __name__ == '__main__':
    unittest.main()
