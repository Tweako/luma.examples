#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Showcase viewport and hotspot functionality.

Loosely based on poster_demo by @bjerrep
https://github.com/bjerrep/ssd1306/blob/master/examples/poster_demo.py

Needs psutil (+ dependencies) installed::
  $ sudo apt-get install python-dev
  $ sudo pip install psutil
"""

import psutil, socket
from hotspot.common import title_text, tiny_font

from demo_opts import get_device
from luma.core.virtual import viewport, snapshot

from hotspot import memory, uptime, cpu_load, clock, network, disk


def position(max):
    forwards = range(0, max)
    backwards = range(max, 0, -1)
    while True:
        for x in forwards:
            yield x
        for x in backwards:
            yield x


def pause_every(interval, generator):
    try:
        while True:
            x = next(generator)
            if x % interval == 0:
                for _ in range(20):
                    yield x
            else:
                yield x
    except StopIteration:
        pass


def intersect(a, b):
    return list(set(a) & set(b))


def first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default
    
def network_hostname():
    def render(draw, width, height):
        hostname = socket.gethostname()
        margin = 3
        title_text(draw, margin, width, text="Hostname")
        draw.text((margin, 20), text=hostname, font=tiny_font, fill="white")

    return render


def main():
    if device.rotate in (0, 2):
        # Horizontal
        widget_width = device.width // 2
        widget_height = device.height
    else:
        # Vertical
        widget_width = device.width
        widget_height = device.height // 2

    # Either function or subclass
    #  cpuload = hotspot(widget_width, widget_height, cpu_load.render)
    cpuload = cpu_load.CPU_Load(widget_width, widget_height, interval=1.0)
    utime = snapshot(widget_width, widget_height, uptime.render, interval=1.0)
    mem = snapshot(widget_width, widget_height, memory.render, interval=2.0)
    dsk = snapshot(widget_width, widget_height, disk.render, interval=2.0)
    # cpuload = snapshot(widget_width, widget_height, cpu_load.render, interval=0.5)
    clk = snapshot(widget_width, widget_height, clock.render, interval=1.0)

    network_ifs = psutil.net_if_stats().keys()
    # wlan = first(intersect(network_ifs, ["wlan0", "wl0"]), "wlan0")
    eth = first(intersect(network_ifs, ["eth0", "en0"]), "eth0")
    # tun = first(intersect(network_ifs, ["tun", "tun0"]), "tun0")
    # lo = first(intersect(network_ifs, ["lo", "lo0"]), "lo")

    # net_wlan = snapshot(widget_width, widget_height, network.stats(wlan), interval=2.0)
    net_eth = snapshot(widget_width, widget_height, network.stats(eth), interval=2.0)
    # net_tun = snapshot(widget_width, widget_height, network.stats(tun), interval=2.0)
    # net_lo = snapshot(widget_width, widget_height, network.stats(lo), interval=2.0)
    
    host = snapshot(widget_width, widget_height, network_hostname(), interval=2.0)

    widgets = [cpuload, utime, clk, net_eth, host, mem, dsk]

    if device.rotate in (0, 2):
        virtual = viewport(device, width=widget_width * len(widgets), height=widget_height)
        for i, widget in enumerate(widgets):
            virtual.add_hotspot(widget, (i * widget_width, 0))

        for x in pause_every(widget_width, position(widget_width * (len(widgets) - 2))):
            virtual.set_position((x, 0))

    else:
        virtual = viewport(device, width=widget_width, height=widget_height * len(widgets))
        for i, widget in enumerate(widgets):
            virtual.add_hotspot(widget, (0, i * widget_height))

        for y in pause_every(widget_height, position(widget_height * (len(widgets) - 2))):
            virtual.set_position((0, y))


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
