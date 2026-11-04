"""Hotel type: name words only make hotels of 40 rooms or fewer riads.

    python3 -m unittest tests.test_hotel_type -v
"""
import csv
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from occupancy_model import classify_hotel_type  # noqa: E402


def h(name, city, keys, hid=''):
    return {'id': hid, 'name': name, 'city': city, 'keys': str(keys)}


class HotelType(unittest.TestCase):
    def test_under_30_rooms_is_a_riad(self):
        self.assertEqual(classify_hotel_type(h('Any Hotel', 'Casablanca', 20)), 'riad_boutique')

    def test_name_word_up_to_40_rooms(self):
        self.assertEqual(classify_hotel_type(h('Riad Fes', 'Fes', 40)), 'riad_boutique')
        self.assertEqual(classify_hotel_type(h('Dar Kamar Ouarzazate', 'Ouarzazate', 47)), 'cultural_leisure')
        self.assertEqual(classify_hotel_type(h('Sofitel Marrakech Palais Imperial & Spa', 'Marrakech', 330)), 'cultural_leisure')
        self.assertEqual(classify_hotel_type(h('Pickalbatros Palais des Roses', 'Agadir / Taghazout', 405)), 'beach_resort')
        self.assertEqual(classify_hotel_type(h('The Ritz-Carlton Rabat Dar Es Salam', 'Rabat / Salé / Témara', 117)), 'city_business')

    def test_desert_kasbahs_and_camps_are_leisure(self):
        self.assertEqual(classify_hotel_type(h('Kasbah Somewhere', 'Zagora', 60)), 'cultural_leisure')
        self.assertEqual(classify_hotel_type(h('Desert Camp', 'Errachidia', 50)), 'cultural_leisure')
        self.assertEqual(classify_hotel_type(h('Kenzi Rissani', 'Errachidia', 61)), 'city_business')    # no name word

    def test_overrides(self):
        self.assertEqual(classify_hotel_type(h('Hôtel LAKASBAH Aït Ben Haddou', 'Ouarzazate', 85, '210')), 'cultural_leisure')
        self.assertEqual(classify_hotel_type(h('Valeria Kasbah del Mar', 'Tamuda Bay / Tétouan', 72, '452')), 'beach_resort')
        self.assertEqual(classify_hotel_type(h('Kasbah Baha Baha', 'Zagora', 60, '238')), 'cultural_leisure')
        self.assertEqual(classify_hotel_type(h('Kasbah Tamadot', 'Marrakech', 42, '61')), 'riad_boutique')

    def test_repo_list(self):
        """Every hotel in hotels.csv against the expected changes of Nov 2026."""
        rows = {r['id']: r for r in csv.DictReader(open(os.path.join(ROOT, 'hotels.csv'), encoding='utf-8'))}
        expect = {'210': 'cultural_leisure', '452': 'beach_resort', '238': 'cultural_leisure', '108': 'cultural_leisure',
                  '61': 'riad_boutique', '232': 'riad_boutique', '156': 'riad_boutique', '14': 'cultural_leisure'}
        for hid, t in expect.items():
            self.assertEqual(classify_hotel_type(rows[hid]), t, rows[hid]['name'])


if __name__ == '__main__':
    unittest.main()
