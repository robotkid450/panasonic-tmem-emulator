CAMERA_MODELS = {
    "AW-UE80":{
            "pan":{
                "angles" : (-175.00, 175.00),
                "angles_head" : (11529, 54005),
                "speed_bounds" : (1, 100),
                "speed_max" : 180
            },
            "tilt":{
                "angles" : (-30.00, 90.00),
                "angles_head" : (36408, 21845),
                "speed_bounds" : (1, 100),
                "speed_max" : 180
            },
            "zoom": {
                "position_bounds": (1365, 4057),
                "speed_bounds" : (1, 99),
            },
            "command_delay": 0.13,
            "move_with_speed_bounds" : (0, 89)
    },
    "AW-UE100":{
            "pan":{
                "angles" : (-175.00, 175.00),
                "angles_head" : (11529, 54005),
                "speed_bounds" : (1, 100),
                "speed_max" : 180,
            },
            "tilt":{
                "angles" : (-30.00, 210.00),
                "angles_head" : (36408, 7281),
                "speed_bounds" : (1, 100),
                "speed_max" : 180
            },
            "zoom": {
                "position_bounds": (1365, 4095),
                "speed_bounds" : (1, 99),
            },
            "command_delay": 0.13,
            "move_with_speed_bounds" : (0, 89)

    },"AW-HE40":{
            "pan":{
                "angles" : (-175.00, 175.00),
                "angles_head" : (54005, 11529),
                "speed_bounds" : (1, 100),
                "speed_max" : {
                    "normal" : 90
                }
            },
            "tilt":{
                "angles" : (-30.00, 90.00),
                "angles_head" : (36408, 21845),
                "speed_bounds" : (1, 100),
                "speed_max" : {
                    "normal" : 90
                }
            },
            "zoom": {
                "position_bounds": (1365, 4057),
                "speed_bounds" : (1, 99),
            },
            "command_delay": 0.13,
            "move_with_speed_bounds" : (0, 89)
    },
    "default":{
            "pan":{
                "angles" : (-175.00, 175.00),
                "angles_head" : (54005, 11529),
                "speed_bounds" : (1, 100),
                "speed_max" : 180
            },
            "tilt":{
                "angles" : (-30.00, 90.00),
                "angles_head" : (36408, 21845),
                "speed_bounds" : (1, 100),
                "speed_max" : 180
            },
            "zoom": {
                "position_bounds": (1365, 4057),
                "speed_bounds" : (1, 99),
            },
            "command_delay": 0.13,
            "move_with_speed_bounds" : (0, 89)
    }

}
