#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import os
import pprint
import urllib.request

import requests
import yaml

pp = pprint.PrettyPrinter(indent=1)

config_file = open('config.yaml', 'r')
config = yaml.load(config_file)

user_id = config["user_id"]
vk_token = config["vk_token"]
download_dir = config["download_dir"]


def main():
    album_list(user_id)


def album_list(usr_id):
    d = {"owner_id": usr_id}
    response = vk_method("photos.getAlbums", d)
    for album in response["response"]["items"]:
        print(album["title"])
        dir_name = download_dir + album["title"]
        if create_dir(dir_name):
            print(u"Создан каталог %s" % dir_name)

        album_id = album["id"]
        photo_list(album_id, dir_name)
        print()


def photo_list(album_id, dir_name):
    d = {"album_id": album_id, "owner_id": user_id}
    response = vk_method("photos.get", d)
    pp.pprint(response)
    for photo in response["response"]["items"]:
        max_res = -1
        url = ""
        for photo_res in photo["sizes"]:
            res = photo_res["width"] * photo_res["height"]
            if res > max_res:
                max_res = res
                url = photo_res["url"]

        photo_id = photo["id"]
        download_photo(url, dir_name, photo_id, photo["text"])
        print()


def create_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        return True
    else:
        return False


def download_photo(url, dir_name, photo_id, text):
    print(u"Загружаю фото %s" % url)
    photo = urllib.request.urlopen(url).read()
    album_title = dir_name.rsplit('/')[-2]
    save_name = "%s/%s_%s.jpg" % (dir_name, album_title, photo_id)
    f = open(save_name, "wb")
    f.write(photo)
    print(u"Сохранено %s" % save_name)
    if text:
        f = open("%s.txt" % save_name, "wb")
        f.write(text.encode('utf-8'))
        print(u"Сохранено описание %s.txt" % save_name)
    f.close()


def vk_method(method, d={}):
    print("Запрос к API")
    url = 'https://api.vk.com/method/%s' % method
    d.update({'access_token': vk_token})
    d.update({'v': "5.80"})
    print("URL: " + url)
    print("Payload: " + str(d) + "\n")
    response = json.loads(requests.post(url, d).content)
    if 'error' in response:
        print('VK API error: %s' % (response['error']['error_msg']))
    else:
        print("Ответ получен")
    return response


if __name__ == "__main__":
    main()
