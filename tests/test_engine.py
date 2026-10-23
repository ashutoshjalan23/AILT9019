import copy
import json
import threading
import unittest
from datetime import datetime
from http.cookiejar import CookieJar
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener

from app.engine import HK, VENUES, chat, is_open, validate_patch
from app.llm import Bailian
from app.server import make_server
from evaluation.run import check
from app.engine import ROOT


class EngineTests(unittest.TestCase):
    def test_proposal_cases(self):
        cases = json.loads((ROOT / 'evaluation/cases.json').read_text())
        for case in cases:
            with self.subTest(case=case['id']):
                _, errors = check(case)
                self.assertEqual(errors, [])

    def test_hours_boundaries_and_weekend(self):
        v = VENUES[0]
        for day,h,m,expected in [(23,7,59,False),(23,8,0,True),(23,20,0,False),(24,9,0,False),(24,10,0,True)]:
            self.assertEqual(is_open(v,datetime(2026,10,day,h,m,tzinfo=HK)),expected)

    def test_overnight_previous_day_schedule(self):
        v = copy.deepcopy(VENUES[0]); v['hours'] = {'weekday':[['22:00','02:00']],'weekend':[]}
        self.assertTrue(is_open(v,datetime(2026,10,24,1,0,tzinfo=HK)))
        self.assertFalse(is_open(v,datetime(2026,10,24,2,0,tzinfo=HK)))
        self.assertFalse(is_open(v,datetime(2026,10,25,1,0,tzinfo=HK)))

    def test_no_relaxing_impossible_budget(self):
        r = chat('At Main Library, vegan under $1',{},datetime(2026,10,23,12,30,tzinfo=HK))
        self.assertEqual(r['kind'],'no_match')

    def test_model_cannot_invent_candidate(self):
        class Fake:
            def complete(self, instruction, payload):
                return {} if 'Extract' in instruction else {'ids':['invented'],'reasons':{'invented':'free'}}
        r = chat('At Main Library, vegetarian',{},datetime(2026,10,23,12,30,tzinfo=HK),Fake())
        self.assertEqual(r['mode'],'hybrid')
        self.assertTrue(r['recommendations'])
        self.assertTrue(all(v['id']!='invented' for v in r['recommendations']))

    def test_valid_model_parsing_and_ranking(self):
        class Fake:
            def complete(self, instruction, payload):
                if 'Extract' in instruction: return {'building':'Main Library','diet':'vegan'}
                return {'ids':['centennial-greens'],'reasons':{'centennial-greens':'Vegan menu tag; starts at HK$35.'}}
        r = chat('Plant-based lunch near the library',{},datetime(2026,10,23,12,30,tzinfo=HK),Fake())
        self.assertEqual(r['mode'],'bailian'); self.assertEqual(r['context']['diet'],'vegan')
        self.assertEqual(r['recommendations'][0]['id'],'centennial-greens')

    def test_api_failure_falls_back(self):
        class Broken:
            def complete(self,*args): raise TimeoutError()
        r = chat('Main Library, cheap',{},datetime(2026,10,23,12,30,tzinfo=HK),Broken())
        self.assertEqual(r['kind'],'recommend'); self.assertEqual(r['mode'],'offline')

    def test_deliberate_offline_mode_has_no_failure_notice(self):
        model = Bailian(); model.enabled = False
        r = chat('Main Library, cheap',{},datetime(2026,10,23,12,30,tzinfo=HK),model)
        self.assertEqual(r['mode'],'offline'); self.assertNotIn('notice',r)

    def test_invalid_filter_values(self):
        for value in ({'diet':'allergy-safe'},{'budget':-1},{'budget':True},{'building':'Made up'},{'clock':'99:00'}):
            with self.subTest(value=value), self.assertRaises(ValueError): validate_patch(value)

    def test_preference_removal_and_location_change(self):
        state = {}; at = datetime(2026,10,23,12,30,tzinfo=HK)
        chat('At Main Library vegetarian under $30',state,at)
        r = chat('At Centennial Campus, any diet, any budget',state,at)
        self.assertNotIn('diet',r['context']); self.assertNotIn('budget',r['context'])
        self.assertEqual(r['context']['building'],'Centennial Campus')

    def test_call_cap_without_network(self):
        model = Bailian(); model.enabled=True; model.key='test-only'; model.limit=0
        with patch('app.llm.urlopen') as network:
            with self.assertRaises(RuntimeError): model.complete('test',{})
            network.assert_not_called()


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Tests never spend course credits, even if a developer has a live .env.
        with patch.dict('os.environ', {'BAILIAN_ENABLED':'false'}):
            cls.server = make_server(0)
        cls.thread = threading.Thread(target=cls.server.serve_forever,daemon=True); cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def send(self, client, path, data):
        req = Request(self.url+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
        with client.open(req) as r: return json.load(r)

    def test_session_isolation_reset_and_static(self):
        a = build_opener(HTTPCookieProcessor(CookieJar())); b = build_opener(HTTPCookieProcessor(CookieJar()))
        self.send(a,'/api/chat',{'message':'At Main Library, vegetarian','at':'2026-10-23T12:30'})
        self.assertEqual(self.send(a,'/api/chat',{'message':'Make it cheaper','at':'2026-10-23T12:30'})['context']['diet'],'vegetarian')
        self.assertEqual(self.send(b,'/api/chat',{'message':'Cheap food'})['kind'],'clarify')
        self.send(a,'/api/reset',{})
        self.assertEqual(self.send(a,'/api/chat',{'message':'Cheap food'})['kind'],'clarify')
        with a.open(self.url+'/') as r: self.assertIn(b'Synthetic data demo',r.read())

    def test_validation_and_cross_origin(self):
        client = build_opener()
        for value in ({'message':''},{'message':3},{'message':'food','at':'bad-date'}):
            with self.subTest(value=value),self.assertRaises(HTTPError) as cm: self.send(client,'/api/chat',value)
            self.assertEqual(cm.exception.code,400)
        req = Request(self.url+'/api/chat',data=b'{"message":"food"}',headers={'Origin':'https://elsewhere.example'})
        with self.assertRaises(HTTPError) as cm: client.open(req)
        self.assertEqual(cm.exception.code,403)


if __name__ == '__main__': unittest.main()
