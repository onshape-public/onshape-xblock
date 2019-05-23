from onshape_xblock.utility import dig_into_dict, quantify, u, merge_d
from onshape_xblock.serialize import Serialize
import os

def test_quantify():
    assert quantify(0) == 0 * u.meter
    assert quantify(1) == 1 * u.meter
    assert quantify("0") == 0 * u.meter
    assert quantify("1") == 1 * u.meter
    assert quantify(0, default_units=u.kg) == 0 * u.kg
    assert quantify(1, default_units=u.kg) == 1 * u.kg
    assert quantify("1", default_units=u.kg) == 1 * u.kg
    assert quantify(1, default_units=u.kg, tolerance=0.01)
    assert quantify("3 meter") == 3*u.m
    assert quantify("3 meter**3") == 3 * u.m ** 3

def test_dig_into_dict():
    d = {'a':1, 'b':{'ba':21, 'bb':22, 'bc': {'bda':241}}}
    assert dig_into_dict(d, None) == d
    assert dig_into_dict(d, ['b']) == {'ba':21, 'bb':22, 'bc': {'bda':241}}
    assert dig_into_dict(d, ['b', 'bb']) == 22
