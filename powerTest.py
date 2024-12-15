from panasonicAW import ptzHead
import time

h = ptzHead.Camera("192.168.1.150", "AW-HE40")
print(h.speed_table)
print(max(h.speed_table))
print(h.speed_table[max(h.speed_table)])



