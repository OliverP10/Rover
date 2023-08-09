# import math

# VERT_DIST_FROM_CENTER = 20
# HORIZ_DIST_FROM_CENTER = 20
# STEERING_DISTANCE = -45

# wheel_one_angle = 0
# wheel_two_angle = 0
# wheel_three_angle = 0
# wheel_four_angle = 0

# if STEERING_DISTANCE > 0:
#     wheel_one_angle = 90 - math.degrees(math.atan((STEERING_DISTANCE+HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER))
#     wheel_two_angle = 90 - math.degrees(math.atan((STEERING_DISTANCE-HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER))
#     wheel_three_angle = 270 + math.degrees(math.atan((STEERING_DISTANCE+HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER))
#     wheel_four_angle = 270 + math.degrees(math.atan((STEERING_DISTANCE-HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER))
# else:
#     wheel_one_angle = 270 + abs(math.degrees(math.atan((STEERING_DISTANCE+HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER)))
#     wheel_two_angle = 270 + abs(math.degrees(math.atan((STEERING_DISTANCE-HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER)))
#     wheel_three_angle = 90 -  abs(math.degrees(math.atan((STEERING_DISTANCE+HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER)))
#     wheel_four_angle = 90 -  abs(math.degrees(math.atan((STEERING_DISTANCE-HORIZ_DIST_FROM_CENTER) / VERT_DIST_FROM_CENTER)))

# print(wheel_one_angle)
# print(wheel_two_angle)
# print(wheel_three_angle)
# print(wheel_four_angle)

def map_angle_to_servo(angle_deg):
    if 0 <= angle_deg <= 180:
        return angle_deg
    else:
        return angle_deg - 180

while(True):
    print(map_angle_to_servo(int(input())))