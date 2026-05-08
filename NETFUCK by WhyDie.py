import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import threading
import subprocess
import argparse
import csv
import time
import os
import platform
import ipaddress
import socket
import re
import random
import json
import urllib.request
import errno
import webbrowser
try:
    from scapy.all import ARP, Ether, srp, srp1, IP, TCP, ICMP
except ImportError:
    pass # Scapy не є обов'язковою, але рекомендована для агресивного режиму
try:
    import dns.resolver
    import dns.zone
    import dns.query
    import dns.reversename
except ImportError:
    pass # dnspython потрібен для перевірки AXFR
try:
    import netifaces
except ImportError:
    pass # netifaces не є обов'язковим, але покращує автовизначення мережі
from concurrent.futures import ThreadPoolExecutor
import ssl
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Any

class NetworkScannerApp:
    # УЛЬТРА-БАЗА ВЕНДОРІВ: Включає всі відомі бренди ноутбуків, ПК та виробників мережевих чіпів
    COMMON_VENDORS = {
        # Apple
        '00:0A:F7': 'Apple', '00:1E:C2': 'Apple', '00:1F:5B': 'Apple', '00:23:12': 'Apple', '00:24:36': 'Apple', '00:25:00': 'Apple', '04:0C:CE': 'Apple', '0C:3E:9F': 'Apple', '10:40:F3': 'Apple', '14:10:9F': 'Apple', '18:20:32': 'Apple', '1C:1A:DF': 'Apple', '20:38:14': 'Apple', '24:A0:74': 'Apple', '28:6A:B8': 'Apple', '2C:F0:A2': 'Apple', '30:10:E4': 'Apple', '34:15:9E': 'Apple', '38:0F:4A': 'Apple', '3C:07:54': 'Apple', '40:3C:FC': 'Apple', '44:4C:0C': 'Apple', '48:D7:05': 'Apple', '4C:32:75': 'Apple', '50:32:37': 'Apple', '54:26:96': 'Apple', '58:1F:AA': 'Apple', '5C:8D:4E': 'Apple', '60:33:4B': 'Apple', '64:20:0C': 'Apple', '68:5B:35': 'Apple', '6C:3E:6D': 'Apple', '70:11:24': 'Apple', '74:81:14': 'Apple', '78:31:C1': 'Apple', '7C:11:BE': 'Apple', '80:E6:50': 'Apple', '84:38:35': 'Apple', '88:1F:A1': 'Apple', '8C:2D:AA': 'Apple', '90:3C:92': 'Apple', '94:94:26': 'Apple', '98:03:D8': 'Apple', '9C:04:EB': 'Apple', 'A0:18:28': 'Apple', 'A4:67:06': 'Apple', 'A8:20:66': 'Apple', 'AC:3C:0B': 'Apple', 'B0:34:95': 'Apple', 'B4:18:D1': 'Apple', 'B8:17:C2': 'Apple', 'BC:3B:AF': 'Apple', 'C0:1A:DA': 'Apple', 'C4:2C:03': 'Apple', 'C8:1E:E7': 'Apple', 'CC:08:E0': 'Apple', 'D0:03:4B': 'Apple', 'D4:9A:20': 'Apple', 'D8:1D:72': 'Apple', 'DC:2B:2A': 'Apple', 'E0:B9:BA': 'Apple', 'E4:25:E7': 'Apple', 'E8:04:0B': 'Apple', 'EC:35:86': 'Apple', 'F0:24:75': 'Apple', 'F4:1B:A1': 'Apple', 'F8:1E:DF': 'Apple', 'FC:25:3F': 'Apple',
        # Samsung
        '00:02:78': 'Samsung', 'F6:C8:BA': 'Samsung', '00:09:18': 'Samsung', '04:18:0F': 'Samsung', '08:08:C2': 'Samsung', '0C:14:20': 'Samsung', '10:1D:C0': 'Samsung', '14:32:D1': 'Samsung', '18:22:7E': 'Samsung', '1C:5A:3E': 'Samsung', '20:13:E0': 'Samsung', '24:46:C8': 'Samsung', '28:27:BF': 'Samsung', '2C:44:01': 'Samsung', '30:19:66': 'Samsung', '34:23:BA': 'Samsung', '38:01:95': 'Samsung', '3C:8B:FE': 'Samsung', '40:0E:85': 'Samsung', '44:4E:1A': 'Samsung', '48:44:F7': 'Samsung', '4C:3B:74': 'Samsung', '50:85:69': 'Samsung', '54:88:0E': 'Samsung', '58:90:43': 'Samsung', '5C:0A:5B': 'Samsung', '60:6B:BD': 'Samsung', '64:1C:B0': 'Samsung', '68:EB:AE': 'Samsung', '6C:83:36': 'Samsung', '70:2A:D5': 'Samsung', '74:45:CE': 'Samsung', '78:46:C4': 'Samsung', '7C:38:66': 'Samsung', '80:4E:81': 'Samsung', '84:25:DB': 'Samsung', '88:32:9B': 'Samsung', '8C:71:F8': 'Samsung', '90:18:7C': 'Samsung', '94:35:0A': 'Samsung', '98:0C:82': 'Samsung', '9C:3A:AF': 'Samsung', 'A0:0B:BA': 'Samsung', 'A4:9A:58': 'Samsung', 'A8:06:00': 'Samsung', 'AC:5F:3E': 'Samsung', 'B0:1B:D2': 'Samsung', 'B4:07:F9': 'Samsung', 'B8:C6:8E': 'Samsung', 'BC:20:A4': 'Samsung', 'C0:8B:6F': 'Samsung', 'C4:42:02': 'Samsung', 'C8:14:79': 'Samsung', 'CC:05:1B': 'Samsung', 'D0:17:6A': 'Samsung', 'D4:87:D8': 'Samsung', 'D8:31:CF': 'Samsung', 'DC:0B:34': 'Samsung', 'E0:99:71': 'Samsung', 'E4:12:1D': 'Samsung', 'E8:11:32': 'Samsung', 'EC:10:7B': 'Samsung', 'F0:08:F1': 'Samsung', 'F4:09:D8': 'Samsung', 'F8:04:2E': 'Samsung', 'FC:A1:3E': 'Samsung',
        # Xiaomi
        '00:9E:C8': 'Xiaomi', '04:E6:76': 'Xiaomi', '08:1F:71': 'Xiaomi', '0C:1D:AF': 'Xiaomi', '10:2A:B3': 'Xiaomi', '14:38:A6': 'Xiaomi', '18:59:36': 'Xiaomi', '20:82:C0': 'Xiaomi', '28:6C:07': 'Xiaomi', '34:80:B3': 'Xiaomi', '38:A4:ED': 'Xiaomi', '3C:8D:20': 'Xiaomi', '40:31:3C': 'Xiaomi', '4C:49:E3': 'Xiaomi', '50:64:2B': 'Xiaomi', '54:36:9B': 'Xiaomi', '58:44:98': 'Xiaomi', '5C:C5:D4': 'Xiaomi', '60:A4:4C': 'Xiaomi', '64:09:80': 'Xiaomi', '68:DF:DD': 'Xiaomi', '74:23:44': 'Xiaomi', '78:11:DC': 'Xiaomi', '7C:1D:D9': 'Xiaomi', '80:5A:04': 'Xiaomi', '8C:BE:BE': 'Xiaomi', '90:0E:B3': 'Xiaomi', '94:87:E0': 'Xiaomi', '98:FA:E3': 'Xiaomi', '9C:99:A0': 'Xiaomi', 'A4:50:46': 'Xiaomi', 'AC:C1:EE': 'Xiaomi', 'B0:E2:35': 'Xiaomi', 'B4:36:E3': 'Xiaomi', 'C4:0B:CB': 'Xiaomi', 'CC:08:FB': 'Xiaomi', 'D0:51:62': 'Xiaomi', 'D4:97:0B': 'Xiaomi', 'E0:76:D0': 'Xiaomi', 'E4:46:DA': 'Xiaomi', 'F0:B4:29': 'Xiaomi', 'F4:8B:32': 'Xiaomi', 'F8:A4:5F': 'Xiaomi', 'FC:64:BA': 'Xiaomi',
        # Huawei
        '00:18:82': 'Huawei', '04:F1:3E': 'Huawei', '08:19:A6': 'Huawei', '0C:37:DC': 'Huawei', '10:47:80': 'Huawei', '14:A0:F8': 'Huawei', '18:C5:8A': 'Huawei', '20:F3:A3': 'Huawei', '24:09:95': 'Huawei', '28:31:52': 'Huawei', '2C:55:D3': 'Huawei', '30:F7:D7': 'Huawei', '34:00:A3': 'Huawei', '38:F8:89': 'Huawei', '3C:F8:08': 'Huawei', '40:4D:8E': 'Huawei', '44:55:B1': 'Huawei', '48:46:FB': 'Huawei', '4C:1F:CC': 'Huawei', '50:A7:2B': 'Huawei', '54:39:DF': 'Huawei', '58:7F:66': 'Huawei', '5C:4C:A9': 'Huawei', '60:DE:F3': 'Huawei', '64:16:F0': 'Huawei', '68:89:C1': 'Huawei', '6C:5E:7A': 'Huawei', '70:7B:E8': 'Huawei', '74:88:2A': 'Huawei', '78:1D:BA': 'Huawei', '7C:A2:3E': 'Huawei', '80:7A:BF': 'Huawei', '84:A8:E4': 'Huawei', '88:53:D4': 'Huawei', '8C:34:FD': 'Huawei', '90:4E:91': 'Huawei', '94:77:2B': 'Huawei', '98:FF:D0': 'Huawei', '9C:28:BF': 'Huawei', 'A0:8C:FD': 'Huawei', 'A4:CA:A0': 'Huawei', 'A8:0C:63': 'Huawei', 'AC:E3:42': 'Huawei', 'B0:5B:67': 'Huawei', 'B4:15:13': 'Huawei', 'B8:3A:5A': 'Huawei', 'BC:76:5E': 'Huawei', 'C0:70:09': 'Huawei', 'C4:07:2F': 'Huawei', 'C8:8D:83': 'Huawei', 'CC:53:B5': 'Huawei', 'D0:2D:B3': 'Huawei', 'D4:40:F0': 'Huawei', 'D8:49:2F': 'Huawei', 'DC:D2:FC': 'Huawei', 'E0:19:54': 'Huawei', 'E4:68:A3': 'Huawei', 'E8:CD:2D': 'Huawei', 'EC:CB:30': 'Huawei', 'F0:C8:50': 'Huawei', 'F4:55:95': 'Huawei', 'F8:4A:73': 'Huawei', 'FC:E3:3C': 'Huawei',
        # BBK (Oppo / Vivo / Realme / OnePlus)
        '14:3F:A6': 'Oppo/Vivo/Realme', '28:A1:83': 'Oppo/Vivo/Realme', '3C:DC:BC': 'Oppo/Vivo/Realme', '48:D0:2D': 'Oppo/Vivo/Realme', '54:8B:C9': 'Oppo/Vivo/Realme', '5C:E2:8C': 'Oppo/Vivo/Realme', '60:8F:5C': 'Oppo/Vivo/Realme', '68:3E:34': 'Oppo/Vivo/Realme', '70:8A:09': 'Oppo/Vivo/Realme', '78:3A:84': 'Oppo/Vivo/Realme', '80:7C:F4': 'Oppo/Vivo/Realme', '8C:15:C8': 'Oppo/Vivo/Realme', '94:0E:6B': 'Oppo/Vivo/Realme', 'A0:91:69': 'Oppo/Vivo/Realme', 'A8:16:D0': 'Oppo/Vivo/Realme', 'B4:1C:30': 'Oppo/Vivo/Realme', 'C0:15:B2': 'Oppo/Vivo/Realme', 'C8:F8:76': 'Oppo/Vivo/Realme', 'CC:66:FA': 'Oppo/Vivo/Realme', 'D0:B3:3F': 'Oppo/Vivo/Realme', 'D4:B1:10': 'Oppo/Vivo/Realme', 'E0:B5:2F': 'Oppo/Vivo/Realme', 'E4:0E:EE': 'Oppo/Vivo/Realme', 'F4:8E:92': 'Oppo/Vivo/Realme',
        # LeEco / LeMobile
        '14:B5:CD': 'LeEco/LeMobile', 'C8:08:E9': 'LeEco/LeMobile',
        # Motorola / Lenovo
        '00:23:76': 'Motorola', '14:1A:A3': 'Motorola', '20:3A:07': 'Motorola', '48:83:C7': 'Motorola', '5C:51:88': 'Motorola', '60:29:A4': 'Motorola', '78:CA:39': 'Motorola', '80:6C:1B': 'Motorola', '84:D6:D0': 'Motorola', '90:B6:86': 'Motorola', '9C:D9:17': 'Motorola', 'A4:70:D6': 'Motorola', 'A8:96:75': 'Motorola', 'B4:C2:87': 'Motorola', 'C8:E0:EB': 'Motorola', 'CC:C3:EA': 'Motorola', 'D4:22:3F': 'Motorola', 'E0:89:7E': 'Motorola', 'E4:9A:DC': 'Motorola', 'F8:E0:79': 'Motorola',
        '00:1E:EC': 'Lenovo', '04:7A:0B': 'Lenovo', '08:8F:C3': 'Lenovo', '10:98:36': 'Lenovo', '20:76:93': 'Lenovo', '24:FD:52': 'Lenovo', '38:B1:DB': 'Lenovo', '44:37:E6': 'Lenovo', '50:7B:9D': 'Lenovo', '54:EE:75': 'Lenovo', '6C:5C:14': 'Lenovo', '74:1A:DF': 'Lenovo', '88:70:8C': 'Lenovo', '98:FA:9B': 'Lenovo', 'A4:8C:DB': 'Lenovo', 'B0:10:41': 'Lenovo', 'C8:5B:76': 'Lenovo', 'D4:3D:7E': 'Lenovo', 'E8:2A:44': 'Lenovo', 'F0:1D:BC': 'Lenovo', 'F8:A2:D6': 'Lenovo',
        # LG / Sony / Microsoft
        '00:1C:62': 'LG Electronics', '00:1E:B2': 'LG Electronics', '00:26:E2': 'LG Electronics', '0C:A6:94': 'LG Electronics', '10:F9:6F': 'LG Electronics', '14:00:29': 'LG Electronics', '1C:5C:F2': 'LG Electronics', '20:59:A0': 'LG Electronics', '24:4B:81': 'LG Electronics', '2C:54:2D': 'LG Electronics', '34:FC:EF': 'LG Electronics', '3C:BD:3E': 'LG Electronics', '40:B0:FA': 'LG Electronics', '48:59:29': 'LG Electronics', '4C:80:93': 'LG Electronics', '58:A2:B5': 'LG Electronics', '60:12:3C': 'LG Electronics', '64:89:F1': 'LG Electronics', '6C:D6:8A': 'LG Electronics', '70:A5:28': 'LG Electronics', '78:F8:82': 'LG Electronics', '88:C9:D0': 'LG Electronics', '98:D6:F7': 'LG Electronics', 'C0:41:A6': 'LG Electronics', 'C4:43:8F': 'LG Electronics', 'CC:2D:B7': 'LG Electronics', 'D8:C4:6A': 'LG Electronics', 'E8:5B:5B': 'LG Electronics', 'F8:0C:F3': 'LG Electronics',
        '00:01:4A': 'Sony', '00:13:A9': 'Sony', '00:19:C5': 'Sony', '00:24:BE': 'Sony', '10:4F:A8': 'Sony', '18:C8:E7': 'Sony', '28:0D:FC': 'Sony', '30:39:26': 'Sony', '3C:07:71': 'Sony', '54:42:49': 'Sony', '58:38:79': 'Sony', '64:D4:BD': 'Sony', '70:9E:29': 'Sony', '7C:E9:D3': 'Sony', '84:8E:DF': 'Sony', '90:C1:15': 'Sony', '94:CE:2C': 'Sony', 'A0:E4:53': 'Sony', 'AC:9B:0A': 'Sony', 'B4:52:7D': 'Sony', 'C8:F7:33': 'Sony', 'D4:4B:5E': 'Sony', 'E0:AE:5E': 'Sony', 'F8:D0:BD': 'Sony',
        '00:03:FF': 'Microsoft', '00:12:5A': 'Microsoft', '00:15:5D': 'Microsoft', '00:1D:D8': 'Microsoft', '00:22:48': 'Microsoft', '00:25:AE': 'Microsoft', '00:50:F2': 'Microsoft', '10:C3:7B': 'Microsoft', '28:18:78': 'Microsoft', '30:59:B7': 'Microsoft', '4C:0B:BE': 'Microsoft', '58:82:A8': 'Microsoft', '60:45:BD': 'Microsoft', '7C:1E:52': 'Microsoft', '98:5F:D3': 'Microsoft', 'B4:AE:2B': 'Microsoft', 'C8:3A:35': 'Microsoft', 'D8:D3:85': 'Microsoft', 'E4:A4:71': 'Microsoft',
        # Amazon (Echo, Fire TV, Kindle) / Consoles / Media
        '00:FC:8B': 'Amazon', '0C:47:C9': 'Amazon', '18:74:2E': 'Amazon', '34:D2:70': 'Amazon', '38:F7:3D': 'Amazon', '40:B4:CD': 'Amazon', '44:65:0D': 'Amazon', '50:F5:20': 'Amazon', '68:37:E9': 'Amazon', '68:54:FD': 'Amazon', '74:75:48': 'Amazon', '88:71:E5': 'Amazon', 'A0:02:DC': 'Amazon', 'AC:63:BE': 'Amazon', 'B4:7C:9C': 'Amazon', 'C0:56:27': 'Amazon', 'F0:27:2D': 'Amazon', 'F0:D2:F1': 'Amazon', 'FC:A1:83': 'Amazon',
        '00:09:BF': 'Nintendo', '00:17:AB': 'Nintendo', '00:19:1D': 'Nintendo', '00:1B:7A': 'Nintendo', '00:1C:BE': 'Nintendo', '00:1E:35': 'Nintendo', '00:21:47': 'Nintendo', '00:22:4C': 'Nintendo', '00:23:CC': 'Nintendo', '00:24:1E': 'Nintendo', '00:25:A0': 'Nintendo', '00:26:59': 'Nintendo', '04:03:D6': 'Nintendo', '18:2A:7B': 'Nintendo', '2C:10:C1': 'Nintendo', '34:AF:2C': 'Nintendo', '40:D2:8A': 'Nintendo', '48:E5:C9': 'Nintendo', '58:2F:40': 'Nintendo', '60:03:08': 'Nintendo', '70:F5:A4': 'Nintendo', '7C:BB:8A': 'Nintendo', '8C:56:C5': 'Nintendo', '94:58:CB': 'Nintendo', '98:B6:E9': 'Nintendo', 'A4:38:CC': 'Nintendo', 'A4:C0:E1': 'Nintendo', 'B8:AE:6E': 'Nintendo', 'CC:FB:65': 'Nintendo', 'D8:6B:F7': 'Nintendo', 'E0:0C:7F': 'Nintendo', 'E0:E7:51': 'Nintendo', 'E8:4E:CE': 'Nintendo', 'F4:BD:9E': 'Nintendo', 'F8:3A:4F': 'Nintendo',
        '00:0E:58': 'Sonos', '34:DF:2A': 'Sonos', '48:A6:B8': 'Sonos', '5C:AA:FD': 'Sonos', '78:28:CA': 'Sonos', '94:9F:3E': 'Sonos', 'B8:E9:37': 'Sonos', 'D8:8B:4C': 'Sonos', 'E0:E0:21': 'Sonos',
        
        # ПК, НОУТБУКИ ТА МАТЕРИНСЬКІ ПЛАТИ (Dell, HP, Lenovo, Acer, Asus, MSI, Toshiba, Gigabyte, ASRock)
        '00:02:2D': 'Supermicro', '00:0E:39': 'Supermicro', '00:25:90': 'Supermicro', '00:30:48': 'Supermicro', '0C:C4:7A': 'Supermicro', '74:E1:B6': 'Supermicro', 'AC:1F:6B': 'Supermicro',
        '00:14:22': 'Dell', '00:1A:A0': 'Dell', '00:21:70': 'Dell', '00:22:19': 'Dell', '00:23:AE': 'Dell', '00:24:E8': 'Dell', '00:25:64': 'Dell', '00:26:B9': 'Dell', '00:B0:D0': 'Dell', '14:FE:B5': 'Dell', '18:FB:7B': 'Dell', '34:17:EB': 'Dell', '54:BF:64': 'Dell', '5C:26:0A': 'Dell', '74:86:7A': 'Dell', '84:2B:2B': 'Dell', '84:8F:69': 'Dell', '90:B1:1C': 'Dell', 'B8:CA:3A': 'Dell', 'C8:1F:66': 'Dell', 'D4:BE:D9': 'Dell', 'EC:F4:BB': 'Dell', 'F4:8E:38': 'Dell', 'F8:B1:56': 'Dell', 'F8:DB:88': 'Dell', '00:80:43': 'Dell', '00:C0:4F': 'Dell',
        '00:0E:7F': 'HP', '00:11:0A': 'HP', '00:13:21': 'HP', '00:14:38': 'HP', '00:15:60': 'HP', '00:16:35': 'HP', '00:17:08': 'HP', '00:18:FE': 'HP', '00:19:BB': 'HP', '00:1A:4B': 'HP', '00:1B:78': 'HP', '00:1C:C4': 'HP', '00:1E:0B': 'HP', '00:1F:29': 'HP', '00:21:5A': 'HP', '00:22:64': 'HP', '00:23:7D': 'HP', '00:24:81': 'HP', '00:25:B3': 'HP', '00:26:55': 'HP', '08:D4:0C': 'HP', '10:E7:C6': 'HP', '14:B3:1F': 'HP', '28:92:4A': 'HP', '3C:D9:2B': 'HP', '5C:B9:01': 'HP', '70:5A:0F': 'HP', '80:C1:6E': 'HP', '94:E1:AC': 'HP', 'A0:1D:48': 'HP', 'B4:99:BA': 'HP', 'CC:48:3A': 'HP', 'D4:81:D7': 'HP', '00:10:83': 'HP', '00:30:C1': 'HP', '00:60:B0': 'HP', '00:A0:C9': 'HP',
        '00:10:60': 'Acer', '00:A0:60': 'Acer', '1C:6F:65': 'Acer', '60:23:CE': 'Acer', '88:01:8D': 'Acer', 'B0:08:BF': 'Acer', 'F0:7B:CB': 'Acer', '00:00:E2': 'Acer',
        '00:0C:76': 'MSI', '00:16:17': 'MSI', '00:19:DB': 'MSI', '00:1D:92': 'MSI', '00:21:85': 'MSI', '00:23:5A': 'MSI', '00:24:21': 'MSI', '00:26:22': 'MSI', '44:8A:5B': 'MSI', '4C:CC:6A': 'MSI', '8C:89:A5': 'MSI', 'D8:CB:8A': 'MSI',
        '00:00:39': 'Toshiba', '00:08:0D': 'Toshiba', '00:15:B7': 'Toshiba', '00:1C:7E': 'Toshiba', '00:23:18': 'Toshiba', '08:00:46': 'Toshiba', '1C:7A:B3': 'Toshiba', '8C:A9:82': 'Toshiba', 'E8:E0:B7': 'Toshiba', '00:A0:F8': 'Toshiba',
        '00:14:FD': 'GigaByte', '00:1A:4D': 'GigaByte', '00:1D:7D': 'GigaByte', '00:24:1D': 'GigaByte', '1C:4B:D6': 'GigaByte', '50:E5:49': 'GigaByte', '90:2B:34': 'GigaByte', 'E0:D5:5E': 'GigaByte', 'FC:AA:14': 'GigaByte',
        '00:19:66': 'ASRock', '00:25:22': 'ASRock', 'BC:5F:F4': 'ASRock', 'D0:50:99': 'ASRock',

        # IoT / Smart Home (Espressif / Tuya)
        '18:B9:05': 'Google (Nest)', '64:16:77': 'Google (Nest)', 'D8:EB:97': 'Google (Nest)', 'E4:F0:42': 'Google (Nest)', '00:1A:11': 'Google', '3C:5A:B4': 'Google', 'F8:0F:F9': 'Google', 'F8:8F:CA': 'Google',
        '00:17:88': 'Philips (Hue)', 'B4:E8:42': 'Philips (Hue)', 'D0:52:A8': 'Philips (Hue)', 'EC:B5:FA': 'Philips (Hue)',
        '18:FE:34': 'Espressif (IoT/Smart Home)', '24:0A:C4': 'Espressif (IoT/Smart Home)', '24:B2:DE': 'Espressif (IoT/Smart Home)', '2C:3A:E8': 'Espressif (IoT/Smart Home)', '30:AE:A4': 'Espressif (IoT/Smart Home)', '34:94:54': 'Espressif (IoT/Smart Home)', '3C:71:BF': 'Espressif (IoT/Smart Home)', '40:22:D8': 'Espressif (IoT/Smart Home)', '44:17:93': 'Espressif (IoT/Smart Home)', '48:3F:DA': 'Espressif (IoT/Smart Home)', '4C:11:AE': 'Espressif (IoT/Smart Home)', '50:02:91': 'Espressif (IoT/Smart Home)', '54:5A:A6': 'Espressif (IoT/Smart Home)', '58:BF:25': 'Espressif (IoT/Smart Home)', '5C:CF:7F': 'Espressif (IoT/Smart Home)', '60:01:94': 'Espressif (IoT/Smart Home)', '68:C6:3A': 'Espressif (IoT/Smart Home)', '80:7D:3A': 'Espressif (IoT/Smart Home)', '84:0D:8E': 'Espressif (IoT/Smart Home)', '84:CC:A8': 'Espressif (IoT/Smart Home)', '84:F3:EB': 'Espressif (IoT/Smart Home)', '90:97:D5': 'Espressif (IoT/Smart Home)', '94:B9:7E': 'Espressif (IoT/Smart Home)', '98:CD:AC': 'Espressif (IoT/Smart Home)', 'A0:20:A6': 'Espressif (IoT/Smart Home)', 'A4:7B:9D': 'Espressif (IoT/Smart Home)', 'A4:CF:12': 'Espressif (IoT/Smart Home)', 'AC:67:B2': 'Espressif (IoT/Smart Home)', 'B4:E6:2D': 'Espressif (IoT/Smart Home)', 'BC:DD:C2': 'Espressif (IoT/Smart Home)', 'C4:4F:33': 'Espressif (IoT/Smart Home)', 'C8:2B:96': 'Espressif (IoT/Smart Home)', 'CC:50:E3': 'Espressif (IoT/Smart Home)', 'D4:D4:DA': 'Espressif (IoT/Smart Home)', 'D8:A0:1D': 'Espressif (IoT/Smart Home)', 'DC:4F:22': 'Espressif (IoT/Smart Home)', 'E0:5A:1B': 'Espressif (IoT/Smart Home)', 'E8:DB:84': 'Espressif (IoT/Smart Home)', 'EC:FA:BC': 'Espressif (IoT/Smart Home)', 'F0:08:D1': 'Espressif (IoT/Smart Home)', 'FC:F5:C4': 'Espressif (IoT/Smart Home)',
        
        # Router / Switch Brands
        '00:09:0F': 'Fortinet', '08:5B:0E': 'Fortinet', '1A:3F:58': 'Fortinet', '90:67:18': 'Fortinet', 'EC:44:76': 'Fortinet',
        '00:1B:17': 'Palo Alto Networks', '08:30:6B': 'Palo Alto Networks', '54:8D:5A': 'Palo Alto Networks',
        '00:0A:EB': 'TP-Link', '14:CC:20': 'TP-Link', '60:E3:27': 'TP-Link', 'A0:F3:C1': 'TP-Link', 'E8:94:F6': 'TP-Link', 'C0:C9:E3': 'TP-Link', 'F4:F2:6D': 'TP-Link', '50:C7:BF': 'TP-Link (Tapo/Kasa)', 'B0:95:8E': 'TP-Link (Tapo/Kasa)', 'C0:06:C3': 'TP-Link (Tapo/Kasa)',
        '00:09:5B': 'Netgear', 'C0:FF:D4': 'Netgear', '08:02:8E': 'Netgear', '28:C6:8E': 'Netgear', '44:94:FC': 'Netgear', 'A0:04:60': 'Netgear',
        '74:24:9F': 'SpaceX Starlink', '20:10:7A': 'SpaceX Starlink', 'E0:A3:AC': 'SpaceX Starlink',
        'C8:3A:35': 'Tenda', '04:95:E6': 'Tenda', '50:2B:73': 'Tenda', 'CC:2D:83': 'Tenda', '00:B0:4C': 'Tenda', '04:33:C2': 'Tenda',
        '50:FF:20': 'Keenetic', '4C:1B:86': 'Keenetic', '04:BF:6D': 'Keenetic', 'E8:37:7A': 'Keenetic',
        '40:A5:EF': 'Mercusys', '00:EB:D8': 'Mercusys', '34:0A:33': 'Mercusys',
        'A0:8C:FD': 'ZTE', 'E4:71:85': 'ZTE', '34:4B:50': 'ZTE', 'C8:64:C7': 'ZTE', 'D4:37:D7': 'ZTE', 'E4:A7:C5': 'ZTE', '08:47:8E': 'ZTE', 'E4:CA:12': 'ZTE', 'F8:DF:A8': 'ZTE', 'CC:7B:35': 'ZTE', '8C:E0:81': 'ZTE',
        '18:28:61': 'AirTies', '88:41:FC': 'AirTies',
        '00:05:5D': 'D-Link', '00:0F:3D': 'D-Link', '00:11:95': 'D-Link', '00:13:46': 'D-Link', '00:15:E9': 'D-Link', '00:17:9A': 'D-Link', '00:19:5B': 'D-Link', '00:1B:11': 'D-Link', '00:1C:F0': 'D-Link', '00:1E:58': 'D-Link', '00:21:91': 'D-Link', '00:22:B0': 'D-Link', '00:24:01': 'D-Link', '00:26:5A': 'D-Link', '14:D6:4D': 'D-Link', '1C:AF:F7': 'D-Link', '28:10:7B': 'D-Link', '34:08:04': 'D-Link', '5C:D9:98': 'D-Link', '78:54:2E': 'D-Link', '84:C9:B2': 'D-Link', '90:94:E4': 'D-Link', 'A0:CC:2B': 'D-Link', 'B0:C5:54': 'D-Link', 'B8:A3:86': 'D-Link', 'C4:A8:1D': 'D-Link', 'CC:B2:55': 'D-Link', 'D8:FE:E3': 'D-Link', 'E0:46:9A': 'D-Link', 'F0:7D:68': 'D-Link', 'FC:75:16': 'D-Link',
        '00:0C:6E': 'Asus', '00:11:2F': 'Asus', '00:13:D4': 'Asus', '00:15:F2': 'Asus', '00:17:31': 'Asus', '00:18:F3': 'Asus', '00:1A:92': 'Asus', '00:1B:FC': 'Asus', '00:1D:60': 'Asus', '00:1E:8C': 'Asus', '00:1F:C6': 'Asus', '00:22:15': 'Asus', '00:23:54': 'Asus', '00:24:8C': 'Asus', '00:26:18': 'Asus', '04:92:26': 'Asus', '08:60:6E': 'Asus', '10:BF:48': 'Asus', '14:DA:E9': 'Asus', '1C:B7:2C': 'Asus', '2C:56:DC': 'Asus', '30:85:A9': 'Asus', '38:D5:47': 'Asus', '40:16:7E': 'Asus', '50:46:5D': 'Asus', '54:A0:50': 'Asus', '70:8B:CD': 'Asus', '74:D0:2B': 'Asus', '88:D7:F6': 'Asus', 'A8:5E:45': 'Asus', 'BC:EE:7B': 'Asus', 'C8:60:00': 'Asus', 'D8:50:E6': 'Asus', 'E0:3F:49': 'Asus', 'F4:6D:04': 'Asus', 'F8:32:E4': 'Asus', '04:42:1A': 'Asus', '08:62:66': 'Asus', '10:7C:61': 'Asus', '30:5A:3A': 'Asus', '50:E0:85': 'Asus', '54:04:A6': 'Asus', '90:E6:BA': 'Asus', 'AC:22:0B': 'Asus',
        '00:06:25': 'Linksys', '00:0C:41': 'Linksys', '00:0F:66': 'Linksys', '00:12:17': 'Linksys', '00:13:10': 'Linksys', '00:14:BF': 'Linksys', '00:16:B6': 'Linksys', '00:18:39': 'Linksys', '00:1A:70': 'Linksys', '00:1C:10': 'Linksys', '00:1D:7E': 'Linksys', '00:1E:E3': 'Linksys', '00:21:29': 'Linksys', '00:22:6B': 'Linksys', '00:23:69': 'Linksys', '14:91:82': 'Linksys', '20:AA:4B': 'Linksys', '30:23:03': 'Linksys', '44:5C:E9': 'Linksys', '50:39:55': 'Linksys', '58:6D:8F': 'Linksys', '60:38:E0': 'Linksys', '68:B6:FC': 'Linksys', '94:10:3E': 'Linksys', 'B0:0C:D1': 'Linksys', 'C8:D7:19': 'Linksys', 'D4:EC:59': 'Linksys', 'E0:1C:41': 'Linksys', 'E4:06:CE': 'Linksys', 'F4:B7:E2': 'Linksys',
        '00:02:CF': 'Zyxel', '00:13:49': 'Zyxel', '00:19:CB': 'Zyxel', '00:1F:33': 'Zyxel', '00:23:F8': 'Zyxel', '00:A0:C5': 'Zyxel', '10:7B:EF': 'Zyxel', '30:1A:7B': 'Zyxel', '34:1E:6B': 'Zyxel', '40:5A:9B': 'Zyxel', '4C:9E:FF': 'Zyxel', '50:67:F0': 'Zyxel', '5C:F4:AB': 'Zyxel', '8C:59:73': 'Zyxel', 'A0:E4:CB': 'Zyxel', 'C8:7B:5B': 'Zyxel', 'CC:5D:4E': 'Zyxel', 'E8:7F:6B': 'Zyxel', 'F8:F0:82': 'Zyxel',
        
        # МЕРЕЖЕВІ АДАПТЕРИ У НОУТБУКАХ (Intel, Realtek, Qualcomm Atheros, Broadcom)
        '00:E0:4C': 'Realtek', '52:54:00': 'Realtek/QEMU', '00:1A:E0': 'Realtek', '00:0B:CD': 'Realtek', '00:14:D1': 'Realtek', '00:08:18': 'Realtek', '00:10:A0': 'Realtek', '00:14:85': 'Realtek', '00:18:E7': 'Realtek', '00:1C:F2': 'Realtek', '00:1E:68': 'Realtek', '00:23:81': 'Realtek', '00:24:1D': 'Realtek', '00:80:C8': 'Realtek', '5C:F9:DD': 'Realtek', '70:85:C2': 'Realtek', '80:3F:5D': 'Realtek', '90:FB:A6': 'Realtek', 'B0:4E:26': 'Realtek', 'D0:DF:9A': 'Realtek', 'E8:03:9A': 'Realtek', 'FC:AA:14': 'Realtek',
        '00:02:B3': 'Intel', '00:03:47': 'Intel', '00:04:23': 'Intel', '00:0C:F1': 'Intel', '00:0E:0C': 'Intel', '00:11:11': 'Intel', '00:12:F0': 'Intel', '00:13:CE': 'Intel', '00:15:00': 'Intel', '00:16:EA': 'Intel', '00:18:DE': 'Intel', '00:19:D1': 'Intel', '00:1B:21': 'Intel', '00:1C:C0': 'Intel', '00:1E:65': 'Intel', '00:1F:3B': 'Intel', '00:21:5C': 'Intel', '00:22:FB': 'Intel', '00:24:D7': 'Intel', '00:26:C6': 'Intel', '00:27:0E': 'Intel', '00:28:F8': 'Intel', '08:11:96': 'Intel', '0C:8B:FD': 'Intel', '10:1F:74': 'Intel', '14:4F:8A': 'Intel', '20:16:D8': 'Intel', '24:77:03': 'Intel', '34:02:86': 'Intel', '34:13:E8': 'Intel', '34:41:5D': 'Intel', '3C:A9:F4': 'Intel', '48:4D:7E': 'Intel', '58:94:6B': 'Intel', '60:F8:1D': 'Intel', '68:05:CA': 'Intel', '74:E5:0B': 'Intel', '80:86:F2': 'Intel', '88:88:C6': 'Intel', '90:A4:DE': 'Intel', '9C:B6:D0': 'Intel', 'A0:88:B4': 'Intel', 'A0:C9:A0': 'Intel', 'A4:02:B9': 'Intel', 'A4:C9:E3': 'Intel', 'A8:A7:95': 'Intel', 'AC:45:EF': 'Intel', 'B4:D5:BD': 'Intel', 'B8:8A:60': 'Intel', 'C0:3F:D5': 'Intel', 'C4:85:08': 'Intel', 'CC:3D:82': 'Intel', 'CC:D9:4F': 'Intel', 'D4:3B:04': 'Intel', 'DC:53:60': 'Intel', 'E0:D4:64': 'Intel', 'E4:F8:9C': 'Intel', 'F4:C8:8A': 'Intel', 'F8:16:54': 'Intel', 'F8:94:C2': 'Intel', 'FC:F8:AE': 'Intel',
        '00:03:7F': 'Qualcomm Atheros', '00:13:74': 'Qualcomm Atheros', '00:1C:F0': 'Qualcomm Atheros', '00:21:1A': 'Qualcomm Atheros', '00:22:A7': 'Qualcomm Atheros', '00:23:CD': 'Qualcomm Atheros', '00:24:D2': 'Qualcomm Atheros', '00:25:DB': 'Qualcomm Atheros', '00:26:5E': 'Qualcomm Atheros', '48:5D:60': 'Qualcomm Atheros', '58:C2:32': 'Qualcomm Atheros', '78:E4:00': 'Qualcomm Atheros', '90:F6:52': 'Qualcomm Atheros', 'E0:06:E6': 'Qualcomm Atheros',
        '00:10:18': 'Broadcom', 'B8:27:EB': 'Raspberry Pi', 'DC:A6:32': 'Raspberry Pi', 'E4:5F:01': 'Raspberry Pi',

        # Enterprise Networking (Cisco, Juniper, HPE/Aruba, Arista)
        '00:00:0C': 'Cisco', '00:01:42': 'Cisco', '00:05:00': 'Cisco', '00:08:E3': 'Cisco', '00:12:43': 'Cisco', '00:17:94': 'Cisco', '00:19:AA': 'Cisco', '00:24:C4': 'Cisco', '50:3D:E5': 'Cisco', '64:A0:E7': 'Cisco', '70:CA:9B': 'Cisco', '84:78:AC': 'Cisco', 'C8:4C:75': 'Cisco', 'F8:72:EA': 'Cisco',
        '00:05:85': 'Juniper', '00:10:DB': 'Juniper', '00:26:88': 'Juniper', '08:81:F4': 'Juniper', '28:C0:DA': 'Juniper', '2C:6B:F5': 'Juniper', '3C:8C:F8': 'Juniper', '40:B4:F0': 'Juniper', '50:C5:8D': 'Juniper', '54:E0:32': 'Juniper', 'A8:D0:E5': 'Juniper',
        '00:08:5A': 'HPE/Aruba', '00:1A:1E': 'HPE/Aruba', '00:24:6C': 'HPE/Aruba', '20:4C:03': 'HPE/Aruba', '2C:37:3E': 'HPE/Aruba', '6C:F3:73': 'HPE/Aruba', '84:D4:7E': 'HPE/Aruba', '94:C6:91': 'HPE/Aruba', 'B0:5A:DA': 'HPE/Aruba',
        '00:1C:73': 'Arista Networks', '28:99:3A': 'Arista Networks', '44:4C:A8': 'Arista Networks', 'A8:2B:B5': 'Arista Networks',

        # Принтери
        '00:00:7D': 'Canon', '00:1E:8F': 'Canon', '00:21:01': 'Canon', '00:E0:98': 'Canon', '18:0C:AC': 'Canon', '30:89:99': 'Canon', '40:4D:7F': 'Canon', '54:EA:A8': 'Canon', '7C:B2:1B': 'Canon', '80:4F:58': 'Canon', '90:FD:9F': 'Canon', 'A0:51:0B': 'Canon', 'B4:9D:0B': 'Canon', 'C4:F7:D5': 'Canon', 'D8:9E:3F': 'Canon', 'F4:A9:97': 'Canon',
        '00:00:AE': 'Brother', '00:80:77': 'Brother', '00:80:A3': 'Brother', '10:08:B1': 'Brother', '30:05:5C': 'Brother', '3C:2A:F4': 'Brother', '4C:BB:58': 'Brother', '50:3C:C4': 'Brother', '58:9A:65': 'Brother', '6C:21:A2': 'Brother', '70:BD:B9': 'Brother', '80:C6:AB': 'Brother', '84:44:64': 'Brother', '90:8D:78': 'Brother', '9C:AD:EF': 'Brother', 'A4:16:04': 'Brother', 'A8:33:2D': 'Brother', 'B8:78:26': 'Brother', 'C0:11:73': 'Brother', 'C8:4B:D6': 'Brother', 'D0:17:C2': 'Brother', 'D4:AE:05': 'Brother', 'E0:B2:F1': 'Brother', 'E8:5A:A8': 'Brother', 'F0:2B:2E': 'Brother', 'F8:51:6D': 'Brother', 'FC:BA:24': 'Brother',
        '00:00:48': 'Epson', '00:01:E6': 'Epson', '00:0F:A9': 'Epson', '00:11:F5': 'Epson', '00:14:D5': 'Epson', '00:1B:3D': 'Epson', '00:21:89': 'Epson', '00:26:AB': 'Epson', '00:40:A5': 'Epson', '08:1F:B7': 'Epson', '10:C6:1F': 'Epson', '18:4E:94': 'Epson', '20:4C:9E': 'Epson', '28:FD:80': 'Epson', '30:96:FB': 'Epson', '38:4D:21': 'Epson', '40:A3:CC': 'Epson', '48:E9:F1': 'Epson', '50:EB:71': 'Epson', '58:FB:84': 'Epson', '60:4E:48': 'Epson', '68:B3:5E': 'Epson', '70:C6:EC': 'Epson', '78:CD:8E': 'Epson', '80:4A:14': 'Epson', '88:75:56': 'Epson', '90:F0:52': 'Epson', '98:F4:28': 'Epson', 'A0:B4:A5': 'Epson', 'A8:AD:3D': 'Epson', 'B0:98:2B': 'Epson', 'B8:DE:5E': 'Epson', 'C0:A0:DE': 'Epson', 'C8:9C:DC': 'Epson', 'D0:92:9E': 'Epson', 'D8:49:A8': 'Epson', 'E0:9E:FC': 'Epson', 'E8:F2:E2': 'Epson', 'F0:A1:32': 'Epson', 'F8:9E:28': 'Epson',
        '00:00:7C': 'Ricoh', '00:11:6B': 'Ricoh', '00:1D:9C': 'Ricoh', '00:26:73': 'Ricoh', '00:A0:B7': 'Ricoh', '08:B2:58': 'Ricoh', '10:18:B2': 'Ricoh', '18:59:7F': 'Ricoh', '20:89:86': 'Ricoh', '28:C9:14': 'Ricoh', '30:8D:99': 'Ricoh', '38:03:FB': 'Ricoh', '40:F2:01': 'Ricoh', '48:A7:F2': 'Ricoh', '50:2C:C6': 'Ricoh', '58:3F:54': 'Ricoh', '60:DF:56': 'Ricoh', '68:8B:28': 'Ricoh', '70:50:AF': 'Ricoh', '78:48:59': 'Ricoh', '80:B2:34': 'Ricoh', '88:64:7A': 'Ricoh', '90:4C:81': 'Ricoh', '98:54:1B': 'Ricoh', 'A0:23:9F': 'Ricoh', 'A8:E3:EE': 'Ricoh', 'B0:A4:23': 'Ricoh', 'B8:8A:E3': 'Ricoh', 'C0:CB:38': 'Ricoh', 'C8:3C:85': 'Ricoh', 'D0:27:51': 'Ricoh', 'D8:D4:3C': 'Ricoh', 'E0:78:E5': 'Ricoh', 'E8:9E:B4': 'Ricoh', 'F0:5D:89': 'Ricoh', 'F8:4D:89': 'Ricoh',
        
        # Мережеві пристрої / Комутатори / VoIP
        '00:0C:42': 'MikroTik', '18:FD:74': 'MikroTik', 'B8:69:F4': 'MikroTik', '48:8F:5A': 'MikroTik', 'CC:2D:E0': 'MikroTik', '2C:C8:1B': 'MikroTik', 'DC:2C:6E': 'MikroTik',
        '00:0B:82': 'Grandstream', 'E4:6F:13': 'Grandstream', '00:1A:E8': 'Grandstream', 'C0:74:AD': 'Grandstream',
        '00:15:65': 'Yealink', '80:5E:C0': 'Yealink', 'E4:AA:EA': 'Yealink', '00:04:13': 'Snom',
        '00:04:F2': 'Polycom', '64:16:7F': 'Polycom', '00:A8:59': 'Fanvil', '00:04:0D': 'Avaya',
        '00:25:9C': 'Cisco', '00:03:6B': 'Cisco', '00:1B:D4': 'Cisco', '00:11:21': 'Cisco',
        '00:15:6D': 'Ubiquiti', '00:27:22': 'Ubiquiti', '04:18:D6': 'Ubiquiti', '24:A4:3C': 'Ubiquiti', '44:D9:E7': 'Ubiquiti', '68:D7:9A': 'Ubiquiti', '74:83:C2': 'Ubiquiti', '78:8A:20': 'Ubiquiti', '80:2A:A8': 'Ubiquiti', 'B4:FB:E4': 'Ubiquiti', 'E0:63:DA': 'Ubiquiti', 'F0:9F:C2': 'Ubiquiti', 'FC:EC:DA': 'Ubiquiti',
        '00:00:1D': 'Juniper', '00:11:32': 'Synology', '00:08:9B': 'QNAP', '24:5E:BE': 'QNAP', '00:50:56': 'VMware', '08:00:27': 'VirtualBox',
        
        # Додані користувачем пристрої
        'E8:C9:13': 'Samsung Electronics Co.,Ltd'
    }

    # ОФЛАЙН БАЗА ВРАЗЛИВОСТЕЙ (CVE ТА ДЕФОЛТНІ ПАРОЛІ)
    COMMON_VULNS = [
        {"match": r"(?i)vsFTPd 2\.3\.4", "vuln": "[КРИТИЧНО] vsFTPd 2.3.4 Backdoor (CVE-2011-2523)", "exploit": "[RCE] Експлуатація через смайлик ':)' в логіні (Порт 6200)"},
        {"match": r"(?i)Apache/2\.4\.49", "vuln": "[КРИТИЧНО] Apache 2.4.49 Path Traversal (CVE-2021-41773)", "exploit": "[LFI/RCE] Читання файлів системи (/etc/passwd)"},
        {"match": r"(?i)Apache/2\.4\.50", "vuln": "[КРИТИЧНО] Apache 2.4.50 Path Traversal (CVE-2021-42013)", "exploit": "[LFI/RCE] Читання файлів системи (/etc/passwd)"},
        {"match": r"(?i)OpenSSH 7\.2", "vuln": "[СЕРЕДНЬО] OpenSSH 7.2p2 User Enumeration (CVE-2018-15473)", "exploit": "[РОЗВІДКА] Можливість перевірити існуючих користувачів"},
        {"match": r"(?i)RouterOS v(5\.|6\.[0-3][0-9]|6\.40|6\.41|6\.42\.0)", "vuln": "[КРИТИЧНО] MikroTik Winbox Exploit (CVE-2018-14847)", "exploit": "[ВИТІК/RCE] Читання файлу паролів без авторизації (Chimay Red)"},
        {"match": r"(?i)Microsoft-IIS/7\.5", "vuln": "[ВИСОКО] MS IIS 7.5 HTTP.sys (CVE-2015-1635)", "exploit": "[DoS/RCE] BSOD при спеціальному Range-запиті (MS15-034)"},
        {"match": r"(?i)Microsoft-IIS/6\.0", "vuln": "[КРИТИЧНО] MS IIS 6.0 WebDAV (CVE-2017-7269)", "exploit": "[RCE] Переповнення буфера через PROPFIND запит"},
        {"match": r"(?i)ProFTPD 1\.3\.5", "vuln": "[КРИТИЧНО] ProFTPD 1.3.5 mod_copy (CVE-2015-3306)", "exploit": "[RCE] Копіювання файлів без авторизації (SITE CPFR)"},
        {"match": r"(?i)Dropbear\s+([0-9]|10|201[0-5])", "vuln": "[ВИСОКО] Старий Dropbear SSH", "exploit": "[ВИТІК] Можливі RCE та обходи автентифікації в старих версіях"},
        {"match": r"(?i)Dahua", "vuln": "[РИЗИК] IP-Камера Dahua", "exploit": "[АТАКА] Вразливість CVE-2021-33044 або дефолтні паролі (admin:admin)"},
        {"match": r"(?i)Hikvision", "vuln": "[РИЗИК] IP-Камера Hikvision", "exploit": "[АТАКА] Backdoor авторизації (CVE-2017-7921) / admin:12345"},
        {"match": r"(?i)Grandstream.*FW:\s*(1\.0\.[0-8]\.)", "vuln": "[ВИСОКО] Застаріла ПЗ Grandstream", "exploit": "[АТАКА] SIP вразливості, дефолтні паролі (admin:admin)"},
        {"match": r"(?i)Freebox", "vuln": "[РИЗИК] Freebox OS", "exploit": "[АТАКА] Ризик дефолтних паролів / відкритих гостьових шар"},
        {"match": r"(?i)Tomcat/([5-7]\.|8\.0)", "vuln": "[ВИСОКО] Застарілий Apache Tomcat", "exploit": "[RCE] Ризик Ghostcat (CVE-2020-1938) по порту 8009"},
    ]

    def __init__(self, root):
        # CLI/configurable network interface for scans (set by CLI or auto-detected)
        self.scan_iface_name = None
        self.scan_iface_ip = None
        self.scan_iface_mac = None
        self.disable_l2 = False
        self.exclude_virtual_ifaces = True

        self.root = root
        self.root.title("NETFUCK - Мережевий Сканер та Аналізатор Вразливостей")
        self.root.geometry("1500x750")
        self.is_scanning = False
        self.stop_event = threading.Event()
        self.api_lock = threading.Lock() # Синхронізатор для API
        self.mac_cache = {} # Кеш для обходу блокувань API
        self.is_root = self.check_root()
        
        self.setup_fonts()
        self.build_gui()

        # Тепер, коли GUI та логгер існують, визначаємо мережу
        initial_network = self.get_local_network()
        self.target_var.set(initial_network)

        # Налаштування інтерфейсу за замовчуванням (може бути перезаписане з CLI)
        try:
            self.configure_interface()
        except Exception:
            pass

        if not self.is_root:
            self.log("УВАГА: Скрипт запущено без прав адміністратора (root/sudo).", "error")
            self.log("Агресивне сканування (через Scapy) може не працювати повноцінно.", "error")

    def setup_fonts(self):
        """Визначає шрифти для консистентного вигляду програми."""
        try:
            # Спроба використати сучасні шрифти, якщо вони є в системі
            self.font_bold = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
            self.font_normal = ctk.CTkFont(family="Segoe UI", size=12)
            self.font_mono = ctk.CTkFont(family="Consolas", size=11)
        except Exception:
            # Резервні системні шрифти
            self.font_bold = ctk.CTkFont(size=13, weight="bold")
            self.font_normal = ctk.CTkFont(size=12)
            self.font_mono = ctk.CTkFont(family="Courier", size=11)

    def check_root(self):
        """Перевіряє, чи запущено скрипт з правами адміністратора."""
        try:
            return os.geteuid() == 0
        except AttributeError: # Windows не має geteuid
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False

    def get_local_network(self):
        """Автоматично визначає локальну мережу та її маску, використовуючи найкращий доступний метод."""
        # 1. Найкращий метод: netifaces (якщо встановлено)
        if 'netifaces' in globals():
            try:
                gws = netifaces.gateways()
                default_gateway_info = gws.get('default', {}).get(netifaces.AF_INET)
                if default_gateway_info:
                    interface = default_gateway_info[1]
                    addrs = netifaces.ifaddresses(interface)
                    ip_info = addrs[netifaces.AF_INET][0]
                    addr = ip_info['addr']
                    netmask = ip_info['netmask']
                    network = ipaddress.IPv4Network(f"{addr}/{netmask}", strict=False)
                    self.log(f"Автоматично визначено мережу: {str(network)} (через 'netifaces')", "debug")
                    return str(network)
            except Exception as e:
                self.log(f"Помилка netifaces: {e}. Використовую резервний метод.", "debug")

        # 2. Резервний метод: сокети (але з маскою /24)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
            network_str = str(ipaddress.IPv4Network(f"{local_ip}/24", strict=False))
            self.log("Модуль 'netifaces' не знайдено. Припускаю маску /24.", "debug")
            self.log(f"Визначена мережа: {network_str}. Для точного визначення маски встановіть 'pip install netifaces'", "debug")
            return network_str
        except Exception:
            pass

        # 3. Останній резервний варіант
        return "192.168.1.0/24"

    def is_virtual_iface(self, name: str) -> bool:
        if not name:
            return False
        n = name.lower()
        keywords = ['virtual', 'vmware', 'vbox', 'tunnel', 'loopback', 'docker', 'br-', 'tap', 'hyper-v', 'veth', 'zerotier', 'wireguard', 'vpn', 'ppp', 'wg']
        return any(k in n for k in keywords)

    def configure_interface(self, iface_name: str = None, disable_l2: bool = False):
        """Configure which local interface/ip to use for scans.
        If iface_name is None, auto-selects the primary non-virtual interface.
        """
        self.disable_l2 = disable_l2
        try:
            if iface_name:
                self.scan_iface_name = iface_name
                if 'netifaces' in globals():
                    addrs = netifaces.ifaddresses(iface_name)
                    inet = addrs.get(netifaces.AF_INET)
                    if inet:
                        self.scan_iface_ip = inet[0].get('addr')
                    macs = addrs.get(netifaces.AF_LINK) or addrs.get(netifaces.AF_PACKET)
                    if macs:
                        self.scan_iface_mac = macs[0].get('addr')
                return

            # Auto-detect
            if 'netifaces' in globals():
                gws = netifaces.gateways()
                default_iface = None
                try:
                    default_iface = gws.get('default', {}).get(netifaces.AF_INET)[1]
                except Exception:
                    default_iface = None

                # Prefer non-virtual gateway interface
                if default_iface and not self.is_virtual_iface(default_iface):
                    self.scan_iface_name = default_iface
                else:
                    # pick first non-virtual interface with an ipv4
                    for iface in netifaces.interfaces():
                        if self.is_virtual_iface(iface):
                            continue
                        addrs = netifaces.ifaddresses(iface)
                        inet = addrs.get(netifaces.AF_INET)
                        if inet:
                            self.scan_iface_name = iface
                            break

                if self.scan_iface_name:
                    addrs = netifaces.ifaddresses(self.scan_iface_name)
                    inet = addrs.get(netifaces.AF_INET)
                    if inet:
                        self.scan_iface_ip = inet[0].get('addr')
                    macs = addrs.get(netifaces.AF_LINK) or addrs.get(netifaces.AF_PACKET)
                    if macs:
                        self.scan_iface_mac = macs[0].get('addr')
                    self.log(f"Використовую інтерфейс для сканування: {self.scan_iface_name} ({self.scan_iface_ip})", "debug")
                    return

            # Fallback: socket connect to determine IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                self.scan_iface_ip = s.getsockname()[0]
            self.log(f"Визначено IP для сканування: {self.scan_iface_ip} (без netifaces).", "debug")
        except Exception as e:
            self.log(f"configure_interface error: {e}", "debug")

    def build_gui(self):
        """Створює та компонує всі елементи графічного інтерфейсу."""
        self.root.configure(fg_color="#242424")
        self.setup_styles()
        self.create_top_frame()
        self.create_results_frame()
        self.create_log_frame()
        self.create_context_menu()

    def setup_styles(self):
        # Налаштування стилю для Treeview (Темна тема)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2B2B2B",
                        foreground="#DCE4EE",
                        rowheight=28,
                        fieldbackground="#2B2B2B",
                        bordercolor="#343638",
                        borderwidth=0,
                        font=self.font_normal)
        style.map('Treeview', background=[('selected', '#007ACC')], foreground=[('selected', 'white')])
        style.configure("Treeview.Heading",
                        background="#3C3F41",
                        foreground="#EAEAEA",
                        relief="flat", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        style.map("Treeview.Heading", background=[('active', '#4A4D4E')])

    def create_top_frame(self):
        # Верхня панель (Налаштування)
        top_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        ctk.CTkLabel(top_frame, text="Мережа:", font=self.font_normal).pack(side=tk.LEFT, padx=(0, 5))
        self.target_var = tk.StringVar()
        ctk.CTkEntry(top_frame, textvariable=self.target_var, width=180, font=self.font_normal).pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(top_frame, text="Режим:", font=self.font_normal).pack(side=tk.LEFT, padx=(10, 5))
        self.mode_var = ctk.StringVar(value="Стандартне (Основні порти + mDNS)")
        mode_cb = ctk.CTkComboBox(top_frame, variable=self.mode_var, width=250, state="readonly",
                                  font=self.font_normal,
                                  values=["Тихе (ARP + ICMP, Без портів)", "Обережне (Повільне, обхід ESET)", "Стандартне (Основні порти + mDNS)", "Кастомне (Вказані порти)", "Агресивне (Всі проби + Топ порти)", "Віддалене (Інтернет)"],
                                  command=self.on_mode_change)
        mode_cb.pack(side=tk.LEFT, padx=5)

        self.custom_ports_var = tk.StringVar(value="80,443,8080")
        self.custom_ports_entry = ctk.CTkEntry(top_frame, textvariable=self.custom_ports_var, width=120, font=self.font_normal, state="disabled")
        self.custom_ports_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.only_open_var = tk.BooleanVar(value=False)
        self.only_open_cb = ctk.CTkCheckBox(top_frame, text="Тільки відкриті порти", variable=self.only_open_var, font=self.font_normal)
        self.only_open_cb.pack(side=tk.LEFT, padx=(10, 5))

        self.auto_subnet_var = tk.BooleanVar(value=True)
        self.auto_subnet_cb = ctk.CTkCheckBox(top_frame, text="Авто-пошук підмереж", variable=self.auto_subnet_var, font=self.font_normal)
        self.auto_subnet_cb.pack(side=tk.LEFT, padx=(10, 5))

        self.scan_btn = ctk.CTkButton(top_frame, text="🚀 Почати Сканування", font=self.font_bold, command=self.start_scan_thread, fg_color="#007ACC", hover_color="#005F9E")
        self.scan_btn.pack(side=tk.LEFT, padx=15)
        
        self.stop_btn = ctk.CTkButton(top_frame, text="🛑 Зупинити", font=self.font_bold, fg_color="#E53935", hover_color="#C62828", command=self.stop_scan, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Група кнопок для експорту та сесій
        actions_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        actions_frame.pack(side=tk.RIGHT, padx=(5, 0))
        self.export_html_btn = ctk.CTkButton(actions_frame, text="📄 Експорт (HTML)", font=self.font_normal, command=self.export_to_html, state="disabled", fg_color="#555555", hover_color="#444444")
        self.export_html_btn.pack(side=tk.LEFT, padx=5)
        self.export_csv_btn = ctk.CTkButton(actions_frame, text="💾 Експорт (CSV)", font=self.font_normal, command=self.export_to_csv, state="disabled", fg_color="#555555", hover_color="#444444")
        self.export_csv_btn.pack(side=tk.LEFT, padx=5)

    def on_mode_change(self, choice):
        """Активує або деактивує поле для вводу кастомних портів."""
        if "Кастомне" in choice:
            self.custom_ports_entry.configure(state="normal")
        else:
            self.custom_ports_entry.configure(state="disabled")

    def parse_ports(self, port_str):
        """Парсить рядок з портів (напр. '80, 443, 8000-8010') у список цілих чисел."""
        ports = set()
        for part in port_str.split(','):
            part = part.strip()
            if not part: continue
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    if 1 <= start <= 65535 and 1 <= end <= 65535 and start <= end:
                        ports.update(range(start, end + 1))
                except ValueError: pass
            else:
                try:
                    port = int(part)
                    if 1 <= port <= 65535:
                        ports.add(port)
                except ValueError: pass
        return sorted(list(ports))

    def create_results_frame(self):
        # Центральна панель (Таблиця результатів)
        mid_frame = ctk.CTkFrame(self.root, fg_color="#2B2B2B")
        mid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("IP", "MAC", "Ім'я хоста", "Виробник", "Пристрій / ОС", "Версії ПЗ", "Стан Портів", "Вразливості", "Експлуатація")
        self.tree = ttk.Treeview(mid_frame, columns=columns, show='headings')
        self.tree.heading("IP", text="IP Адреса")
        self.tree.heading("MAC", text="MAC Адреса")
        self.tree.heading("Ім'я хоста", text="Ім'я хоста")
        self.tree.heading("Виробник", text="Виробник Обладнання")
        self.tree.heading("Пристрій / ОС", text="Тип Пристрою / ОС")
        self.tree.heading("Версії ПЗ", text="Версії ПЗ")
        self.tree.heading("Стан Портів", text="Стан Портів")
        self.tree.heading("Вразливості", text="Знайдені Вразливості")
        self.tree.heading("Експлуатація", text="Вектор Атаки / Експлуатація")
        
        self.tree.column("IP", width=120, anchor='w')
        self.tree.column("MAC", width=130, anchor='w')
        self.tree.column("Ім'я хоста", width=150, anchor='w')
        self.tree.column("Виробник", width=160, anchor='w')
        self.tree.column("Пристрій / ОС", width=280, anchor='w')
        self.tree.column("Версії ПЗ", width=220, anchor='w')
        self.tree.column("Стан Портів", width=200, anchor='w')
        self.tree.column("Вразливості", width=220, anchor='w')
        self.tree.column("Експлуатація", width=300, anchor='w')
        
        scroll = ttk.Scrollbar(mid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=2)

        self.tree.bind("<Button-3>", self.show_context_menu) # Для Windows/Linux
        self.tree.bind("<Button-2>", self.show_context_menu) # Для macOS

    def create_log_frame(self):
        # Нижня панель (Логи)
        bottom_frame = ctk.CTkFrame(self.root, fg_color="#2B2B2B")
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        log_header = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        log_header.pack(fill=tk.X, padx=2, pady=(2, 0))
        ctk.CTkLabel(log_header, text="Журнал подій:", font=self.font_bold).pack(side=tk.LEFT)
        ctk.CTkButton(log_header, text="📋 Копіювати", width=100, height=24, font=self.font_normal, fg_color="#555555", hover_color="#444444", command=self.copy_logs).pack(side=tk.RIGHT)
        ctk.CTkButton(log_header, text="🗑️ Очистити", width=100, height=24, font=self.font_normal, command=self.clear_logs).pack(side=tk.RIGHT, padx=5)
        
        self.log_area = ctk.CTkTextbox(bottom_frame, height=150, text_color="#DCE4EE", fg_color="#202020", font=self.font_mono, border_width=1, border_color="#3C3F41")
        self.log_area.pack(fill=tk.X, padx=2, pady=2)
        self.log_area.tag_config("error", foreground="#ff6b6b")
        self.log_area.tag_config("success", foreground="#50fa7b")
        self.log_area.tag_config("info", foreground="#cccccc")
        self.log_area.tag_config("debug", foreground="#8ab4f8")
        self.log_area.configure(state='disabled')

    def create_context_menu(self):
        # Створення контекстного меню
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#2B2B2B", fg="#DCE4EE", activebackground="#007ACC", activeforeground="white", relief='flat', font=self.font_normal)
        self.context_menu.add_command(label="📋 Копіювати IP-адресу", command=lambda: self.copy_selected_item(0, "IP"))
        self.context_menu.add_command(label="📋 Копіювати MAC-адресу", command=lambda: self.copy_selected_item(1, "MAC"))
        self.context_menu.add_command(label="📋 Копіювати Ім'я хоста", command=lambda: self.copy_selected_item(2, "Ім'я хоста"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🌐 Відкрити в браузері (HTTP)", command=lambda: self.open_in_browser("http"))
        self.context_menu.add_command(label="🔒 Відкрити в браузері (HTTPS)", command=lambda: self.open_in_browser("https"))
        self.context_menu.add_command(label="🔍 Шукати на Shodan.io", command=self.search_on_shodan)

    def log(self, message, status="info", from_thread=False):
        """Безпечний вивід логів з інших потоків"""
        def _update_ui():
            self.log_area.configure(state='normal')
            time_str = datetime.now().strftime("%H:%M:%S")
            prefix = "[*]"
            if status == "error": prefix = "[!] "
            elif status == "success": prefix = "[+] "
            elif status == "debug": prefix = "[~] "
            self.log_area.insert(tk.END, f"{time_str} {prefix} {message}\n", status)
            self.log_area.see(tk.END)
            self.log_area.configure(state='disabled')
        if from_thread:
            self.root.after(0, _update_ui)
        else:
            _update_ui()

    def export_to_csv(self):
        """Експорт результатів з таблиці у CSV файл"""
        if not self.tree.get_children():
            messagebox.showinfo("Пусто", "Немає даних для експорту.")
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                 title="Зберегти звіт як...")
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["IP Адреса", "MAC Адреса", "Ім'я хоста", "Виробник Обладнання", "Тип Пристрою / ОС", "Версії ПЗ", "Стан Портів", "Вразливості", "Експлуатація"])
                    for row_id in self.tree.get_children():
                        writer.writerow(self.tree.item(row_id)['values'])
                messagebox.showinfo("Успіх", f"Звіт успішно збережено у:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося зберегти файл:\n{e}")

    def copy_logs(self):
        """Копіює весь текст логів у буфер обміну"""
        logs = self.log_area.get("1.0", tk.END).strip()
        if logs:
            self.root.clipboard_clear()
            self.root.clipboard_append(logs)
            self.log("Журнал подій скопійовано до буфера обміну.", "debug")
        else:
            messagebox.showinfo("Пусто", "Немає логів для копіювання.")

    def export_to_html(self):
        """Експорт результатів у стилізований HTML звіт."""
        if not self.tree.get_children():
            messagebox.showinfo("Пусто", "Немає даних для експорту.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".html",
                                                 filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                                                 title="Зберегти HTML звіт як...")
        if not file_path:
            return

        # --- HTML/CSS Шаблон ---
        html_template = """
        <!DOCTYPE html>
        <html lang="uk">
        <head>
            <meta charset="UTF-8">
            <title>Звіт Сканування Мережі</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #1e1e1e; color: #d4d4d4; margin: 0; padding: 20px; }}
                .container {{ max-width: 95%; margin: auto; background-color: #252526; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); overflow: hidden; }}
                h1 {{ text-align: center; color: #4e9ad8; padding: 20px; margin: 0; background-color: #2d2d30; border-bottom: 1px solid #3e3e42; }}
                p.info {{ text-align: center; padding-bottom: 20px; color: #a0a0a0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #3e3e42; white-space: pre-wrap; word-break: break-word; vertical-align: top; font-size: 13px; }}
                th {{ background-color: #333337; color: #d4d4d4; font-weight: 600; }}
                tr:hover {{ background-color: #3e3e42; }}
                .ip-link a {{ color: #9cdcfe; text-decoration: none; font-weight: bold; }}
                .ip-link a:hover {{ text-decoration: underline; }}
                .vuln-critical {{ background-color: #5a1d1d; }}
                .vuln-risk {{ background-color: #5a481d; }}
                tr.vuln-critical:hover {{ background-color: #7a2d2d; }}
                tr.vuln-risk:hover {{ background-color: #7a682d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Звіт Сканування Мережі</h1>
                <p class="info">Згенеровано: {scan_date} | Ціль: {scan_target}</p>
                <table>
                    <thead><tr><th>IP Адреса</th><th>MAC Адреса</th><th>Ім'я хоста</th><th>Виробник</th><th>Тип Пристрою / ОС</th><th>Версії ПЗ</th><th>Стан Портів</th><th>Вразливості</th><th>Вектор Атаки</th></tr></thead>
                    <tbody>{table_rows}</tbody>
                </table>
            </div>
        </body>
        </html>
        """

        table_rows = ""
        for row_id in self.tree.get_children():
            values = [str(v) for v in self.tree.item(row_id)['values']]
            ip, mac, hostname, vendor, device, versions, ports, vulns, exploit = values
            
            vuln_class = ""
            if "[КРИТИЧНО]" in vulns:
                vuln_class = "vuln-critical"
            elif "[РИЗИК]" in vulns or "[ВИТІК ДАНИХ]" in vulns:
                vuln_class = "vuln-risk"

            import html
            values_escaped = [html.escape(v).replace('\n', '<br>') for v in values]
            ip_e, mac_e, hostname_e, vendor_e, device_e, versions_e, ports_e, vulns_e, exploit_e = values_escaped

            table_rows += f'<tr class="{vuln_class}"><td class="ip-link"><a href="http://{ip}" target="_blank">{ip_e}</a></td><td>{mac_e}</td><td>{hostname_e}</td><td>{vendor_e}</td><td>{device_e}</td><td>{versions_e}</td><td>{ports_e}</td><td>{vulns_e}</td><td>{exploit_e}</td></tr>'

        scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        scan_target = self.target_var.get()
        final_html = html_template.format(scan_date=scan_date, scan_target=scan_target, table_rows=table_rows)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_html)
            self.log(f"HTML звіт успішно збережено у: {file_path}", "success")
            messagebox.showinfo("Успіх", f"HTML звіт успішно збережено у:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти HTML файл:\n{e}")

    def clear_logs(self):
        """Очищує поле з логами"""
        self.log_area.configure(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.configure(state='disabled')

    def show_context_menu(self, event):
        """Показує контекстне меню при правому кліку на рядку"""
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_selected_item(self, column_index, item_name):
        """Копіює значення з обраної колонки у буфер обміну"""
        selected_id = self.tree.selection()
        if not selected_id: return
        selected_item = self.tree.item(selected_id[0])
        item_value = selected_item['values'][column_index]
        self.root.clipboard_clear()
        self.root.clipboard_append(item_value)
        self.log(f"{item_name}-адресу {item_value} скопійовано.", "debug")

    def open_in_browser(self, protocol):
        """Відкриває IP-адресу обраного пристрою у веб-браузері."""
        selected_id = self.tree.selection()
        if not selected_id: return
        ip = self.tree.item(selected_id[0])['values'][0]
        url = f"{protocol}://{ip}"
        try:
            webbrowser.open_new_tab(url)
            self.log(f"Відкриваю {url} у браузері...", "debug")
        except Exception as e:
            self.log(f"Не вдалося відкрити браузер: {e}", "error")

    def search_on_shodan(self):
        """Шукає IP-адресу обраного пристрою на Shodan.io."""
        selected_id = self.tree.selection()
        if not selected_id: return
        ip = self.tree.item(selected_id[0])['values'][0]
        url = f"https://www.shodan.io/host/{ip}"
        try:
            webbrowser.open_new_tab(url)
            self.log(f"Шукаю інформацію про {ip} на Shodan.io...", "debug")
        except Exception as e:
            self.log(f"Не вдалося відкрити браузер: {e}", "error")

    def insert_row(self, ip, mac, hostname, vendor, device, versions, ports, vulns, exploit):
        """Додає знайдений пристрій у таблицю GUI"""
        self.tree.insert('', tk.END, values=(ip, mac, hostname, vendor, device, versions, ports, vulns, exploit))

    def start_scan_thread(self):
        targets_input = self.target_var.get().strip()
        target_list = [t.strip() for t in targets_input.split(',') if t.strip()]
        
        valid_targets = []
        for t in target_list:
            try:
                valid_targets.append(ipaddress.ip_network(t, strict=False))
            except ValueError:
                messagebox.showerror("Помилка", f"Невірний формат мережі: {t}\nВикористовуйте наприклад 192.168.1.0/24")
                return
                
        if not valid_targets:
            messagebox.showerror("Помилка", "Не вказано жодної підмережі для сканування.")
            return

        if self.is_scanning:
            return
        self.is_scanning = True
        self.stop_event.clear()
        self.scan_btn.configure(state="disabled")
        self.update_action_buttons_state(is_scanning=True)
        self.stop_btn.configure(state="normal")
        self.tree.delete(*self.tree.get_children())
        self.clear_logs()

        mode = self.mode_var.get()
        # Якщо користувач не має прав адміністратора, забороняємо агресивний режим і перемикаємо на стандартний
        if not self.is_root and "Агресивне" in mode:
            try:
                messagebox.showwarning("Обмежені права", "Агресивний режим потребує прав адміністратора. Переключаю на 'Стандартне'.")
            except Exception:
                pass
            self.mode_var.set("Стандартне (Основні порти + mDNS)")
            mode = self.mode_var.get()
        # Якщо обрано віддалений режим — переконатись у дозволі оператора
        if "Віддале" in mode or "Remote" in mode:
            ok = messagebox.askyesno("Підтвердження дозволу", "Ви підтверджуєте, що маєте письмовий дозвіл на віддалене сканування цих мереж?\n(Сканування без дозволу може бути незаконним)")
            if not ok:
                self.is_scanning = False
                self.scan_btn.configure(state="normal")
                self.update_action_buttons_state()
                return
        custom_ports = None
        if "Кастомне" in mode:
            custom_ports = self.parse_ports(self.custom_ports_var.get())
            if not custom_ports:
                messagebox.showerror("Помилка", "Вкажіть коректні порти для кастомного режиму (наприклад: 80,443,8000-8010)")
                self.is_scanning = False
                self.scan_btn.configure(state="normal")
                self.update_action_buttons_state()
                return

        only_open = self.only_open_var.get()
        auto_subnet = self.auto_subnet_var.get()
        threading.Thread(target=self.run_scan, args=(valid_targets, mode, custom_ports, only_open, auto_subnet), daemon=True).start()

    def stop_scan(self):
        self.log("Отримано сигнал на екстрену зупинку! Завершую потоки...", "error")
        self.stop_event.set()
        self.stop_btn.configure(state="disabled")

    def run_scan(self, targets, mode, custom_ports=None, only_open=False, auto_subnet=False):
        if auto_subnet:
            targets = self.discover_connected_subnets(targets)
            
        for target in targets:
            if self.stop_event.is_set():
                break
            self.log(f"ІНІЦІАЛІЗАЦІЯ БОЙОВОГО СКАНУВАННЯ ПІДМЕРЕЖІ: {str(target)}", "success", from_thread=True)
            self.run_native_scan(str(target), mode, custom_ports, only_open)
            
        self.root.after(0, self.finish_scan)

    def discover_connected_subnets(self, target_networks):
        """Робить пінг-свіп поширених шлюзів для виявлення сусідніх маршрутизованих VLAN та підмереж"""
        self.log("Авто-розвідка: шукаю підключені маршрутизатором сусідні підмережі (VLAN)...", "debug", from_thread=True)
        discovered_str = set([str(net) for net in target_networks])
        gateways_to_test = set()

        for net in target_networks:
            net_str = net.network_address.exploded
            if net_str.startswith('192.168.'):
                for i in range(0, 256):
                    gateways_to_test.add(f"192.168.{i}.1")
                    gateways_to_test.add(f"192.168.{i}.254")
            elif net_str.startswith('10.'):
                parts = net_str.split('.')
                base = f"10.{parts[1]}"
                for i in range(0, 256):
                    gateways_to_test.add(f"{base}.{i}.1")
                    gateways_to_test.add(f"{base}.{i}.254")
            elif net_str.startswith('172.'):
                parts = net_str.split('.')
                if 16 <= int(parts[1]) <= 31:
                    base = f"172.{parts[1]}"
                    for i in range(0, 256):
                        gateways_to_test.add(f"{base}.{i}.1")
                        gateways_to_test.add(f"{base}.{i}.254")

        # Відфільтровуємо IP, які вже включені до введених нами цільових мереж
        final_gateways = []
        for gw in gateways_to_test:
            ip_obj = ipaddress.ip_address(gw)
            if not any(ip_obj in net for net in target_networks):
                final_gateways.append(gw)

        if not final_gateways:
            return target_networks

        def check_gw(ip):
            if self.stop_event.is_set(): return None
            is_up, _ = self.ping_ip(ip)
            return ip if is_up else None

        self.log(f"Пінг-свіп {len(final_gateways)} можливих шлюзів для перевірки маршрутів...", "debug", from_thread=True)
        new_networks = []
        with ThreadPoolExecutor(max_workers=150) as executor:
            results = executor.map(check_gw, final_gateways)

        for res in results:
            if res:
                parts = res.split('.')
                new_net = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
                if new_net not in discovered_str:
                    discovered_str.add(new_net)
                    new_networks.append(ipaddress.ip_network(new_net, strict=False))
                    self.log(f"Знайдено підключену підмережу: {new_net} (Шлюз {res} відповів)", "success", from_thread=True)

        if new_networks:
            self.log(f"Додано до черги сканування {len(new_networks)} нових підмереж!", "success", from_thread=True)
        else:
            self.log("Нових підмереж не виявлено.", "debug", from_thread=True)

        return target_networks + new_networks

    def finish_scan(self):
        self.is_scanning = False
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.update_action_buttons_state()
        if self.stop_event.is_set():
            self.log("СКАНУВАННЯ ПЕРЕРВАНО ОПЕРАТОРОМ.", "error", from_thread=True)
        else:
            self.log("СКАНУВАННЯ УСПІШНО ЗАВЕРШЕНО!", "success", from_thread=True)

    def update_action_buttons_state(self, is_scanning=False):
        """Оновлює стан кнопок експорту."""
        state = "disabled" if is_scanning or not self.tree.get_children() else "normal"
        self.export_csv_btn.configure(state=state)
        self.export_html_btn.configure(state=state)

    # ========================== РІДНИЙ СКАНИР (Native Python) ==========================

    def get_full_arp_table(self):
        """Швидко отримує всі MAC-адреси за один виклик до системи"""
        arp_table = {}
        try:
            if platform.system().lower() == 'windows':
                output = subprocess.check_output(['arp', '-a'], encoding='cp866', errors='ignore')
            else:
                output = subprocess.check_output(['arp', '-an'], encoding='utf-8', errors='ignore')
            for line in output.splitlines():
                # Більш гнучкий regex для підтримки різних форматів виводу arp -a (Linux, Windows, macOS)
                match = re.search(r'\(?(\d+\.\d+\.\d+\.\d+)\)?\s+.*?\s+(([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2})', line)
                if match:
                    ip = match.group(1)
                    mac = match.group(2).upper().replace('-', ':')
                    arp_table[ip] = mac
        except Exception:
            pass
        return arp_table

    def aggressive_arp_discovery(self, target_network):
        """Використовує Scapy для відправки сирих ARP-запитів (найбільш надійний метод)"""
        arp_table = {}
        try:
            if 'srp' not in globals(): # Перевіряємо, чи Scapy встановлено
                self.log("Scapy не знайдено. Використовуються стандартні методи ARP.", "debug", from_thread=True)
                return {}

            self.log("Запуск агресивного ARP-сканування через Scapy...", "debug", from_thread=True)
            srp_kwargs = {}
            if self.scan_iface_name:
                srp_kwargs['iface'] = self.scan_iface_name
            ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=target_network), timeout=2, verbose=False, **srp_kwargs)
            for _, rcv in ans:
                arp_table[rcv.psrc] = rcv.hwsrc.upper()
            self.log(f"Scapy виявив {len(arp_table)} пристроїв.", "success", from_thread=True)
        except Exception as e:
            self.log(f"Помилка Scapy ARP Discovery: {e}", "error", from_thread=True)
        return arp_table

    def run_native_scan(self, target_network, mode, custom_ports=None, only_open=False):
        is_stealth = "Тихе" in mode
        is_careful = "Обережне" in mode
        is_aggressive = "Агресивне" in mode
        is_remote = "Віддале" in mode or "Remote" in mode
        is_custom = "Кастомне" in mode

        network = ipaddress.ip_network(target_network, strict=False)
        hosts = list(network.hosts())
        if is_careful:
            # Обхід евристики ESET: скануємо IP хаотично, а не по порядку (1, 2, 3...), щоб не викликати підозр
            random.shuffle(hosts)
        
        arp_cache = self.get_full_arp_table()
        if is_stealth or is_careful:
            self.log("Етап 1: Читання локального ARP-кешу (Без агресивних ARP-проб Scapy)...", "debug", from_thread=True)
        else:
            # Для віддаленого сканування або якщо L2 вимкнено — уникаємо широкомовних ARP (Scapy)
            if is_remote or getattr(self, 'disable_l2', False):
                self.log("Пропускаю агресивне ARP-сканування через віддалений режим/налаштування.", "debug", from_thread=True)
            else:
                self.log("Етап 1: Агресивне ARP/Scapy виявлення для знаходження 'сплячих' пристроїв...", "debug", from_thread=True)
                arp_cache.update(self.aggressive_arp_discovery(target_network))

        self.log(f"Етап 2: Знайдено {len(arp_cache)} пристроїв на апаратному рівні. Починаю аналіз всіх {len(hosts)} IP...", "success", from_thread=True)
        
        def check_host(ip_obj):
            if self.stop_event.is_set(): return
            
            # Розмазуємо старт потоків у часі, віддалене сканування має більший інтервал
            if is_remote:
                time.sleep(random.uniform(0.05, 1.0))
            else:
                time.sleep(random.uniform(0.01, 0.5))
            try:
                ip = str(ip_obj)
                
                is_in_arp = ip in arp_cache
                # Ініціалізуємо прапор відповіді на ping до використання
                is_ping_up, ttl = False, None
                if is_in_arp:
                    self.log(f"[{ip}] Знайдено в ARP-кеші.", "debug", from_thread=True)

                # Раніше була логіка відсіву "ARP-only привидів" — видалено.
                # Тепер ми перевіряємо всі хости повноцінно (ping, порти, банери), щоб уникнути пропусків.
                
                is_ping_up, ttl = False, None
                if not is_in_arp:
                    is_ping_up, ttl = self.ping_ip(ip)
                    if is_ping_up:
                        self.log(f"[{ip}] Відповів на стандартний ICMP Ping.", "debug", from_thread=True)

                has_firewall_bypass = False
                if not is_in_arp and not is_ping_up and not is_stealth:
                    if self.stop_event.is_set(): return
                    # ESET жорстко блокує "сирі" пакети Scapy, тому ми їх не використовуємо в Обережному режимі
                    if not is_careful and self.probe_scapy_ping(ip):
                        self.log(f"[{ip}] Відповів на ICMP Ping (Scapy).", "debug", from_thread=True)
                        has_firewall_bypass = True
                    if self.stop_event.is_set(): return
                    # ESET часто блокує сирі TCP-пакети Scapy, тому в "Обережному" режимі ми їх не використовуємо
                    if not is_careful and not has_firewall_bypass and self.probe_tcp_ack(ip):
                        self.log(f"[{ip}] Відповів на TCP ACK Probe (Bypass).", "debug", from_thread=True)
                        has_firewall_bypass = True

                open_ports = []
                open_ports_only_numbers = []
                snmp_info, upnp_info, mdns_info, sip_info = "", "", "", "" # Ці змінні будуть містити деталі, а не просто статус
                mndp_info, netbios_name, mdns_hostname, llmnr_name = "", "", "", ""
                upnp_hostname, snmp_hostname, mndp_identity, dns_name, wsd_hostname = "", "", "", "", ""
                is_smbv1, axfr_result = False, None

                if not is_stealth:
                    # Для віддаленого режиму уникаємо локальних/multicast UDP-проб (mDNS, MNDP, LLMNR)
                    if not is_custom:
                        if self.stop_event.is_set(): return
                        if not is_remote:
                            # локальні або link-local тести
                            # Виконуємо всі локальні UDP-проби (mDNS, NetBIOS, LLMNR, WSD, MNDP)
                            mdns_info = self.probe_mdns(ip) # mDNS - UDP, не працює через інтернет
                            netbios_name = self.get_netbios_name(ip) # NetBIOS - UDP
                            mdns_hostname = self.get_mdns_hostname(ip)
                            llmnr_name = self.get_llmnr_name(ip)
                            wsd_hostname = self.probe_wsd(ip)
                            mndp_info, mndp_identity = self.probe_mikrotik_mndp(ip)
                            mndp_info, mndp_identity = self.probe_mikrotik_mndp(ip)
                        else:
                            # Віддалений режим: мінімальні UDP-проби, але залишаємо SIP та SNMP (якщо агресивно)
                            sip_info = self.probe_sip(ip)
                            mndp_info, mndp_identity = "", ""

                        if is_aggressive:
                            if self.stop_event.is_set(): return
                            snmp_info, snmp_hostname = self.probe_snmp(ip)

                    if self.stop_event.is_set(): return
                    self.log(f"[{ip}] Сканую порти...", "debug", from_thread=True)
                    # Для віддаленого режиму використовуємо більший таймаут для TCP connect
                    port_timeout = 2.0 if is_remote else None
                    open_ports = self.fast_port_scan(ip, mode, custom_ports, socket_timeout=port_timeout)
                    if any(status == "open" for _, status in open_ports):
                        self.log(f"[{ip}] Знайдено відкриті порти: {', '.join(str(p) for p, status in open_ports if status == 'open')}", "debug", from_thread=True)

                    # Витягуємо тільки відкриті порти для подальших проб, які залежать від відкритого порту
                    open_ports_only_numbers = [p for p, status in open_ports if status == "open"]

                    # Проби, що вимагають відкритого TCP порту, запускаємо після сканування портів
                    if 445 in open_ports_only_numbers: is_smbv1 = self.probe_smb_v1(ip)
                    if 53 in open_ports_only_numbers: axfr_result = self.probe_dns_axfr(ip)

                has_tcp_response = any(status in ("open", "closed") for _, status in open_ports)
                has_l4_response = bool(has_tcp_response or snmp_info or upnp_info or mdns_info or sip_info or mndp_info or netbios_name)
                is_up = is_in_arp or is_ping_up or has_l4_response or has_firewall_bypass
                
                if self.stop_event.is_set(): return

                if is_up:
                    log_reason = "ARP" if is_in_arp else "Ping" if is_ping_up else "L4 Проба" if has_l4_response else "Firewall Bypass"
                    log_msg = f"ЗНАЙДЕНО ВІДПОВІДЬ ({log_reason}) від {ip}!"
                    self.log(log_msg, "success", from_thread=True)

                    mac = arp_cache.get(ip) or self.get_mac_from_arp(ip)
                    vendor = self.get_vendor_by_mac(mac)

                    if ttl is None:
                        _, ttl = self.ping_ip(ip)

                    banners, ssl_name, ftp_anon = {}, "", False
                    mikrotik_version, grandstream_model = "", ""
                    
                    if not is_stealth:
                        self.log(f"[{ip}] Збираю додаткову інформацію...", "debug", from_thread=True)
                        try:
                            # DNS PTR із таймаутом (dnspython або thread-wrapped gethostbyaddr)
                            dns_name = self.get_reverse_dns(ip)
                        except: pass

                        banners = self.grab_deep_banners(ip, open_ports_only_numbers)
                        ssl_name = self.get_ssl_cert_name(ip, open_ports_only_numbers)
                        
                        # Якщо режим віддалений — виконуємо додаткові віддалені проби та зливаємо результати
                        if is_remote:
                            try:
                                remote_results = self.remote_service_probes(ip, open_ports, is_aggressive, socket_timeout=port_timeout)
                                if remote_results:
                                    # Merge banners
                                    if 'banners' in remote_results:
                                        banners.update(remote_results.get('banners', {}))
                                    # SSL CN
                                    if not ssl_name and 'ssl_cn' in remote_results:
                                        first = remote_results['ssl_cn']
                                        if isinstance(first, list) and first:
                                            ssl_name = first[0]
                                    # hostnames (PTR/SNMP)
                                    if 'hostnames' in remote_results:
                                        for hsrc, hval in remote_results['hostnames']:
                                            if not dns_name:
                                                dns_name = hval
                                    # mikrotik/winbox
                                    if 'mikrotik' in remote_results and not mikrotik_version:
                                        mikrotik_version = remote_results['mikrotik'][0]
                                    if 'winbox' in remote_results and not mikrotik_version:
                                        mikrotik_version = remote_results['winbox'][0]
                            except Exception:
                                pass

                        mikrotik_version = self.probe_mikrotik_web(ip)
                        grandstream_model = self.probe_grandstream_web(ip)
                        
                        # Додатково витягуємо версію MikroTik з FTP банера (якщо Web закритий, а MNDP не пройшов)
                        if not mikrotik_version and banners:
                            for p, b in banners.items():
                                if 'mikrotik' in b.lower():
                                    m = re.search(r'(?i)MikroTik\s+([678]\.[\w\.\-]+)', b)
                                    if m: mikrotik_version = f"RouterOS {m.group(1)}"; break

                        # Якщо web-проба не дала результат, спробуємо MNDP або Winbox банер
                        if not mikrotik_version:
                            if mndp_info and 'routeros' in mndp_info.lower():
                                mikrotik_version = mndp_info
                            else:
                                winbox_info = self.probe_winbox_banner(ip)
                                if winbox_info:
                                    mikrotik_version = winbox_info

                        # Глибокий пошук моделі Grandstream, якщо web-проба не спрацювала
                        if not grandstream_model:
                            if sip_info and 'grandstream' in sip_info.lower():
                                gs_parts = [s.split(': ', 1)[1] for s in sip_info.split(' | ') if ': ' in s and 'grandstream' in s.lower()]
                                if gs_parts: grandstream_model = gs_parts[0]
                            # Резервний пошук в HTTP банерах (якщо закритий SIP)
                            if not grandstream_model and banners:
                                for p, b in banners.items():
                                    if 'grandstream' in b.lower() or 'ucm' in b.lower() or 'gxp' in b.lower():
                                        m = re.search(r'(?i)Server:\s*([^\s\]\[]+.*?)(?:\s+Powered-By|$|\[)', b)
                                        if m: grandstream_model = m.group(1).strip(); break
                        
                        # Відновлюємо статус відкритих портів, якщо HTTP-проби змогли пробити Firewall
                        for p in list(banners.keys()):
                            if p not in open_ports_only_numbers:
                                open_ports_only_numbers.append(p)
                                for i, (op_p, _) in enumerate(open_ports):
                                    if op_p == p:
                                        open_ports[i] = (p, "open")
                                        break
                                else:
                                    open_ports.append((p, "open"))

                        if is_aggressive and 21 in open_ports_only_numbers:
                            ftp_anon = self.check_ftp_anonymous(ip)
                            
                    # Витягуємо ім'я хоста з заголовків Web-серверів (HTTP Title)
                    http_title_name = ""
                    for p, banner in banners.items():
                        title_match = re.search(r'\[(.*?)\]', banner)
                        if title_match:
                            possible_title = title_match.group(1).strip()
                            if len(possible_title) < 30 and not any(x in possible_title.lower() for x in ['login', 'index', 'admin', 'auth', 'welcome', '404', 'error', 'page', 'dashboard', 'router', 'gateway']):
                                http_title_name = possible_title
                                break
                    
                    versions_found = []
                    if mndp_info and mndp_info != "MikroTik (MNDP)": versions_found.append(mndp_info)
                    if mikrotik_version and mikrotik_version not in mndp_info: versions_found.append(mikrotik_version)
                    if grandstream_model: 
                        if not grandstream_model.lower().startswith('grandstream'): grandstream_model = f"Grandstream {grandstream_model}"
                        versions_found.append(grandstream_model)
                    if sip_info:
                        clean_sip = [s.split(': ', 1)[1] for s in sip_info.split(' | ') if ': ' in s]
                        if clean_sip: versions_found.append(f"SIP: {' / '.join(clean_sip)[:80]}")
                    if snmp_info and "SNMP Відкритий" not in snmp_info: versions_found.append(f"SNMP: {snmp_info.strip()}")
                    if upnp_info: versions_found.append(f"UPnP: {upnp_info.strip()}")
                    versions_found.extend(banners.values())
                    versions_found = sorted(list(set(filter(None, versions_found))))
                    versions_str = "\n".join(versions_found)

                    device_type = self.analyze_device_type(vendor, open_ports_only_numbers, banners, ttl, netbios_name, sip_info, snmp_info, upnp_info, ssl_name, mdns_info, mikrotik_version, grandstream_model, dns_name, mndp_info, is_smbv1)
                    
                    vulns, exploit = self.analyze_vulnerabilities(open_ports_only_numbers, banners, snmp_info, upnp_info, ftp_anon, device_type, mndp_info, is_smbv1, axfr_result, versions_str)
                    
                    open_list = []
                    closed_list = []
                    filtered_list = []
                    for p, status in open_ports:
                        if status == 'open': open_list.append(f"{p}({status})")
                        elif status == 'closed': closed_list.append(f"{p}({status})")
                        else: filtered_list.append(f"{p}({status})")
                        
                    if sip_info:
                        for sip_port in [5060, 5061, 5080]:
                            if f"Port {sip_port}" in sip_info:
                                open_list.append(f"{sip_port}/udp(open)")
                    if snmp_info: open_list.append("161/udp(open)")
                    if mdns_info: open_list.append("5353/udp(open)")
                    if mndp_info: open_list.append("5678/udp(open)")
                    
                    ports_info = open_list + closed_list + filtered_list
                    
                    # Збір та фільтрація всіх знайдених імен хоста
                    hostnames_found = []
                    hostnames_found = []
                    if dns_name: hostnames_found.append(dns_name)
                    if netbios_name and netbios_name != dns_name: hostnames_found.append(netbios_name)
                    if mdns_hostname and mdns_hostname not in hostnames_found: hostnames_found.append(mdns_hostname)
                    if llmnr_name and llmnr_name not in hostnames_found: hostnames_found.append(llmnr_name)
                    if wsd_hostname and wsd_hostname not in hostnames_found: hostnames_found.append(wsd_hostname)
                    if upnp_hostname and upnp_hostname not in hostnames_found: hostnames_found.append(upnp_hostname)
                    if snmp_hostname and snmp_hostname not in hostnames_found: hostnames_found.append(snmp_hostname)
                    if mndp_identity and mndp_identity not in hostnames_found: hostnames_found.append(mndp_identity)
                    if ssl_name and ssl_name not in hostnames_found: hostnames_found.append(ssl_name)
                    if http_title_name and http_title_name not in hostnames_found: hostnames_found.append(http_title_name)

                    # Вибираємо найкращий хостнейм серед доступних джерел
                    preferred = self.select_preferred_hostname(dns_name, netbios_name, mdns_hostname, llmnr_name, wsd_hostname, upnp_hostname, snmp_hostname, mndp_identity, ssl_name, http_title_name)
                    if preferred:
                        final_hostname = preferred
                    else:
                        final_hostname = " / ".join(hostnames_found) if hostnames_found else "-"

                    # Фільтрація: якщо стоїть галочка "Тільки відкриті", а відкритих портів немає - пропускаємо хост
                    if only_open and not open_list and not is_stealth:
                        return

                    if not is_stealth and not is_ping_up and not has_l4_response and not has_firewall_bypass and is_in_arp:
                        ports_str = "Привид (Тільки старий запис у ARP-кеші)"
                    else:
                        ports_str = ", ".join(ports_info) if ports_info else ("Живий (Закриті порти)" if not is_stealth else "Живий (Тихий режим)")

                    # Додавання в таблицю: всі хости, включаючи ті, що були лише в ARP-кеші
                        
                    self.root.after(0, self.insert_row, ip, mac, final_hostname, vendor, device_type, versions_str, ports_str, vulns, exploit)
                    self.log(f"Профіль складено для {ip} -> {device_type}", "success", from_thread=True)
            except Exception as e:
                self.log(f"Критична помилка потоку для {ip}: {e}", "error", from_thread=True)

        max_workers = 200 if is_remote else 50
        if is_careful:
            max_workers = 2 # Ультра-мінімальна кількість для повного обходу Network Protection (ESET)
        # For remote scans, allow higher parallelism but process in chunks to avoid floods
        if is_remote and len(hosts) > 512:
            chunk_size = 256
            for i in range(0, len(hosts), chunk_size):
                if self.stop_event.is_set(): break
                chunk = hosts[i:i+chunk_size]
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    executor.map(check_host, chunk)
                # Gentle pause between chunks to reduce blast-rate
                time.sleep(1.0)
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                executor.map(check_host, hosts)
            
        self.root.after(0, self.finish_scan)
        
    def ping_ip(self, ip):
        sys_os = platform.system().lower()
        if sys_os == 'windows':
            cmd = ['ping', '-n', '1', '-w', '1500', ip]
        elif sys_os == 'darwin':
            cmd = ['ping', '-c', '1', '-t', '1', ip]
        else:
            cmd = ['ping', '-c', '1', '-W', '1', ip]
        try:
            # Читаємо вивід ping для витягування TTL (Рідний OS Fingerprinting)
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, encoding='cp866' if sys_os=='windows' else 'utf-8', errors='ignore')
            ttl_match = re.search(r'[Tt][Tt][Ll]=(\d+)', output)
            ttl = int(ttl_match.group(1)) if ttl_match else None
            return True, ttl
        except:
            return False, None

    def get_mac_from_arp(self, ip):
        # 1. Спробуємо отримати MAC з системного кешу (швидко)
        try:
            if platform.system().lower() == 'windows':
                output = subprocess.check_output(['arp', '-a', ip], encoding='cp866', errors='ignore')
            else:
                output = subprocess.check_output(['arp', '-n', ip], encoding='utf-8', errors='ignore')
            
            match = re.search(r"([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})", output)
            if match:
                return match.group(0).upper().replace('-', ':')
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # 2. Якщо в кеші немає, робимо прямий запит через Scapy (найнадійніше)
        if 'srp' in globals():
            try:
                srp_kwargs = {}
                if self.scan_iface_name:
                    srp_kwargs['iface'] = self.scan_iface_name
                ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=1, verbose=False, **srp_kwargs)
                if ans:
                    return ans[0][1].hwsrc.upper()
            except Exception:
                pass # Scapy може не спрацювати

        return "Не знайдено"

    def get_vendor_by_mac(self, mac):
        if not mac or mac == "Не знайдено":
            return "Невідомо"

        # 1. Перевірка на Рандомізовану (Stealth) MAC-адресу
        try:
            first_byte_hex = mac[:2]
            first_byte = int(first_byte_hex, 16)
            # Якщо встановлено "Locally Administered Bit" (другий біт = 1), це фейкова адреса
            if first_byte & 2:
                # Перевіряємо на стандартний патерн рандомізації (Windows/Android/iOS)
                if first_byte_hex[1].upper() in ['2', '6', 'A', 'E']:
                    return "Прихована MAC (Стандартна рандомізація)"
                return "Прихована MAC (Нестандартна рандомізація)"
        except:
            pass

        if mac in self.mac_cache:
            return self.mac_cache[mac]

        # Перевірка локальної бази (OUI) для швидкості
        prefix = mac[:8].upper()
        if prefix in self.COMMON_VENDORS:
            self.mac_cache[mac] = self.COMMON_VENDORS[prefix]
            return self.COMMON_VENDORS[prefix]

        # Якщо локально немає, обережно стукаємо в API (запобігання бану IP)
        try:
            with self.api_lock: # Блокуємо інші потоки, щоб не отримати HTTP 429 Too Many Requests
                url = f"https://api.maclookup.app/v2/macs/{mac}/company/name"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=2) as response:
                    resp_str = response.read().decode('utf-8').strip()
                    vendor = resp_str if resp_str and "*NO COMPANY*" not in resp_str else "Невідомий виробник"
                time.sleep(0.5) # Пауза щоб API сервер нас не забанив
                self.mac_cache[mac] = vendor
                return vendor
        except:
            # Фоллбек якщо немає інтернету або API лежить
            self.mac_cache[mac] = "Невідомий виробник"
            return "Невідомий виробник"

    def fast_port_scan(self, ip, mode="Стандартне", custom_ports=None, socket_timeout: Optional[float] = None) -> List[Tuple[int, str]]:
        if "Тихе" in mode:
            return []

        ports_to_scan = []
        if "Кастомне" in mode:
            # Для кастомного режиму використовуються ТІЛЬКИ вказані порти
            if custom_ports:
                ports_to_scan = custom_ports
            else:
                return [] # Безпечний вихід, якщо порти не передано
        elif "Агресивне" in mode:
            ports_to_scan = [
                21, 22, 23, 25, 53, 80, 81, 110, 111, 135, 139, 143, 443, 445, 515, 548, 554, 591, 631, 993, 995,
                1433, 1521, 1723, 1883, 2000, 2049, 3306, 3389, 4899, 5000, 5060, 5355, 5432, 5900, 5985, 5986,
                6379, 7000, 8000, 8008, 8080, 8081, 8096, 8291, 8443, 8883, 8888, 8920, 9090, 9100, 9200, 9300,
                10000, 27017, 32400
            ]
        elif "Обережне" in mode:
            ports_to_scan = [80, 443, 445, 5060, 8291] # Тільки ТОП-5 критичних портів. ESET блокує довгі перебори
        else: # Стандартний режим
            ports_to_scan = [21, 22, 23, 53, 80, 111, 135, 139, 443, 445, 554, 3306, 3389, 5000, 5060, 5432, 5900, 8080, 8089, 8291, 8443]

        is_standard = "Стандартне" in mode
        is_careful = "Обережне" in mode
        if is_standard or is_careful:
            # Рандомізуємо порядок портів, щоб обійти сигнатури секвентального сканування ESET
            random.shuffle(ports_to_scan)

        scanned_ports_with_status = []
        for port in ports_to_scan:
            if self.stop_event.is_set(): break
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    to = socket_timeout if socket_timeout is not None else 1.0
                    s.settimeout(to) # Збільшуємо таймаут для віддалених хостів, якщо вказано
                    # Якщо вибрано локальний інтерфейс, біндимося на його IP, щоб уникнути відповідей з інших адаптерів
                    try:
                        if getattr(self, 'scan_iface_ip', None):
                            s.bind((self.scan_iface_ip, 0))
                    except Exception:
                        pass
                    result = s.connect_ex((ip, port))
                    if result == 0:
                        scanned_ports_with_status.append((port, "open"))
                    elif result == errno.ECONNREFUSED: # Connection refused (port closed)
                        scanned_ports_with_status.append((port, "closed"))
                    else: # Other errors like timeout, host unreachable, etc.
                        scanned_ports_with_status.append((port, "filtered"))
            except OSError as e:
                self.log(f"Помилка сокета при скануванні {ip}:{port} - {e}", "debug", from_thread=True)
                scanned_ports_with_status.append((port, "error"))
                
            # Випадкова затримка між запитами на порти
            if is_careful and not self.stop_event.is_set():
                time.sleep(random.uniform(0.5, 1.5)) # Обережна пауза, що імітує роботу браузера
            elif is_standard and not self.stop_event.is_set():
                time.sleep(random.uniform(0.2, 0.7))
                
        return scanned_ports_with_status

    def remote_service_probes(self, ip: str, open_ports: List[Tuple[int, str]], is_aggressive: bool, socket_timeout: float = 2.0) -> Dict[str, Any]:
        """Run deep remote-suitable probes: reverse DNS, SSL cert names, HTTP/other banners, SNMP, MikroTik/Winbox."""
        results = {}
        # Reverse DNS
        try:
            rd = self.get_reverse_dns(ip)
            if rd:
                results.setdefault('hostnames', []).append(('ptr', rd))
        except Exception:
            pass

        # Deep banner grab (HTTP, SSH, FTP, SMTP, etc.)
        try:
            open_ports_only = [p for p, s in open_ports]
            banners = self.grab_deep_banners(ip, open_ports_only)
            if banners:
                results['banners'] = banners
        except Exception:
            pass

        # SSL cert names from known TLS ports
        try:
            ssl_name = self.get_ssl_cert_name(ip, open_ports_only if 'open_ports_only' in locals() else [])
            if ssl_name:
                results.setdefault('ssl_cn', []).append(ssl_name)
        except Exception:
            pass

        # SNMP probe (only if aggressive)
        if is_aggressive:
            try:
                snmp_info, snmp_hostname = self.probe_snmp(ip)
                if snmp_info:
                    results.setdefault('snmp', []).append(snmp_info)
                if snmp_hostname:
                    results.setdefault('hostnames', []).append(('snmp', snmp_hostname))
            except Exception:
                pass

        # MikroTik / Winbox detection if port 8291 open
        try:
            if any(p == 8291 for p, _ in open_ports):
                mndp_info, mndp_identity = self.probe_mikrotik_mndp(ip)
                if mndp_identity:
                    results.setdefault('mikrotik', []).append(mndp_identity)
                wb = self.probe_winbox_banner(ip)
                if wb:
                    results.setdefault('winbox', []).append(wb)
        except Exception:
            pass

        return results

    def get_netbios_name(self, ip):
        """Хак: Відправляє сирий UDP NBNS запит для отримання імені Windows ПК без авторизації"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(1.0) # Збільшено час очікування для Wi-Fi
                # Якщо відомий IP локального інтерфейсу — прив'язуємо сокет
                try:
                    if getattr(self, 'scan_iface_ip', None):
                        s.bind((self.scan_iface_ip, 0))
                except Exception:
                    pass
                # Магічний Payload: Node Status Request (Wildcard)
                payload = b'\x81\x04\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x20\x43\x4b\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x00\x00\x21\x00\x01'
                s.sendto(payload, (ip, 137))
                data, _ = s.recvfrom(1024)
                
                # Розумний парсинг списку імен у відповіді
                if len(data) > 56:
                    num_names = data[56]
                    offset = 57
                    for _ in range(num_names):
                        if offset + 18 > len(data): break
                        name_bytes = data[offset:offset+15]
                        name_type = data[offset+15]
                        # Тип 0x00 (Workstation) або 0x20 (File Server) містять реальне ім'я ПК
                        if name_type in (0x00, 0x20):
                            name = name_bytes.decode('ascii', errors='ignore').replace('\x00', '').strip()
                            if name and not all(c == '\x00' for c in name) and name != "__MSBROWSE__":
                                return name
                        offset += 18
        except:
            pass
        return ""

    def get_mdns_hostname(self, ip):
        """Робить зворотний mDNS запит (PTR) для отримання імені хоста (Apple/Linux/Win10+)"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(1.0)
                try:
                    if getattr(self, 'scan_iface_ip', None):
                        s.bind((self.scan_iface_ip, 0))
                except Exception:
                    pass
                parts = ip.split('.')
                rev_ip = f"{parts[3]}.{parts[2]}.{parts[1]}.{parts[0]}.in-addr.arpa"
                
                header = b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
                qname = b''.join(bytes([len(p)]) + p.encode() for p in rev_ip.split('.')) + b'\x00'
                qtype_qclass = b'\x00\x0c\x80\x01'
                
                s.sendto(header + qname + qtype_qclass, ('224.0.0.251', 5353))
                s.sendto(header + qname + qtype_qclass, (ip, 5353)) # Unicast fallback
                
                data, _ = s.recvfrom(1024)
                idx = data.find(b'\x05local')
                if idx > 0:
                    for i in range(1, 64):
                        if idx - i - 1 >= 0 and data[idx - i - 1] == i:
                            return data[idx - i:idx].decode('utf-8', errors='ignore')
        except:
            pass
        return ""

    def get_llmnr_name(self, ip):
        """Робить LLMNR запит (UDP 5355), на який завжди відповідають сучасні Windows (10/11)"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(1.0)
                try:
                    if getattr(self, 'scan_iface_ip', None):
                        s.bind((self.scan_iface_ip, 0))
                except Exception:
                    pass
                parts = ip.split('.')
                rev_ip = f"{parts[3]}.{parts[2]}.{parts[1]}.{parts[0]}.in-addr.arpa"
                
                # LLMNR Запит (Transaction ID 0, Standard Query)
                header = b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
                qname = b''.join(bytes([len(p)]) + p.encode() for p in rev_ip.split('.')) + b'\x00'
                qtype_qclass = b'\x00\x0c\x00\x01' # PTR запит
                
                s.sendto(header + qname + qtype_qclass, (ip, 5355))
                data, _ = s.recvfrom(1024)
                
                # Шукаємо всі ASCII послідовності в бінарній відповіді, схожі на імена ПК
                strings = re.findall(b'[a-zA-Z0-9-]{3,}', data[len(header):])
                for s_bytes in strings:
                    decoded = s_bytes.decode('utf-8', errors='ignore')
                    if decoded.lower() not in ('in-addr', 'arpa', 'local') and not decoded.isdigit():
                        return decoded # Повертає знайдене ім'я комп'ютера
        except:
            pass
        return ""

    def probe_wsd(self, ip):
        """Відправляє WSD (Web Services Discovery) запит на порт 3702. Ідеально для сучасних Windows 10/11."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(0.5)
                try:
                    if getattr(self, 'scan_iface_ip', None):
                        s.bind((self.scan_iface_ip, 0))
                except Exception:
                    pass
                msg = (
                    '<?xml version="1.0" encoding="utf-8" ?>'
                    '<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:wsd="http://schemas.xmlsoap.org/ws/2005/04/discovery">'
                    '<env:Header>'
                    '<wsa:To>urn:schemas-xmlsoap-org:ws:2004:08:addressing:role:discovery</wsa:To>'
                    '<wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>'
                    '<wsa:MessageID>urn:uuid:11111111-2222-3333-4444-555555555555</wsa:MessageID>'
                    '</env:Header>'
                    '<env:Body>'
                    '<wsd:Probe/>'
                    '</env:Body>'
                    '</env:Envelope>'
                )
                s.sendto(msg.encode(), (ip, 3702))
                data, _ = s.recvfrom(2048)
                text = data.decode('utf-8', errors='ignore')
                match = re.search(r'(?i)<[^:]*:(?:Computer|HostName|FriendlyName)[^>]*>([^<]+)</', text)
                if match:
                    return match.group(1).strip()
        except: pass
        return ""

    def grab_deep_banners(self, ip, open_ports):
        """Глибокий збір інформації з відкритих портів (SSH, FTP, HTTP тощо)"""
        banners = {}
        # Примусово додаємо 80 і 443 для HTTP банерів в обхід блокувань ESET
        ports_to_check = set(open_ports)
        ports_to_check.update([80, 443])
        
        for port in ports_to_check:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # Bind to interface IP if available to avoid responses via other adapters
                    try:
                        if getattr(self, 'scan_iface_ip', None):
                            s.bind((self.scan_iface_ip, 0))
                    except Exception:
                        pass
                    s.settimeout(1.0)
                    if port in [443, 8443]:
                        ctx = ssl.create_default_context()
                        ctx.check_hostname = False
                        ctx.verify_mode = ssl.CERT_NONE
                        s = ctx.wrap_socket(s, server_hostname=ip)

                    s.connect((ip, port))
                    
                    # Для Web-серверів відправляємо GET запит, щоб витягнути <title> (як це робить AIPS)
                    if port in [80, 443, 8080, 8443]:
                        s.sendall(f"GET / HTTP/1.1\r\nHost: {ip}\r\nConnection: close\r\nUser-Agent: Mozilla/5.0\r\n\r\n".encode())
                        data = b""
                        try:
                            while True:
                                chunk = s.recv(1024)
                                if not chunk: break
                                data += chunk
                                if len(data) > 8192: break # Не качаємо весь сайт, тільки початок
                        except: pass
                        
                        text = data.decode('utf-8', errors='ignore')
                        title_match = re.search(r'(?i)<title[^>]*>(.*?)</title>', text, re.DOTALL)
                        server_match = re.search(r'(?i)server:\s*([^\r\n]+)', text)
                        powered_match = re.search(r'(?i)x-powered-by:\s*([^\r\n]+)', text)
                        
                        parts = []
                        if server_match: parts.append(f"Server: {server_match.group(1).strip()}")
                        if powered_match: parts.append(f"Powered-By: {powered_match.group(1).strip()}")
                        if title_match: 
                            title = title_match.group(1).strip().replace('\n', '').replace('\r', '')
                            if title: parts.append(f'[{title}]')
                            
                        if parts:
                            banners[port] = " ".join(parts)[:75]
                    else:
                        # Для SSH, FTP, SMTP просто читаємо вітання
                        data = s.recv(1024).decode('utf-8', errors='ignore').strip()
                        if data:
                            banners[port] = data.split('\n')[0].strip()[:100]
            except:
                pass
        return banners
        
    def get_ssl_cert_name(self, ip, ports):
        """Витягує ім'я хоста з SSL сертифікатів (Особливо потужно для 3389 RDP)"""
        ports_to_check = set(ports)
        ports_to_check.update([443, 8443, 3389, 465, 993])
        for port in (443, 8443, 3389, 465, 993):
            if port not in ports_to_check:
                continue
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if getattr(self, 'scan_iface_ip', None):
                    try:
                        sock.bind((self.scan_iface_ip, 0))
                    except Exception:
                        pass
                sock.settimeout(0.8)
                sock.connect((ip, port))
                with ctx.wrap_socket(sock, server_hostname=ip) as ssock:
                    cert = ssock.getpeercert()
                    if cert:
                        for sub in cert.get('subject', []):
                            if sub and sub[0][0] == 'commonName':
                                cn = sub[0][1]
                                if cn and not cn.startswith('localhost') and not cn.replace('.','').isdigit():
                                    return cn
            except Exception:
                # ignore and try next port
                pass
            finally:
                try:
                    if sock:
                        sock.close()
                except Exception:
                    pass
        return ""

    def get_reverse_dns(self, ip):
        """Пробує отримати PTR (reverse DNS) для IP з таймаутом.
        Спочатку через dnspython (якщо встановлено), інакше через socket.gethostbyaddr
        виконаний у воркер-потоці з обмеженим таймаутом, щоб не блокувати потік сканера."""
        # Спроба через dnspython
        if 'dns' in globals():
            try:
                rev_name = dns.reversename.from_address(ip)
                ans = dns.resolver.resolve(rev_name, 'PTR', lifetime=1.0)
                if ans:
                    name = str(ans[0]).rstrip('.')
                    return name
            except Exception:
                pass

        # Фолбек на socket.gethostbyaddr з таймаутом
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(socket.gethostbyaddr, ip)
                try:
                    result = fut.result(timeout=1.0)
                    if result and result[0]:
                        return result[0]
                except Exception:
                    pass
        except Exception:
            pass
        return ""

    def normalize_hostname(self, name: str) -> str:
        """Нормалізує імя хоста: видаляє кінцеві крапки, локальні домени і зайві пробіли."""
        if not name:
            return ""
        try:
            n = name.strip()
            if n.endswith('.'):
                n = n[:-1]
            # Видаляємо .local та інші очевидні локальні домени
            n = re.sub(r"\.(local|lan|home|internal)$", '', n, flags=re.I)
            return n
        except Exception:
            return name

    def select_preferred_hostname(self, dns_name, netbios_name, mdns_hostname, llmnr_name, wsd_hostname, upnp_hostname, snmp_hostname, mndp_identity, ssl_name, http_title_name):
        """Вибирає найкращий hostname серед доступних джерел за пріоритетом.

        Пріоритет (в порядку): NetBIOS (Windows), LLMNR, reverse DNS, SSL CN, mDNS, WSD, UPnP, SNMP, MNDP, HTTP Title
        Повертає перший валідний результат, або порожній рядок.
        """
        # Нормалізуємо всі вхідні імена
        candidates = {
            'netbios': self.normalize_hostname(netbios_name),
            'llmnr': self.normalize_hostname(llmnr_name),
            'dns': self.normalize_hostname(dns_name),
            'ssl': self.normalize_hostname(ssl_name),
            'mdns': self.normalize_hostname(mdns_hostname),
            'wsd': self.normalize_hostname(wsd_hostname),
            'upnp': self.normalize_hostname(upnp_hostname),
            'snmp': self.normalize_hostname(snmp_hostname),
            'mndp': self.normalize_hostname(mndp_identity),
            'http': self.normalize_hostname(http_title_name),
        }

        # Prioritize NetBIOS for Windows hostnames (often contains computer name)
        order = ['netbios', 'llmnr', 'dns', 'ssl', 'mdns', 'wsd', 'upnp', 'snmp', 'mndp', 'http']
        for key in order:
            val = candidates.get(key)
            if val and len(val) > 1 and not val.isdigit():
                return val
        return ""

    def check_ftp_anonymous(self, ip):
        """Перевіряє можливість анонімного входу на FTP (порт 21)"""
        try:
            with socket.create_connection((ip, 21), timeout=1.5) as s:
                s.recv(1024)
                s.sendall(b"USER anonymous\r\n")
                resp = s.recv(1024).decode(errors='ignore')
                if "331" in resp or "230" in resp:
                    s.sendall(b"PASS anonymous@example.com\r\n")
                    resp = s.recv(1024).decode(errors='ignore')
                    if "230" in resp: return True
        except: pass
        return False

    def probe_sip(self, ip):
        """Відправляє SIP OPTIONS запит (поведінка svmap) для ідентифікації IP-телефонів та АТС"""
        found_sip_services = []

        # Динамічно отримуємо IP-адресу нашого сканера для правильних заголовків Via та Contact
        local_ip = "192.168.1.100"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as temp_s:
                # Якщо відомий IP інтерфейсу — використаємо його для коректних Via/Contact
                if getattr(self, 'scan_iface_ip', None):
                    try:
                        temp_s.bind((self.scan_iface_ip, 0))
                    except Exception:
                        pass
                else:
                    try:
                        temp_s.connect((ip, 53))
                    except Exception:
                        pass
                local_ip = temp_s.getsockname()[0]
        except: pass

        for port in [5060, 5061, 5062, 5080]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.settimeout(1.0)
                    # Прив'язуємо сокет, щоб отримати реальний порт для зворотного зв'язку (як це робить svmap)
                    try:
                        if getattr(self, 'scan_iface_ip', None):
                            s.bind((self.scan_iface_ip, 0))
                        else:
                            s.bind(('', 0))
                    except Exception:
                        try:
                            s.bind(('', 0))
                        except:
                            pass
                    actual_port = s.getsockname()[1]

                    # Ідеальний SIP OPTIONS запит. Додано ;rport та фактичний порт для гарантованої відповіді від АТС/Телефонів
                    msg = f"OPTIONS sip:100@{ip}:{port} SIP/2.0\r\nVia: SIP/2.0/UDP {local_ip}:{actual_port};branch=z9hG4bK-svmap;rport\r\nMax-Forwards: 70\r\nTo: <sip:100@{ip}:{port}>\r\nFrom: <sip:scanner@{local_ip}:{actual_port}>;tag=1928301774\r\nCall-ID: a84b4c76e66710\r\nCSeq: 1 OPTIONS\r\nContact: <sip:scanner@{local_ip}:{actual_port}>\r\nUser-Agent: svmap\r\nAccept: application/sdp\r\nContent-Length: 0\r\n\r\n"
                    s.sendto(msg.encode(), (ip, port))
                    data, _ = s.recvfrom(2048)
                    if b"SIP/2.0" in data:
                        text_data = data.decode('utf-8', errors='ignore')
                        server_val, ua_val = "", ""
                        for line in text_data.split('\r\n'):
                            if line.lower().startswith('server:'): server_val = line[7:].strip()
                            elif line.lower().startswith('user-agent:'): ua_val = line[11:].strip()
                        best_info = ua_val if len(ua_val) > len(server_val) else server_val
                        if best_info:
                            found_sip_services.append(f"Port {port}: {best_info}")
            except:
                pass
        return " | ".join(found_sip_services) if found_sip_services else ""

    def probe_winbox_banner(self, ip):
        """Проста перевірка порту Winbox (8291) — читаємо будь-який банер або ascii-рядки.
        Це не реалізує повний Winbox handshake, але часто дозволяє отримати модель/версію,
        якщо сервіс повертає інформацію при підключенні або у відповіді на негайне recv()."""
        try:
            with socket.create_connection((ip, 8291), timeout=1.0) as s:
                s.settimeout(0.8)
                try:
                    data = s.recv(1024)
                except Exception:
                    data = b''
                if data:
                    text = data.decode('utf-8', errors='ignore')
                    # common markers to look for
                    m = re.search(r'(?i)(routeros)\s*v?([0-9]+(\.[0-9]+)+)', text)
                    if m:
                        return f"RouterOS {m.group(2)}"
                    # Try to find model-like strings
                    m2 = re.search(r'([A-Za-z0-9_-]{3,}\s*\d{1,4}\w?)', text)
                    if m2:
                        return m2.group(1).strip()
        except Exception:
            pass
        return ""
    

    def probe_snmp(self, ip):
        """Хак: Відправляє SNMPv1 GetRequest для витягування моделі та імені хоста (sysName)"""
        snmp_info = ""
        snmp_hostname = ""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(0.5)
                # Запит sysDescr.0 (1.3.6.1.2.1.1.1.0) з community 'public'
                req = b'\x30\x29\x02\x01\x00\x04\x06\x70\x75\x62\x6c\x69\x63\xa0\x1c\x02\x04\x00\x00\x00\x01\x02\x01\x00\x02\x01\x00\x30\x0e\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x01\x00\x05\x00'
                s.sendto(req, (ip, 161))
                data, _ = s.recvfrom(1024)
                if len(data) > 30:
                    strings = re.findall(b'[ -~\r\n]{10,}', data)
                    if strings:
                        longest = max(strings, key=len).decode('ascii', errors='ignore')
                        snmp_info = longest.strip().replace('\r\n', ' ')
                    else:
                        snmp_info = "SNMP Відкритий"
                
                # Запит sysName.0 (Hostname принтера / роутера)
                req_name = b'\x30\x29\x02\x01\x00\x04\x06\x70\x75\x62\x6c\x69\x63\xa0\x1c\x02\x04\x00\x00\x00\x02\x02\x01\x00\x02\x01\x00\x30\x0e\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x05\x00\x05\x00'
                s.sendto(req_name, (ip, 161))
                data2, _ = s.recvfrom(1024)
                if len(data2) > 30:
                    strings = re.findall(b'[ -~]{3,}', data2[-50:])
                    if strings:
                        snmp_hostname = max(strings, key=len).decode('ascii', errors='ignore').strip()
        except:
            pass
        return snmp_info, snmp_hostname

    def probe_upnp(self, ip):
        """Хак: Відправляє SSDP запит, знаходить XML конфіг і читає точну назву заліза та ім'я (FriendlyName)"""
        upnp_info = ""
        upnp_hostname = ""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(0.5)
                msg1 = f'M-SEARCH * HTTP/1.1\r\nHost: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nST: ssdp:all\r\nMX: 1\r\n\r\n'
                msg2 = f'M-SEARCH * HTTP/1.1\r\nHost: {ip}:1900\r\nMAN: "ssdp:discover"\r\nST: ssdp:all\r\nMX: 1\r\n\r\n'
                s.sendto(msg1.encode(), (ip, 1900))
                s.sendto(msg2.encode(), (ip, 1900)) # Дублюємо запит для хитрих пристроїв (Smart TV)
                data, _ = s.recvfrom(1024)
                text = data.decode('utf-8', errors='ignore')
                
                upnp_parts = []
                # Спочатку забираємо заголовок Server, який містить версії ОС (напр. Linux/2.6, UPnP/1.0, MiniUPnPd/1.5)
                server_match = re.search(r'(?i)Server:\s*([^\r\n]+)', text)
                if server_match:
                    upnp_parts.append(f"Server: {server_match.group(1).strip()}")

                # Спробуємо знайти та завантажити XML конфіг
                loc_match = re.search(r'(?i)Location:\s*(http://[^\s]+)', text)
                if loc_match:
                    xml_url = loc_match.group(1).strip()
                    req = urllib.request.Request(xml_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=1.5) as response:
                        xml_data = response.read().decode('utf-8', errors='ignore')
                        model = re.search(r'<modelName>(.*?)</modelName>', xml_data)
                        model_num = re.search(r'<modelNumber>(.*?)</modelNumber>', xml_data)
                        vendor_xml = re.search(r'<manufacturer>(.*?)</manufacturer>', xml_data)
                        fname = re.search(r'<friendlyName>(.*?)</friendlyName>', xml_data)
                        
                        if fname: upnp_hostname = fname.group(1).strip()
                        
                        hw_info = ""
                        if vendor_xml and model: hw_info = f"{vendor_xml.group(1)} {model.group(1)}"
                        elif model: hw_info = model.group(1)
                        if hw_info and model_num and model_num.group(1) not in hw_info: hw_info += f" {model_num.group(1)}"
                        if hw_info: upnp_parts.append(hw_info)
                        
                if upnp_parts:
                    upnp_info = " | ".join(upnp_parts)
        except:
            pass
        return upnp_info, upnp_hostname

    def probe_mdns(self, ip):
        """Відправляє mDNS запит для розпізнавання пристроїв Apple, Chromecast, IoT"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(0.5)
                query = b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x09_services\x07_dns-sd\x04_udp\x05local\x00\x00\x0c\x00\x01'
                s.sendto(query, (ip, 5353))
                data, _ = s.recvfrom(1024)
                if data:
                    strings = re.findall(b'[ -~]{5,}', data)
                    clean_str = " ".join([st.decode(errors='ignore') for st in strings])
                    return clean_str
        except: pass
        return ""

    def probe_mikrotik_web(self, ip):
        """Витягує точну версію RouterOS через Web-інтерфейс (HTTP/HTTPS) навіть якщо порт заблоковано сканером"""
        for port in [80, 443, 8080]:
            protocol = "https" if port == 443 else "http"
            url = f"{protocol}://{ip}:{port}" if port not in [80, 443] else f"{protocol}://{ip}"
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, context=ctx, timeout=1.5) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                    
                    # Шукаємо версію в title (дуже часто зустрічається в нових RouterOS v7)
                    title_m = re.search(r'<title>.*?v([678]\.[\w\.\-]+).*?</title>', html, re.IGNORECASE)
                    if title_m: return f"RouterOS {title_m.group(1)}"
                    
                    # Універсальний пошук для старих та нових версій (підтримує rc, beta, testing, v8)
                    match = re.search(r'(?i)RouterOS\s*v?([678]\.[\w\.\-]+)', html)
                    if match:
                        return f"RouterOS {match.group(1)}"
                        
                    # Резервний парсинг версії для прошивок RouterOS 7.x / 8.x (з глибини HTML тегів)
                    match_v7 = re.search(r'>\s*v?([678]\.[\w\.\-]+)\s*<', html)
                    if match_v7 and "mikrotik" in html.lower():
                        return f"RouterOS {match_v7.group(1)}"
            except:
                pass
        return ""

    def probe_grandstream_web(self, ip):
        """Витягує точну модель та версію прошивки пристроїв Grandstream з Web-інтерфейсу"""
        for port in [80, 443, 8080, 8089]:
            protocol = "https" if port in [443, 8089] else "http"
            url = f"{protocol}://{ip}:{port}" if port not in [80, 443] else f"{protocol}://{ip}"
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, context=ctx, timeout=1.5) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                    server_header = response.headers.get('Server', '')
                    
                    model_match = re.search(r'(?i)(GXP\d+|HT\d+|UCM\d+|GXV\d+|DP\d+|GWN\d+|HT-\d+)', html)
                    fw_match = re.search(r'(?i)(?:Firmware|Software|Prog)\s*(?:Version)?[\s:]+([\d\.]+)', html)
                    
                    if model_match and fw_match:
                        return f"Grandstream {model_match.group(1).upper()} (FW: {fw_match.group(1)})"
                    elif fw_match and ("Grandstream" in html or "Grandstream" in server_header):
                        return f"Grandstream (FW: {fw_match.group(1)})"
                    elif 'Grandstream' in server_header:
                        return server_header.strip()
            except:
                pass
        return ""

    def probe_mikrotik_mndp(self, ip):
        """Відправляє специфічний UDP-пакет на порт 5678 (MikroTik MNDP) і витягує інформацію"""
        mndp_info = ""
        mndp_identity = ""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # Деякі RouterOS відповідають лише якщо джерельний порт також 5678
                try:
                    s.bind(("", 5678))
                except Exception:
                    pass
                s.settimeout(1.0)
                # Надсилаємо кілька маленьких запитів
                for _ in range(2):
                    try:
                        s.sendto(b'\x00\x00\x00\x00', (ip, 5678))
                    except Exception:
                        pass
                try:
                    data, _ = s.recvfrom(2048)
                except Exception:
                    data = b''

                if data and len(data) > 4:
                    offset = 4
                    version, board = "", ""
                    while offset < len(data):
                        if offset + 4 > len(data):
                            break
                        tlv_type = int.from_bytes(data[offset:offset+2], 'big')
                        tlv_len = int.from_bytes(data[offset+2:offset+4], 'big')
                        offset += 4
                        if offset + tlv_len > len(data):
                            break

                        value = data[offset:offset+tlv_len]
                        try:
                            val_str = value.decode('utf-8', errors='ignore').strip()
                        except Exception:
                            val_str = ''

                        if tlv_type == 5:
                            mndp_identity = val_str
                        elif tlv_type == 7:
                            version = val_str
                        elif tlv_type == 14:
                            board = val_str
                        else:
                            if not mndp_identity and len(val_str) > 1:
                                mndp_identity = val_str

                        offset += tlv_len

                    res = []
                    if board:
                        res.append(board)
                    if version:
                        # Спроба витягти числову версію
                        m = re.search(r'([0-9]+(\.[0-9]+)+)', version)
                        ver = m.group(1) if m else version
                        res.append(f"RouterOS {ver}")

                    if res:
                        mndp_info = " ".join(res)
                    else:
                        mndp_info = "MikroTik (MNDP)"
        except Exception:
            pass
        return mndp_info, mndp_identity

    def probe_scapy_ping(self, ip):
        """Відправляє ICMP Echo запит через Scapy (Layer 3). Чудово працює через маршрутизатори/підмережі."""
        if 'sr1' not in globals(): return False
        try:
            reply = sr1(IP(dst=ip)/ICMP(), timeout=1.0, verbose=False)
            return reply is not None
        except Exception:
            return False

    def probe_tcp_ack(self, ip):
        """Відправляє TCP ACK на популярні порти. Відповідь RST вказує на живий хост, обходить більшість фаєрволів."""
        if 'sr1' not in globals(): return False
        try:
            # Додаємо 8291 (Winbox) та 2000 (Bandwidth Test) для гарантованого "пробиття" жорстких фаєрволів MikroTik
            for port in [80, 443, 2000, 5060, 8089, 8291]:
                reply = sr1(IP(dst=ip)/TCP(dport=port, flags='A'), timeout=0.5, verbose=False)
                if reply and reply.haslayer(TCP) and 'R' in str(reply[TCP].flags): # R = RST
                    return True
        except Exception:
            return False
        return False

    def probe_smb_v1(self, ip):
        """Спроба 'домовитись' по протоколу SMBv1. Успіх вказує на застарілу/вразливу систему."""
        try:
            with socket.create_connection((ip, 445), timeout=1.0) as s:
                # NetBIOS Session Service header + SMB Header + Negotiate Protocol Request
                packet = b'\x00\x00\x00\x85\xff\x53\x4d\x42\x72\x00\x00\x00\x00\x18\x53\xc8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xfe\x00\x00\x00\x00\x00\x62\x00\x02\x4e\x54\x20\x4c\x4d\x20\x30\x2e\x31\x32\x00'
                s.sendall(packet)
                response = s.recv(1024)
                # Якщо у відповіді є SMB-хедер і сервер обрав наш діалект (індекс не 0xFFFF), то SMBv1 підтримується.
                if response and response[4:8] == b'\xff\x53\x4d\x42' and response[8] == 0x72:
                    dialect_index = int.from_bytes(response[34:36], 'little')
                    if dialect_index != 0xFFFF:
                        return True
        except:
            pass
        return False

    def probe_dns_axfr(self, ip):
        """Спроба виконати трансфер зони DNS (AXFR). Успіх - це серйозний витік інформації."""
        if 'dns' not in globals(): return None
        domain = ""
        try:
            # Reverse DNS lookup для визначення домену
            rev_name = dns.reversename.from_address(ip)
            domain = str(dns.resolver.resolve(rev_name, "PTR")[0])
            parts = domain.strip('.').split('.')
            if len(parts) >= 2: domain = ".".join(parts[-2:])
            else: return None
        except Exception:
            return None
        try:
            zone = dns.zone.from_xfr(dns.query.xfr(ip, domain, timeout=2))
            if zone: return f"Успішний трансфер зони '{domain}'! Знайдено {len(zone.nodes.keys())} хостів."
        except Exception: pass
        return None

    def analyze_vulnerabilities(self, ports, banners, snmp_info, upnp_info, ftp_anon, device_type, mndp_info="", is_smbv1=False, axfr_result=None, versions_str=""):
        """Аналізатор вразливостей (CVE, Misconfigurations) на основі відкритих портів та банерів"""
        vulns = []
        exploits = []
        
        if 21 in ports:
            if ftp_anon:
                vulns.append("[КРИТИЧНО] Відкритий Анонімний FTP")
                exploits.append("[ЕКСПЛУАТАЦІЯ] Повний доступ до файлів без пароля (Читання/Запис)")
            else:
                vulns.append("FTP без шифрування")
                exploits.append("[MITM] Можливе перехоплення паролів у відкритому вигляді (Sniffing)")
        if 23 in ports:
            vulns.append("[РИЗИК] Telnet Доступ")
            exploits.append("[MITM] Трафік не зашифрований. Ризик перехоплення консолі / Bruteforce")
        if 445 in ports:
            if is_smbv1:
                vulns.append("[КРИТИЧНО] Увімкнено SMBv1!")
                exploits.append("[RCE] Система вкрай вразлива до EternalBlue (MS17-010) та інших черв'яків.")
            elif "Комп'ютер" in device_type:
                vulns.append("[РИЗИК] Відкритий SMB (Windows)")
                exploits.append("[RCE] Перевірити на новіші вразливості (SMBGhost, etc) / SMB Relay / Null Session Enum")
        if 3389 in ports:
            vulns.append("Відкритий RDP")
            exploits.append("[АТАКА] RDP Bruteforce, Ризик BlueKeep (CVE-2019-0708) для старих ОС")
        if 4899 in ports:
            vulns.append("Radmin Сервер")
            exploits.append("[АТАКА] Віддалене управління ПК. Ризик Bruteforce або перехоплення сесії")
        if 5900 in ports:
            vulns.append("VNC Сервер")
            exploits.append("[АТАКА] Bruteforce VNC, Ризик обходу автентифікації")
        if 554 in ports:
            vulns.append("RTSP Відеопотік (Камера)")
            exploits.append("[ПРИВАТНІСТЬ] Доступ до камери за дефолтними паролями (admin:12345)")
        if 9100 in ports:
            vulns.append("PDL / JetDirect (Принтер)")
            exploits.append("[АТАКА] Ін’єкція PJL (PRET), Крадіжка конфіденційних роздруківок")
        if snmp_info:
            vulns.append("[ВИТІК ДАНИХ] Відкритий SNMP ('public')")
            exploits.append("[РОЗВІДКА] Злив таблиці маршрутизації, паролів WiFi, конфігів (snmpwalk)")
        if upnp_info:
            vulns.append("UPnP відкритий")
            exploits.append("[ЕКСПЛУАТАЦІЯ] Прокидання портів ззовні без відома адміна (IGD), SSDP DDoS")
        if mndp_info:
            vulns.append("[ВИТІК ДАНИХ] Відкритий MNDP (MikroTik Discovery)")
            exploits.append("[РОЗВІДКА] Видимість пристрою в мережі (MAC, Версія, Identity)")
        if axfr_result:
            vulns.append("[КРИТИЧНО] Дозволено трансфер зони DNS (AXFR)")
            exploits.append(f"[ВИТІК ДАНИХ] {axfr_result}")

        # Аналіз по базі відомих версій CVE
        combined_info = f"{versions_str} {' '.join(banners.values())} {device_type} {snmp_info} {upnp_info}"
        for vuln_entry in self.COMMON_VULNS:
            if re.search(vuln_entry["match"], combined_info):
                if vuln_entry["vuln"] not in vulns:
                    vulns.append(vuln_entry["vuln"])
                if vuln_entry["exploit"] not in exploits:
                    exploits.append(vuln_entry["exploit"])
            
        # Якщо нічого серйозного
        vuln_str = "\n".join(vulns) if vulns else "Прямих загроз не знайдено"
        exploit_str = "\n".join(exploits) if exploits else "-"
        return vuln_str, exploit_str

    def analyze_device_type(self, vendor, ports, banners=None, ttl=None, netbios_name="", sip_info="", snmp_info="", upnp_info="", ssl_name="", mdns_info="", mikrotik_version="", grandstream_model="", dns_name="", mndp_info="", is_smbv1=False):
        if banners is None: banners = {}
        vendor_l = vendor.lower()
        mdns_l = mdns_info.lower()
        device_type = "Мережевий пристрій"
        os_guess = ""
        
        # OS Fingerprinting через TTL (Як це робить Nmap, але рідним Python)
        if ttl:
            if ttl <= 64: os_guess = "Linux/macOS/Android"
            elif ttl <= 128: os_guess = "Windows"
            else: os_guess = "Мережеве обладнання (Cisco/Router)"
            
        if netbios_name:
            device_type = f"Комп'ютер/Сервер (Ім'я: {netbios_name})"
            if not os_guess: os_guess = "Windows"

        if dns_name and not netbios_name:
            device_type = f"Хост ({dns_name})"
            if "Комп'ютер" not in device_type: 
                device_type = f"Мережевий хост ({dns_name})"

        banners_str = " ".join(banners.values()).lower()

        # Уточнення на основі нових протоколів (SIP / SNMP / UPnP)
        if upnp_info:
            device_type = f"Smart-Пристрій / Медіа ({upnp_info[:60]})"
            if not os_guess: os_guess = "Вбудована ОС (Linux/RTOS)"
        elif mdns_info:
            if "apple" in mdns_l or "mac" in mdns_l or "_airplay" in mdns_l:
                device_type = "Apple Device (mDNS)"
            elif "googlecast" in mdns_l:
                device_type = "Google Chromecast"
            elif "shelly" in mdns_l or "sonoff" in mdns_l:
                device_type = "IoT Smart Home Device"
            else:
                device_type = f"IoT / Media Пристрій ({mdns_info[:60]})"
        elif sip_info:
            device_type = f"SIP-Пристрій / IP-Телефон ({sip_info})"
            if not os_guess: os_guess = "Вбудована ОС (RTOS/Linux)"
        elif snmp_info:
            device_type = f"Керований Комутатор/Маршрутизатор ({snmp_info[:55]}...)"
            if 'cisco' in snmp_info.lower(): os_guess = "Cisco IOS"
            elif 'huawei' in snmp_info.lower(): os_guess = "Huawei VRP"
            elif 'mikrotik' in snmp_info.lower(): os_guess = "RouterOS"
            
        elif 'mikrotik' in vendor_l or 'routerboard' in vendor_l or mikrotik_version or mndp_info or 8291 in ports:
            device_type = "Маршрутизатор (MikroTik)"
            os_guess = "RouterOS"
            if 8291 in ports: device_type += " [Winbox відкритий]"
            if mndp_info: device_type += " [MNDP виявлено]"
        elif grandstream_model or 'grandstream' in vendor_l or 'grandstream' in sip_info.lower() or 'grandstream' in banners_str:
            best_gs = grandstream_model
            
            # Якщо Web-парсер нічого не дав, але є відповідь від SIP svmap-проби
            if not best_gs and sip_info:
                gs_parts = [s.split(': ', 1)[1] for s in sip_info.split(' | ') if ': ' in s and "SIP Сервіс" not in s]
                if gs_parts: best_gs = gs_parts[0]
                
            # Якщо SIP не дав результату, шукаємо в HTTP банерах (Server: UCM6204)
            if not best_gs and banners:
                for p, b in banners.items():
                    if 'grandstream' in b.lower() or 'ucm' in b.lower():
                        m = re.search(r'(?i)Server:\s*([^\s\]\[]+.*?)(?:\s+Powered-By|$|\[)', b)
                        if m: best_gs = m.group(1).strip(); break

            if best_gs: 
                if not best_gs.lower().startswith('grandstream'): best_gs = f"Grandstream {best_gs}"
                device_type = f"IP-Телефонія / АТС ({best_gs})"
            else:
                device_type = "IP-Телефонія / АТС (Grandstream)"
                
            if not os_guess: os_guess = "Вбудована ОС (RTOS/Linux)"
        elif any(v in vendor_l for v in ['yealink', 'polycom', 'snom', 'fanvil', 'avaya']):
            device_type = f"IP-Телефон ({vendor})"
            if sip_info: device_type += f" [{sip_info[:40]}]"
        elif any(v in vendor_l for v in ['cisco', 'tp-link', 'ubiquiti', 'asus', 'd-link', 'netgear', 'tenda', 'keenetic', 'mercusys', 'zte', 'linksys', 'zyxel', 'airties']):
            device_type = f"Комутатор/Роутер ({vendor})"
        elif any(v in vendor_l for v in ['apple', 'samsung', 'xiaomi', 'huawei', 'oppo', 'vivo', 'realme', 'motorola', 'lg electronics', 'sony', 'oneplus', 'nokia', 'leeco', 'lemobile']):
            device_type = f"Смартфон/Планшет/ТБ ({vendor})"
        elif 'synology' in vendor_l or 'qnap' in vendor_l or 548 in ports:
            device_type = f"NAS Сховище ({vendor})"
        elif 'starlink' in vendor_l or 'starlink' in banners_str:
            device_type = "Супутниковий Термінал (Starlink)"
            os_guess = "Вбудована ОС (Linux)"
        elif 2049 in ports and "NAS" not in device_type:
            device_type = f"NAS / Сховище (NFS)"
        elif 554 in ports:
            device_type = f"IP Камера / NVR ({vendor})"
        elif 9100 in ports or 631 in ports or 515 in ports: # JetDirect, IPP, LPR
            device_type = f"Мережевий Принтер ({vendor})"
        elif 32400 in ports:
            device_type = "Медіа-сервер (Plex)"
        elif 8096 in ports or 8920 in ports:
            device_type = "Медіа-сервер (Jellyfin/Emby)"
        elif 1883 in ports or 8883 in ports:
            device_type = f"IoT / MQTT Брокер ({vendor})"
        elif any(v in vendor_l for v in ['dell', 'hp', 'lenovo', 'asustek', 'msi', 'acer', 'gigabyte', 'asrock', 'intel', 'realtek', 'qualcomm', 'broadcom', 'microsoft']):
            device_type = f"Комп'ютер/Ноутбук/ПК ({vendor})"
        elif any(v in vendor_l for v in ['vmware', 'virtualbox', 'qemu', 'parallels']):
            device_type = f"Віртуальна машина ({vendor})"
        elif any(v in vendor_l for v in ['espressif', 'tuya', 'amazon', 'nintendo', 'sonos', 'raspberry']):
            device_type = f"IoT / Smart-пристрій ({vendor})"

        # Перевизначення пристрою за допомогою банерів
        if 'microsoft-iis' in banners_str:
            device_type = "Windows Server (IIS)"
        elif 'apache' in banners_str or 'nginx' in banners_str:
            if device_type.startswith("Мережевий") or device_type.startswith("Хост"):
                device_type = f"Linux/Web-Сервер ({banners_str[:20]})"

        if 445 in ports or 139 in ports or 135 in ports or 3389 in ports:
            if "Комп'ютер" not in device_type and "Сервер" not in device_type and "Ноутбук" not in device_type:
                if is_smbv1:
                    device_type += " (Ймовірно застаріла Windows)"
                else:
                    device_type += " (Ймовірно Windows ПК/Сервер)"
        elif (80 in ports or 443 in ports or 8080 in ports) and device_type == "Мережевий пристрій":
             device_type = "Web-Сервер / Інтерфейс керування"
        
        # ФІНАЛЬНИЙ ФОЛЛБЕК НА ВИРОБНИКА (Ніколи не повертає просто "Мережевий пристрій", якщо вендор відомий)
        if device_type == "Мережевий пристрій" and vendor and vendor not in ["Невідомий виробник", "Невідомо", "Прихована MAC (Рандомізована пристроєм)"]:
            device_type = f"Мережевий пристрій ({vendor})"
        elif vendor == "Прихована MAC (Рандомізована пристроєм)" and device_type == "Мережевий пристрій":
            # Поглиблений аналіз пристроїв з прихованою MAC на основі інших "відбитків"
            if "Apple Device" in mdns_info or any(p in ports for p in [62078, 5000, 7000]): # AirPlay/AirDrop ports
                device_type = "Прихована MAC (Ймовірно Apple: iPhone/iPad/Mac)"
            elif ttl and ttl > 64:
                device_type = "Прихована MAC (Ймовірно Windows 10/11)"
            elif "googlecast" in mdns_info.lower() or "chromecast" in dns_name.lower():
                 device_type = "Прихована MAC (Ймовірно Google: Android/Chromecast)"
            elif mdns_info or upnp_info:
                 # Якщо є хоч якась інформація з mDNS/UPnP, показуємо її
                 extra_info = (mdns_info or upnp_info).strip()
                 device_type = f"Прихована MAC (IoT/Media: {extra_info})"
            else:
                 # Якщо нічого не допомогло
                 device_type = "Пристрій з прихованою MAC (iOS/Android/Win11)"

        # Додаємо здогадану ОС, якщо раніше це не було визначено
        if os_guess and "ОС:" not in device_type:
            device_type += f" | ОС: {os_guess}"
            
        # Додаємо внутрішній домен/ім'я з перехопленого сертифіката
        if ssl_name and ssl_name.lower() not in device_type.lower():
             device_type += f" [Cert Name: {ssl_name}]"

        return device_type


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    parser = argparse.ArgumentParser(description="NETFUCK - Network scanner GUI")
    parser.add_argument('--interface', '-i', help='Назва інтерфейсу для сканування (наприклад "Ethernet")')
    parser.add_argument('--disable-l2', action='store_true', help='Вимкнути ARP/Scapy L2 проби (корисно при віддалених запусках або Windows)')
    parser.add_argument('--no-virtual-filter', action='store_true', help='Не виключати віртуальні адаптери при авто-підборі')
    args = parser.parse_args()

    root = ctk.CTk()
    app = NetworkScannerApp(root)
    # Apply CLI options to app
    if args.interface:
        try:
            app.configure_interface(args.interface, disable_l2=args.disable_l2)
        except Exception:
            pass
    else:
        app.exclude_virtual_ifaces = not args.no_virtual_filter
        if args.disable_l2:
            app.disable_l2 = True
    root.mainloop()
