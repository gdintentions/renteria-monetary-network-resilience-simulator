"""Real three-process localhost RPC test; no external network exposure."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from qrcn.paxos import Proposer, canonical_value, Acceptor
from qrcn.tcpnode import rpc

class Processes(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.children=[]
        self.ports={}
        self.paths={}
        for name in "abc":
            path=str(Path(self.temp.name)/(name+".sqlite"))
            self.paths[name]=path
            process=subprocess.Popen([sys.executable,"-m","qrcn.tcpnode",name,path],
                                      stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            self.children.append(process)
            port=process.stdout.readline().strip()
            if not port.isdecimal():raise RuntimeError("Node failed to start")
            self.ports[name]=int(port)
        self.reachable=set("abc")
    def tearDown(self):
        for child in self.children:child.terminate()
        for child in self.children:
            try:child.communicate(timeout=3)
            except subprocess.TimeoutExpired:child.kill();child.communicate(timeout=3)
        self.temp.cleanup()
    def call(self,name,op,slot,ballot,value):
        if name not in self.reachable:raise ConnectionError("Partition dropped RPC")
        return rpc(self.ports[name],op,slot,ballot,value)
    def test_three_processes_partition_and_restart(self):
        proposer=Proposer(tuple("abc"),self.call)
        left=canonical_value("tx-remote",100)
        right=canonical_value("tx-remote",200)
        self.reachable={"a"}
        self.assertEqual(proposer.propose("tx-remote",10,left).status,"no_prepare_quorum")
        self.reachable={"a","b"}
        self.assertEqual(proposer.propose("tx-remote",11,left).status,"chosen")
        process=self.children[1]
        process.terminate();process.communicate(timeout=3)
        new=subprocess.Popen([sys.executable,"-m","qrcn.tcpnode","b",self.paths["b"]],
                             stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.children[1]=new
        self.ports["b"]=int(new.stdout.readline().strip())
        self.reachable={"b","c"}
        outcome=proposer.propose("tx-remote",12,right)
        self.assertEqual((outcome.status,outcome.chosen_value),("adopted_prior",left))
        self.assertEqual(Acceptor("b",self.paths["b"]).inspect("tx-remote")["accepted_value"],left)

if __name__=="__main__":unittest.main()
