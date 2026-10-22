from urllib.parse import urlsplit
import socket, base64, os, json, struct

class CDP:
    def __init__(self,url):
        u=urlsplit(url)
        self.sock=socket.create_connection((u.hostname,u.port),timeout=15)
        self.sock.sendall((f'GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: '+base64.b64encode(os.urandom(16)).decode()+'\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        response=b''
        while b'\r\n\r\n' not in response:response+=self.sock.recv(1)
        if not response.startswith(b'HTTP/1.1 101 '):raise RuntimeError(response.decode())
        self.id=0
        self.errors=[]
    def read(self,n):
        data=b''
        while len(data)<n:
            chunk=self.sock.recv(n-len(data))
            if not chunk:raise RuntimeError('CDP disconnected')
            data+=chunk
        return data
    def call(self,method,params=None):
        self.id+=1
        data=json.dumps({'id':self.id,'method':method,'params':params or {}}).encode()
        n=len(data)
        header=bytes([129,128+n]) if n<126 else bytes([129,254])+struct.pack('!H',n) if n<65536 else bytes([129,255])+struct.pack('!Q',n)
        mask=os.urandom(4)
        self.sock.sendall(header+mask+bytes(x^mask[i%4] for i,x in enumerate(data)))
        while True:
            first,second=self.read(2)
            size=second&127
            if size==126:size=struct.unpack('!H',self.read(2))[0]
            elif size==127:size=struct.unpack('!Q',self.read(8))[0]
            masking=self.read(4) if second&128 else None
            payload=self.read(size)
            if masking:payload=bytes(x^masking[i%4] for i,x in enumerate(payload))
            if first&15!=1:continue
            msg=json.loads(payload)
            if msg.get('method')=='Runtime.exceptionThrown':self.errors.append(msg['params'])
            if msg.get('id')==self.id:
                if 'error' in msg:raise RuntimeError(msg['error'])
                return msg.get('result',{})
    def evaluate(self,expression):
        response=self.call('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
        if 'exceptionDetails' in response:raise RuntimeError(response['exceptionDetails'])
        return response.get('result',{}).get('value')
