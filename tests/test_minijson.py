import typing as tp
import unittest

from minijson import dumps, loads, dumps_object, loads_object, EncodingError, DecodingError, \
    switch_default_double, switch_default_float, MiniJSONEncoder


class TestMiniJSON(unittest.TestCase):

    def test_encoder_strict_output(self):
        enc = MiniJSONEncoder(use_strict_order=True)
        enc.encode({"test": "2", "value": 2})
        enc.encode({b"test": "2", b"value": 2})

    def test_encoder_overrided_default(self):
        class Encoder(MiniJSONEncoder):
            def default(self, v):
                return v.real, v.imag

        e = Encoder()
        e.encode(2 + 3j)

    def test_bytes(self):
        a = {b'test': b'dupa'}
        e = MiniJSONEncoder()
        b = e.encode(a)
        self.assertEqual(loads(b), a)

    def test_bytes_26(self):
        a = b'x' * 256
        e = MiniJSONEncoder()
        b = e.encode(a)
        self.assertEqual(loads(b), a)
        self.assertEqual(len(b), 256 + 3)

    def test_bytes_27(self):
        e = MiniJSONEncoder()
        a = b'x' * 65537
        b = e.encode(a)
        self.assertEqual(loads(b), a)
        self.assertEqual(len(b), 65537 + 5)

    def test_encoder_given_default(self):
        def encode(v):
            return v.real, v.imag

        e = MiniJSONEncoder(default=encode)
        e.encode(2 + 3j)

    def test_encoder_no_default(self):
        e = MiniJSONEncoder()
        self.assertRaises(EncodingError, lambda: e.encode(2 + 3j))

    def test_accepts_bytearrays(self):
        b = {'test': 'hello'}
        a = dumps(b)
        a = bytearray(a)
        self.assertEqual(loads(a), b)

    def assertLoadingIsDecodingError(self, b: bytes):
        self.assertRaises(DecodingError, lambda: loads(b))

    def assertSameAfterDumpsAndLoads(self, c, repres: tp.Optional[bytes] = None):
        b = dumps(c)
        if repres is not None:
            self.assertEqual(b, repres)
        d = loads(b)
        self.assertEqual(c, d)

    def test_default_returns_nonjsonable(self):
        """Assert that if transform returns a non-JSONable value, EncodingError is raised"""

        def transform(c):
            return c

        self.assertRaises(EncodingError, lambda: dumps(2 + 3j, transform))

    def test_default(self):
        """Assert the default argument works"""

        def transform(c):
            return c.real, c.imag

        dumps(2 + 3j, transform)
        dumps({'test': 2 + 3j}, transform)

    def test_subclasses_of_dicts(self):
        """Assert that you can correctly serialize subclasses of dict"""

        class Subclass(dict):
            pass

        a = Subclass({1: 2, 3: 4})
        b = dumps(a)
        self.assertEqual(loads(b), {1: 2, 3: 4})

    def test_should_double_be_used(self):
        class Encoder(MiniJSONEncoder):
            def should_double_be_used(self, y):
                return y == 0

        e = Encoder()

        self.assertEqual(len(e.encode(0.0)), 9)
        self.assertEqual(len(e.encode(1.0)), 5)

    def test_subclasses_of_lists(self):
        """Assert that you can correctly serialize subclasses of list"""

        class Subclass(list):
            pass

        a = Subclass([1, 2, 3])
        b = dumps(a)
        self.assertEqual(loads(b), [1, 2, 3])

    def test_subclasses_of_tuples(self):
        """Assert that you can correctly serialize subclasses of tuple"""

        class Subclass(tuple):
            pass

        a = Subclass((1, 2, 3))
        b = dumps(a)
        self.assertEqual(loads(b), [1, 2, 3])

    def test_malformed(self):
        """Test unserializing malformed strings yields DecodingError"""
        self.assertRaises(EncodingError, lambda: dumps(2 + 3j))
        self.assertLoadingIsDecodingError(b'\x00\x02a')
        self.assertLoadingIsDecodingError(b'\x00\x02a')
        self.assertLoadingIsDecodingError(b'\x09\x00')
        self.assertLoadingIsDecodingError(b'\x82\x00')

    def test_short_nonstring_key_dicts(self):
        self.assertSameAfterDumpsAndLoads({i: i for i in range(20)})
        self.assertSameAfterDumpsAndLoads({i: i for i in range(300)})
        self.assertSameAfterDumpsAndLoads({i: i for i in range(66000)})

    def test_smok_bug_case_2(self):
        self.assertSameAfterDumpsAndLoads({"zażółć gęślą jaźń": "zażółć gęślą jaźń"})

    def test_invalid_name_dict(self):
        self.assertLoadingIsDecodingError(b'\x15\x01\x81\x01')
        self.assertLoadingIsDecodingError(b'\x0B\x01\x01\xFF\x15')
        self.assertLoadingIsDecodingError(b'\x0D\x01\x00\x00')
        self.assertLoadingIsDecodingError(b'\x0E\x00\x00\x01\x00\x00')

    def test_encode_double(self):
        switch_default_double()
        b = dumps(4.5)
        self.assertGreaterEqual(len(b), 5)
        self.assertEqual(loads(b), 4.5)
        switch_default_float()

    def test_minijson_encoder_returns_a_bool_and_a_bytes(self):
        class Encoder(MiniJSONEncoder):
            def default(self, v):
                if isinstance(v, complex):
                    return True
                else:
                    return b'test'

        e = Encoder()
        e.encode(3 + 4j)
        e.encode(object())

    def test_smok_bug(self):
        a = [{'service': 'gui', 'when': 1628873412444398,
              'message': "DEBUG:gui.run:Loaded {'aspect_ratio': {'width': 16, 'height': 9}, 'menu': [{'label': 'GBówna', 'id': 'main'}], 'visualizations': [{'label': 'GBówna', 'id': 'main', 'elements': [{'type': 'text', 'zindex': 15, 'text': 'Stan wejsciowy alarmu', 'top': 10, 'left': 10, 'size': 5}, {'type': 'input', 'zindex': 15, 'widget_type': {'type': 'input'}, 'fqts': 'prog wej1', 'readonly': False, 'top': 10, 'left': 20, 'input_size': 5}, {'type': 'text', 'zindex': 15, 'text': 'Stan wyjsciowy alarmu', 'top': 20, 'left': 10, 'size': 5}, {'type': 'input', 'zindex': 15, 'widget_type': {'type': 'input'}, 'fqts': 'prog wyj1', 'readonly': True, 'top': 20, 'left': 20, 'input_size': 5}]}]} as visualizations",
              'level': 10}]
        self.assertSameAfterDumpsAndLoads(a)
        a = [{'service': 'gui', 'when': 1628873412444398,
              'message': "DEBUG:gui.run:Loaded {'aspect_ratio': {'width': 16, 'height': 9}, 'menu': [{'label': 'GBówna', 'id': 'main'}], 'visualizations': [{'label': 'GBówna', 'id': 'main', 'elements': [{'type': 'text', 'zindex': 15, 'text': 'Stan wejsciowy alarmu', 'top': 10, 'left': 10, 'size': 5}, {'type': 'input', 'zindex': 15, 'widget_type': {'type': 'input'}, 'fqts': 'prog wej1', 'readonly': False, 'top': 10, 'left': 20, 'input_size': 5}, {'type': 'text', 'zindex': 15, 'text': 'Stan wyjsciowy alarmu', 'top': 20, 'left': 10, 'size': 5}, {'type': 'input', 'zindex': 15, 'widget_type': {'type': 'input'}, 'fqts': 'prog wyj1', 'readonly': True, 'top': 20, 'left': 20, 'input_size': 5}]}]} as visualizations",
              'level': 10}, {'service': 'gui', 'when': 1628873412444961,
                             'message': 'DEBUG:rapid.channels:Reconnecting leds current amount of users is 0 due_to_failures=False',
                             'level': 10}, {'service': 'gui', 'when': 1628873412446439,
                                            'message': 'DEBUG:rapid.channels:Successfully reconnected leds',
                                            'level': 10}]
        self.assertSameAfterDumpsAndLoads(a)

    def test_booleans(self):
        self.assertSameAfterDumpsAndLoads({'test': True,
                                           'test2': False})

    def test_string(self):
        self.assertSameAfterDumpsAndLoads('test')
        self.assertSameAfterDumpsAndLoads('t' * 128)
        self.assertSameAfterDumpsAndLoads('t' * 65535)
        self.assertSameAfterDumpsAndLoads('t' * 65540)

    def test_lists(self):
        self.assertSameAfterDumpsAndLoads([None] * 4)
        self.assertSameAfterDumpsAndLoads([None] * 256)
        self.assertSameAfterDumpsAndLoads([None] * 17)

    def test_long_dicts(self):
        self.assertSameAfterDumpsAndLoads({str(i): i for i in range(17)})

    def test_dicts_not_string_keys(self):
        self.assertSameAfterDumpsAndLoads({i: i for i in range(17)})

    def test_long_dicts_and_lists(self):
        self.assertSameAfterDumpsAndLoads({str(i): i * 2 for i in range(65535)})
        self.assertSameAfterDumpsAndLoads({str(i): i * 2 for i in range(0x1FFFFF)})
        self.assertSameAfterDumpsAndLoads(list(range(0xFFFF)))
        self.assertSameAfterDumpsAndLoads(list(range(0x1FFFF)))

    def test_weird_dict(self):
        self.assertSameAfterDumpsAndLoads({'a' * 300: 2})

    def test_negatives(self):
        self.assertSameAfterDumpsAndLoads(-1, b'\x03\xFF')
        self.assertSameAfterDumpsAndLoads(-259, b'\x02\xfe\xfd')
        self.assertSameAfterDumpsAndLoads(-0x7FFF, b'\x02\x80\x01')
        self.assertSameAfterDumpsAndLoads(-0xFFFF, b'\x01\xff\xff\x00\x01')
        self.assertSameAfterDumpsAndLoads(0x1FFFF)
        self.assertSameAfterDumpsAndLoads(0xFFFFFFFF)
        self.assertSameAfterDumpsAndLoads(0x1FFFFFF)
        self.assertSameAfterDumpsAndLoads(0xFFFFFFFFF)
        self.assertSameAfterDumpsAndLoads(0xFFFFFFFFFFFFF)
        self.assertSameAfterDumpsAndLoads(0xFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        self.assertSameAfterDumpsAndLoads(-0xFFFFFFFFFFFFFFFFFFFFFFFFFFFF)

    def test_dumps(self):
        self.assertSameAfterDumpsAndLoads({"name": "land", "operator_id": "dupa", "parameters":
            {"lat": 45.22999954223633, "lon": 54.79999923706055, "alt": 234}})

    def test_loads_exception(self):
        self.assertLoadingIsDecodingError(b'')
        self.assertLoadingIsDecodingError(b'\x1F')
        self.assertLoadingIsDecodingError(b'\x00\x01')
        self.assertLoadingIsDecodingError(b'\x00\x01\xFF')
        self.assertLoadingIsDecodingError(b'\x81\xFF')
        self.assertLoadingIsDecodingError(b'\x0B\x03\x04name\x84land')

    def test_loads(self):
        a = loads(
            b'\x0B\x03\x04name\x84land\x0Boperator_id\x84dupa\x0Aparameters\x0B\x03\x03lat\x09B4\xeb\x85\x03lon\x09B[33\x03alt\x09Cj\x00\x00')
        self.assertEqual(a, {"name": "land", "operator_id": "dupa", "parameters":
            {"lat": 45.22999954223633, "lon": 54.79999923706055, "alt": 234}})

    def test_dumps_loads_object(self):
        class Test:
            def __init__(self, a):
                self.a = a

        a = Test(2)
        b = dumps_object(a)
        c = loads_object(b, Test)
        self.assertEqual(a.a, c.a)
        self.assertIsInstance(c, Test)
        self.assertRaises(DecodingError, lambda: loads_object(b'\x07\x00', Test))
