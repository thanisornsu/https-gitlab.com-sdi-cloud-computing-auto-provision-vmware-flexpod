# -*- coding: utf-8 -*-
import threading


def count100000():
    i = 0
    while i < 100000:
        i = i+1
        print i


def count500000():
    j = 0
    while j < 500000:
        j = j+1
        print j


def mainCount():
    count100000()
    count500000()


def startThread():
    threads = []
    t = threading.Thread(target=mainCount)
    threads.append(t)
    t.start()


mainCount()

