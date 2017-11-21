#!/usr/bin/env python3
import re,sys,socket,subprocess

if len(sys.argv)!=2:
    print("Usage: server_script.py <port number>")
    sys.exit()

HOST, PORT ='', int(sys.argv[1])

LISTEN_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LISTEN_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
LISTEN_SOCKET.bind((HOST, PORT))
LISTEN_SOCKET.listen(1)

print("Serving HTTP on port",PORT," ....")

def find_page_usingre(file):
    lst=re.findall("/([\w/]*[^1\s]*)",file)
    return lst[0]

while 1:
    CLIENT_CONNECTION, CLIENT_ADDRESS = LISTEN_SOCKET.accept()
    REQUEST = CLIENT_CONNECTION.recv(1024)
    REQUEST=REQUEST.decode('utf-8')
    print(REQUEST)
    PAGE=find_page_usingre(REQUEST)
    print("Request received from ",CLIENT_ADDRESS," for page /"+PAGE)

    if PAGE=="close_connection":
        HTTP_RESPONSE="""\
HTTP/1.1 200 OK

Server has been turned off
"""
        CLIENT_CONNECTION.sendall(bytes(HTTP_RESPONSE,'utf-8'))
        CLIENT_CONNECTION.close()
        break
    
    try:
        if PAGE=='/':
            PAGE=PAGE+'index.html'
        RESPONSE=open(PAGE,'r')
        HTTP_RESPONSE=RESPONSE.read()
        RESPONSE.close()
        HEADER="""\
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

"""
        CLIENT_CONNECTION.sendall(bytes(HEADER+HTTP_RESPONSE,'utf-8'))
    except IsADirectoryError:
        HEADER="""\
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

"""
        LIST=subprocess.run("ls "+PAGE,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        OUTPUT=str(LIST.stdout)
        OUTPUT=OUTPUT.replace('\\n','<br>')
        OUTPUT=OUTPUT.strip('b')
        OUTPUT=OUTPUT.strip('\'')
        CLIENT_CONNECTION.sendall(bytes(HEADER+OUTPUT,'utf-8'))
    except FileNotFoundError as e:
        HTTP_RESPONSE="""\
HTTP/1.1 404 NOT FOUND

Page not found: """
        CLIENT_CONNECTION.sendall(bytes(HTTP_RESPONSE+'/'+PAGE,'utf-8'))
    finally:
        CLIENT_CONNECTION.close()
