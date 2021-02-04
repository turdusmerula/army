from army.api.log import log
from army.api.version import Version, VersionRange, VersionException
from helper import raised, run
import os
import unittest

log.setLevel('CRITICAL')


class TestVersionRange(unittest.TestCase):
    def test_filter(self):
        range = VersionRange(["0.0.1", "0.0.2", "1.0.0"])
        assert len(range.filter("0.0.1"))==1
        assert len(range.filter(">0.0.2"))==1
        assert len(range.filter(">=0.0.2"))==2
    
    def test_select(self):
        range = VersionRange(["0.0.1", "0.0.2", "1.0.0"])
        assert range.select("0.0.1")==Version("0.0.1")
 
    def test_in(self):
        range = VersionRange(["0.0.1", "0.0.2", "1.0.0"])
        assert "~0.0.1" in range
        assert "0.0.1" in range
        assert "0.0.8" not in range

    def test_getitem(self):
        range = VersionRange(["0.0.1", "0.0.2", "1.0.0"])
        assert range["~0.0.1"]==Version("0.0.2")
        assert range["latest"]==Version("1.0.0")
