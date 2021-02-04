from army.api.log import log
from army.api.version import Version, VersionException
from helper import raised, run
import os
import unittest

log.setLevel('CRITICAL')


class TestVersion(unittest.TestCase):

    def test_bad_version(self):
        values = [
            "",
            "1.1.1.1",
            "1.a",
            "1-a"
        ]
        
        for value in values:
            print("version:", value)
            assert raised(Version, value)[0]==VersionException

    def test_comparisons(self):
        values = [
            #           [L<R    L<=R   L>R    L>=R   L==R ]
        #     ["1", "1",  [False, True,  False, True,  True ]],
        #     ["1", "2",  [True,  True,  False, False, False]],
        #     ["2", "1",  [False, False, True,  True,  False]],
        #     
        #     ["2.0", "2.0",  [False, True,  False, True,  True ]],
        #     ["2.0", "1.9",  [False, False, True,  True,  False]],
        #     ["1.9", "2.0",  [True,  True,  False, False, False]],
         
            ["2.0.0", "2.0.0",  [False, True,  False, True,  True ]],
            ["2.0.0", "1.9.9",  [False, False, True,  True,  False]],
            ["1.9.9", "2.0.0",  [True,  True,  False, False, False]],
         
            ["2.0.0-aa", "2.0.0-aa",  [False, True,  False, True,  True ]],
            ["2.0.0-aa", "2.0.0-ab",  [True,  True,  False, False, False]],
            ["2.0.0-ab", "2.0.0-aa",  [False, False, True,  True,  False]],
         
        #     ["1.1.1", "1",       [False, True, False,  True,  True]],
        #     ["1.1.1", "1.1",     [False, True, False,  True,  True]],
        #     ["1.1.1-rc1", "1.1", [True,  True, False, False, False]],
         
            ["1.1.1", "1.1.1-dev",       [False, False, True,  True,  False]],
            ["1.1.1-dev", "1.1.1-dev",   [False, True,  False,  True,  True]],
             
            ["2.1.2", "2.1.2",  [False, True,  False, True,  True ]],
            ["2.1.2", "2.1.1",  [False, False, True,  True,  False]],
            ["2.1.2", "2.1.3",  [True,  True,  False, False, False]],
        ]
         
        for v in values:
            vl = Version(v[0])
            vr = Version(v[1])
            asserts = v[2]
             
            print(f"{vl}<{vr}: {vl<vr}")
            assert (vl<vr)==asserts[0]
             
            print(f"{vl}<={vr}: {vl<=vr}")
            assert (vl<=vr)==asserts[1]
             
            print(f"{vl}>{vr}: {vl>vr}")
            assert (vl>vr)==asserts[2]    
             
            print(f"{vl}>={vr}: {vl>=vr}")
            assert (vl>=vr)==asserts[3]    
         
            print(f"{vl}=={vr}: {vl==vr}")
            assert (vl==vr)==asserts[4]    
         
            print("---")
#     
#         print(Version(Version("1.0.0")))
