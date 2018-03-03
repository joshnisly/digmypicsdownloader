#!/usr/bin/env python3


import configparser
import json
import requests
import os
import queue
import threading
import urllib.parse

_HOST = 'https://www.digmypics.com'


def make_request(url):
    url = _HOST + url
    print(url)
    return requests.get(url)


class DownloadThread(threading.Thread):
    def __init__(self, input_queue, order_id, output_dir):
        threading.Thread.__init__(self)
        self._queue = input_queue
        self._order_id = order_id
        self._output_dir = output_dir

    def run(self):
        while True:
            pic = self._queue.get_nowait()

            pic_dir = os.path.join(self._output_dir, pic['Folder'])
            os.makedirs(pic_dir, exist_ok=True)
            pic_path = os.path.join(pic_dir, pic['Name'].replace('.tif', '.jpg'))

            if os.path.exists(pic_path):
                continue

            pic_url = '/photos/full/%s/%s.jpg' % (self._order_id, pic['id'])
            print(pic_path)
            pic_data = make_request(pic_url).content
            with open(pic_path, 'wb') as output:
                output.write(pic_data)


def main():
    parser = configparser.ConfigParser()
    parser.read('config.ini')

    order_id = parser.get('Order', 'OrderID')
    zipcode = parser.get('Order', 'Zip')

    response = make_request('/api/api/photos/get?' + urllib.parse.urlencode({
        'oid': order_id,
        'sZip': zipcode
    })).text

    pics = json.loads(response)

    output_dir = parser.get('Environment', 'OutputDir')
    input_queue = queue.Queue()
    for pic in pics:
        input_queue.put(pic)

    for i in range(0, 10):
        thread = DownloadThread(input_queue, order_id, output_dir)
        thread.start()


if __name__ == '__main__':
    main()
