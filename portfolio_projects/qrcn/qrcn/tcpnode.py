"""Localhost-only JSON RPC. Not authenticated, encrypted, or safe for exposure.

The demonstration spawns separate OS processes, each with an independent
SQLite acceptor file; network calls are loopback and untrusted.
"""
from __future__ import annotations
import argparse
import json
import socket
import socketserver
from .paxos import Acceptor

MAX_LINE=32768

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            raw=self.rfile.readline(MAX_LINE+1)
            if not raw or len(raw)>MAX_LINE or not raw.endswith(b"\n"):
                return
            request=json.loads(raw)
            if request.get("op") == "prepare":
                answer=self.server.acceptor.prepare(request["slot"],request["ballot"])
            elif request.get("op") == "accept":
                answer=self.server.acceptor.accept(
                    request["slot"],request["ballot"],request["value"])
            else:
                raise ValueError("Unrecognized protocol operation")
            response={"reply":answer}
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
            response={"error":str(exc)}
        self.wfile.write((json.dumps(response,sort_keys=True)+"\n").encode())

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address=True
    daemon_threads=True
    def __init__(self, host_port, acceptor):
        super().__init__(host_port,Handler)
        self.acceptor=acceptor


def rpc(port: int, op: str, slot: str, ballot: int, value: str|None,
        *, timeout: float=2) -> dict:
    data=json.dumps({"op":op,"slot":slot,"ballot":ballot,"value":value},
                    separators=(",",":")).encode()+b"\n"
    if len(data)>MAX_LINE:raise ValueError("Request too large")
    with socket.create_connection(("127.0.0.1",port),timeout=timeout) as connection:
        connection.settimeout(timeout)
        connection.sendall(data)
        stream=connection.makefile("rb")
        try: line=stream.readline(MAX_LINE+1)
        finally: stream.close()
    if not line or len(line)>MAX_LINE:raise ConnectionError("Invalid/empty RPC response")
    answer=json.loads(line)
    if "error" in answer:raise ValueError(answer["error"])
    return answer["reply"]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("node")
    parser.add_argument("db")
    args=parser.parse_args()
    acceptor=Acceptor(args.node,args.db)
    with Server(("127.0.0.1",0),acceptor) as server:
        print(server.server_address[1],flush=True)
        server.serve_forever(poll_interval=0.1)

if __name__=="__main__":main()
