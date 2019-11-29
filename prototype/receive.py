import flask
from flask import Flask, request, render_template, url_for
import numpy as np
import cv2 as cv
import os
from flask import Response
from werkzeug.utils import secure_filename
import threading
import socket

outputFrame=None
lock=threading.Lock()

HOST='127.0.0.1'
PORT=3000


app=Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

def recvall(sock,count):
    buf=b''
    while count:
        newbuf=sock.recv(count)
        if not newbuf: return None
        buf+=newbuf
        count-=len(newbuf)
    return buf

def recv():
    global outputFrame, lock
    client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print("a")
    client_socket.connect((HOST,PORT))
    print("b")
    while True:
        message='1'
        client_socket.send(message.encode())

        length=recvall(client_socket,16)
        stringData=recvall(client_socket,int(length))
        data=np.frombuffer(stringData,dtype='uint8')

        decimg=cv.imdecode(data,1)
       # encodeImage = cv.imencode(".jpg", decimg)
        print('c')
        with lock:
            outputFrame = decimg.copy()
       # yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(decimg) + b'\r\n')

def generate():
    global outputFrame, lock

    # loop over frames from the output stream
    while True:
    # wait until the lock is acquired
        with lock:
            if outputFrame is None:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(outputFrame) + b'\r\n')


@app.route('/video_feed')
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    print('d')
    return Response(generate(),mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
    t = threading.Thread(target=recv)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=5555, debug=True,threaded=True,use_reloader=False)
