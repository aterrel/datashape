import numpy as np

from datashape.discovery import (discover, null, unite_identical, unite_base,
        unite_merge_dimensions, do_one)
from datashape.coretypes import *
from datashape.internal_utils import raises
from datashape.py2help import skip
from datashape import dshape

def test_simple():
    assert discover(3) == int64
    assert discover(3.0) == float64
    assert discover(3.0 + 1j) == complex128
    assert discover('Hello') == string
    assert discover(True) == bool_
    assert discover(None) == null


def test_list():
    print(discover([1, 2, 3]))
    assert discover([1, 2, 3]) == 3 * discover(1)
    assert discover([1.0, 2.0, 3.0]) == 3 * discover(1.0)


def test_heterogeneous_ordered_container():
    print(discover(('Hello', 1)))
    assert discover(('Hello', 1)) == Tuple([discover('Hello'), discover(1)])



def test_string():
    assert discover('1') == discover(1)
    assert discover('1.0') == discover(1.0)
    assert discover('True') == discover(True)
    assert discover('true') == discover(True)


def test_record():
    assert discover({'name': 'Alice', 'amount': 100}) == \
            Record([['amount', discover(100)],
                    ['name', discover('Alice')]])


def test_datetime():
    inputs = ["1991-02-03 04:05:06",
              "11/12/1822 06:47:26.00",
              "1822-11-12T06:47:26",
              "Fri Dec 19 15:10:11 1997",
              "Friday, November 11, 2005 17:56:21",
              "1982-2-20 5:02:00",
              "20030331 05:59:59.9",
              "Jul  6 2030  5:55PM",
              "1994-10-20 T 11:15",
              "2013-03-04T14:38:05.123",
              # "15MAR1985:14:15:22",
              # "201303041438"
              ]
    for dt in inputs:
        assert discover(dt) == datetime_


def test_date():
    assert discover('2014-01-01') == date_


def test_integrative():
    data = [{'name': 'Alice', 'amount': '100'},
            {'name': 'Bob', 'amount': '200'},
            {'name': 'Charlie', 'amount': '300'}]

    assert dshape(discover(data)) == \
            dshape('3 * {amount: int64, name: string}')


def test_numpy_scalars():
    assert discover(np.int32(1)) == int32
    assert discover(np.float64(1)) == float64


def test_numpy_array():
    assert discover(np.ones((3, 2), dtype=np.int32)) == dshape('3 * 2 * int32')


unite = do_one([unite_identical,
                unite_merge_dimensions,
                unite_base])

def test_unite():
    assert unite([int32, int32, int32]) == 3 * int32
    assert unite([3 * int32, 2 * int32]) == 2 * (var * int32)
    assert unite([2 * int32, 2 * int32]) == 2 * (2 * int32)
    assert unite([3 * (2 * int32), 2 * (2 * int32)]) == 2 * (var * (2 * int32))


def test_unite_missing_values():
    assert unite([int32, null, int32]) == 3 * Option(int32)
    assert unite([string, null, int32])


def test_unite_tuples():
    assert discover([[1, 1, 'hello'],
                     [1, '', ''],
                     [1, 1, 'hello']]) == \
                    3 * Tuple([int64, Option(int64), Option(string)])

    assert discover([[1, 1, 'hello', 1],
                     [1, '', '', 1],
                     [1, 1, 'hello', 1]]) == \
                    3 * Tuple([int64, Option(int64), Option(string), int64])

def test_unite_records():
    discover([{'name': 'Alice', 'balance': 100},
              {'name': 'Bob', 'balance': ''}]) == \
            2 * Record([['name', string], ['balance', Option(int64)]])

    # assert unite((Record([['name', string], ['balance', int32]]),
    #               Record([['name', string]]))) == \
    #                 Record([['name', string], ['balance', Option(int32)]])



def test_dshape_missing_data():
    assert discover([[1, 2, '', 3],
                     [1, 2, '', 3],
                     [1, 2, '', 3]]) == \
                3 * Tuple([int64, int64, null, int64])


def test_discover_mixed():
    i = discover(1)
    f = discover(1.0)
    assert dshape(discover([[1, 2, 1.0, 2.0]] * 10)) == \
            10 * Tuple([i, i, f, f])

    print(dshape(discover([[1, 2, 1.0, 2.0], [1.0, 2.0, 1, 2]] * 5)))
    assert dshape(discover([[1, 2, 1.0, 2.0], [1.0, 2.0, 1, 2]] * 5)) == \
            10 * (4 * f)


def test_test():
    print(discover([['Alice', 100], ['Bob', 200]]))
    print(2 * Tuple([string, int64]))
    assert discover([['Alice', 100], ['Bob', 200]]) == \
            2 * Tuple([string, int64])

def test_discover_appropriate():
    assert discover((1, 1.0)) == Tuple([int64, real])
    print(discover([(1, 1.0), (1, 1.0), (1, 1)]))
    assert discover([(1, 1.0), (1, 1.0), (1, 1)]) == \
            3 * Tuple([int64, real])

def test_big_discover():
    data = [['1'] + ['hello']*20] * 10
    assert discover(data) == 10 * Tuple([int64] + [string]*20)


def test_unite_base():
    assert unite_base([date_, datetime_]) == 2 * datetime_
