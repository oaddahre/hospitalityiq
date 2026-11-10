"""The bare domain kodohospitality.com → https://www.kodohospitality.com,
same path and query string, 301, over http and https; www and the Railway
domain are not redirected, so there is no loop.

    python3 -m unittest tests.test_bare_domain -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (host, X-Forwarded-Proto, path with query) for each request, made by the
# app's test client in a child process with a scratch DATA_DIR
CASES = [
    ('kodohospitality.com', 'http', '/'),
    ('kodohospitality.com', 'https', '/'),
    ('kodohospitality.com', 'http', '/about'),
    ('kodohospitality.com', 'https', '/about?utm_source=x&a=1'),
    ('kodohospitality.com', 'https', '/team'),
    ('KodoHospitality.com.', 'https', '/about'),
    ('kodohospitality.com:443', 'https', '/about'),
    ('kodohospitality.com', 'https', '/a%20b/caf%C3%A9?q=%C3%A9t%C3%A9'),
    ('www.kodohospitality.com', 'https', '/about'),
    ('www.kodohospitality.com', 'http', '/about'),
    ('example-app.up.railway.app', 'https', '/about'),
]

CHILD = r"""
import json, sys
sys.path.insert(0, %r)
import app as A
c = A.app.test_client()
out = []
for host, proto, url in json.loads(sys.argv[1]):
    r = c.get(url, headers={'Host': host, 'X-Forwarded-Proto': proto})
    out.append([r.status_code, r.headers.get('Location')])
print(json.dumps(out))
"""


class BareDomain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = tempfile.mkdtemp(prefix='kodo-host-')
        try:
            for f in ('hotels.csv', 'performance.csv', 'pipeline.csv', 'owners.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            env = {**os.environ, 'DATA_DIR': d, 'ANTHROPIC_API_KEY': '', 'RESEND_API_KEY': '',
                   'DATA_MIGRATIONS': 'off'}
            p = subprocess.run([sys.executable, '-c', CHILD % ROOT, json.dumps(CASES)],
                               env=env, capture_output=True, text=True, cwd=ROOT)
            if p.returncode:
                raise RuntimeError(p.stderr[-2000:])
            cls.res = dict(zip((tuple(c) for c in CASES), json.loads(p.stdout.strip().splitlines()[-1])))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def get(self, host, proto, url):
        return self.res[(host, proto, url)]

    def test_http_and_https_go_to_www_with_the_same_path(self):
        for proto in ('http', 'https'):
            self.assertEqual(self.get('kodohospitality.com', proto, '/'),
                             [301, 'https://www.kodohospitality.com/'])
        self.assertEqual(self.get('kodohospitality.com', 'http', '/about'),
                         [301, 'https://www.kodohospitality.com/about'])
        self.assertEqual(self.get('kodohospitality.com', 'https', '/team'),
                         [301, 'https://www.kodohospitality.com/team'])

    def test_query_string_kept(self):
        self.assertEqual(self.get('kodohospitality.com', 'https', '/about?utm_source=x&a=1'),
                         [301, 'https://www.kodohospitality.com/about?utm_source=x&a=1'])

    def test_encoded_path_and_query_unchanged(self):
        self.assertEqual(self.get('kodohospitality.com', 'https', '/a%20b/caf%C3%A9?q=%C3%A9t%C3%A9'),
                         [301, 'https://www.kodohospitality.com/a%20b/caf%C3%A9?q=%C3%A9t%C3%A9'])

    def test_host_case_port_and_trailing_dot(self):
        for host in ('KodoHospitality.com.', 'kodohospitality.com:443'):
            self.assertEqual(self.get(host, 'https', '/about'),
                             [301, 'https://www.kodohospitality.com/about'])

    def test_www_and_railway_not_redirected_so_no_loop(self):
        for host, proto in (('www.kodohospitality.com', 'https'), ('www.kodohospitality.com', 'http'),
                            ('example-app.up.railway.app', 'https')):
            self.assertEqual(self.get(host, proto, '/about')[0], 200, host)


if __name__ == '__main__':
    unittest.main()
