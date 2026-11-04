"""Hotel type: name words only make small hotels riads.

    python3 -m unittest tests.test_hotel_type -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from occupancy_model import classify_hotel_type  # noqa: E402


def h(name, city, keys):
    return {'name': name, 'city': city, 'keys': str(keys)}


class HotelType(unittest.TestCase):
    def test_large_palais_is_typed_by_city(self):
        self.assertEqual(classify_hotel_type(h('Sofitel Marrakech Palais Imperial & Spa', 'Marrakech', 330)), 'cultural_leisure')
        self.assertEqual(classify_hotel_type(h('Pickalbatros Palais des Roses', 'Agadir / Taghazout', 405)), 'beach_resort')
        self.assertEqual(classify_hotel_type(h('The Ritz-Carlton Rabat Dar Es Salam', 'Rabat / Salé / Témara', 117)), 'city_business')

    def test_small_and_mid_keep_the_name_rule(self):
        self.assertEqual(classify_hotel_type(h('Riad Fes', 'Fes', 30)), 'riad_boutique')
        self.assertEqual(classify_hotel_type(h('Valeria Kasbah del Mar', 'Tamuda Bay / Tétouan', 72)), 'riad_boutique')   # 60-99: not changed yet
        self.assertEqual(classify_hotel_type(h('Any Hotel', 'Casablanca', 20)), 'riad_boutique')                       # under 30 rooms


if __name__ == '__main__':
    unittest.main()
