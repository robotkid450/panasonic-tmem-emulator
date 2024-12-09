from panasonicAW import ptzHead
import time

ip = input("Enter the IP of the device: ")
model = input("Enter the model of the device: ")

head = ptzHead.Camera(ip)
human_pan_min = int(input("Enter the minimum pan angle in degrees: "))
human_pan_max = int(input("Enter the maximum pan angle in degrees: "))

human_tilt_min = int(input("Enter the minimum tilt angle in degrees: "))
human_tilt_max = int(input("Enter the maximum tilt angle in degrees: "))

ready_message = '''
Please verify the following is correct

ip : {ip}
model : {model}

pan minimum : {human_pan_min}
pan maximum : {human_pan_max}
tilt minimum : {human_tilt_min}
tilt maximum : {human_tilt_max}

'''

result_message = '''
Values pulled from Camera Head

ip : {ip}
model : {model}

pan minimum : {head_pan_min}
pan maximum : {head_pan_max}
tilt minimum : {head_tilt_min}
tilt maximum : {head_tilt_max}
zoom minimum : {zoom_min_min}
zoom maximum : {zoom_min_max}
'''
print(ready_message.format(ip=ip, model=model, human_pan_min=human_pan_min,human_pan_max=human_pan_max,
    human_tilt_min=human_tilt_min, human_tilt_max=human_tilt_max))
input("Press Enter to continue...")
head.position_set_absolute_with_speed_hex("0000", "ffff", 89)

time.sleep(0.4)
head.zoom_set_absolute_hex("555")
time.sleep(5)
pt_min_x, pt_min_y = head.position_query_hex()
time.sleep(0.4)
zoom_min = head.zoom_query_hex()
time.sleep(0.4)
head.zoom_set_absolute_hex("FFF")
time.sleep(0.4)
head.position_set_absolute_with_speed_hex("ffff", "0000", 89)
time.sleep(5)
pt_max_x, pt_max_y = head.position_query_hex()
time.sleep(0.4)
zoom_max = head.zoom_query_hex()

pt_min_x = head.hex_to_int(pt_min_x)
pt_min_y = head.hex_to_int(pt_min_y)

pt_max_x = head.hex_to_int(pt_max_x)
pt_max_y = head.hex_to_int(pt_max_y)

zoom_min = head.hex_to_int(zoom_min)
zoom_max = head.hex_to_int(zoom_max)


print(result_message.format(ip=ip, model=model, head_pan_min=pt_min_x, head_pan_max=pt_max_x,
    head_tilt_min=pt_min_y, head_tilt_max=pt_max_y, zoom_min_min=zoom_min, zoom_min_max=zoom_max))
