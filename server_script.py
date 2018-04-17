#!/usr/bin/env python3
import re,sys,socket,subprocess,os

if len(sys.argv)!=2:
    print("Usage: server_script.py <port number>")
    sys.exit()

HOST, PORT ='', int(sys.argv[1])

LISTEN_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LISTEN_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
LISTEN_SOCKET.bind((HOST, PORT))
LISTEN_SOCKET.listen(1)

print("[*]Serving HTTP on port",PORT," ....")

def make_page_from_list(fi):
    new_output=''
    for xx in fi:
        new_output=new_output+xx+'<br>'
    return new_output

def find_page_usingre(file):
    lst=re.findall("/([\w/]*[^1\s]*)",file)
    return lst[0]

#function to be used to convert directory items into hyperlinks
def designthis(x):
    x=x.strip('\\')
    a='<a href="'+x+'">'+x+'</a>'
    return a
try:
    while 1:
        CLIENT_CONNECTION, CLIENT_ADDRESS = LISTEN_SOCKET.accept()
        REQUEST = CLIENT_CONNECTION.recv(1024)
        REQUEST=REQUEST.decode('utf-8')
        PAGE=find_page_usingre(REQUEST)
        print("[*]Request received from ",CLIENT_ADDRESS[0],":",CLIENT_ADDRESS[1]," for page /"+PAGE)
        if PAGE=="close_connection":
            HTTP_RESPONSE="""\
HTTP/1.1 200 OK
Server has been turned off
"""
            CLIENT_CONNECTION.sendall(bytes(HTTP_RESPONSE,'utf-8'))
            CLIENT_CONNECTION.close()
            break
        try:
            if PAGE=='':
                RESPONSE=open('.','r')
            #print(PAGE)
            else:
                RESPONSE=open(PAGE,'r')
            if re.search('html$',PAGE):
                HTTP_RESPONSE=RESPONSE.read()
            else:
                HTTP_RESPONSE=RESPONSE.read()
                #HTTP_RESPONSE=RESPONSE.readlines()
                #HTTP_RESPONSE=make_page_from_list(HTTP_RESPONSE)
            RESPONSE.close()
            HEADER="""\
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

"""
            CLIENT_CONNECTION.sendall(bytes(HEADER+HTTP_RESPONSE,'utf-8'))
        except IsADirectoryError:
            OUTPUT=None
            HEADER="""\
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

""" 
            try:
                if PAGE=='':
                    OUTPUT=os.listdir('.')
                else:
                    OUTPUT=os.listdir(PAGE)
                #LIST=subprocess.run("ls "+PAGE,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            except:
                HEADER="""\
HTTP/1.1 503 OK
Content-Type: text/html; charset=utf-8

"""
                HTTP_RESPONSE='Directory could not be traced'
                CLIENT_CONNECTION.sendall(bytes(HEADER+HTTP_RESPONSE,'utf-8'))
            #OUTPUT=str(LIST.stdout)
            #OUTPUT=OUTPUT.strip('b')
            #lent=len(OUTPUT)
            #OUTPUT=OUTPUT[1:lent-2]
            #OUTPUT=OUTPUT.split("\\n")
            OUTPUT=list(map(designthis,OUTPUT))
            OUTPUT=make_page_from_list(OUTPUT)
            mediate="<html><head><title>Directory listing</title></head><body><h3 style='color:blue;'>Contents of directory:</h3>"
            CLIENT_CONNECTION.sendall(bytes(HEADER+mediate+OUTPUT,'utf-8'))
        except KeyboardInterrupt:
            print('\n[*]Shutting down server')
            sys.exit()
        except FileNotFoundError as e:
            HTTP_RESPONSE="""\
HTTP/1.1 404 NOT FOUND
Page not found: """
            CLIENT_CONNECTION.sendall(bytes(HTTP_RESPONSE+'/'+PAGE,'utf-8'))
        finally:
            CLIENT_CONNECTION.close()
except KeyboardInterrupt:
    print('\n[*]Shutting down server')
sys.exit()
