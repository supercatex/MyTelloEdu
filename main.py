#coding=utf-8
from core.TelloEdu import TelloEduManager

tm = TelloEduManager(8889)
tm.find_tello()
if len(tm.tello_list) != 2:
    exit()

tm.sn_mapping()
tm.set_tello_name("0TQDG44EDBNYXK", "1")
tm.set_tello_name("0TQDG44EDBC6WJ", "2")
tm.get_battery()

for t in tm.tello_list:
    print(t.ip, t.sn, t.name, t.battery)

tm.set_next_command("*", "mon")
tm.action("啟動挑戰版功能")

tm.set_next_command("*", "mdirection 0")
tm.action("只啟動下方挑戰版")

tm.set_next_command("*", "takeoff")
tm.action("起飛")

tm.set_next_command("1", "go 0 0 60 60 m1")
tm.set_next_command("2", "go 0 0 60 60 m3")
tm.action("下方定位", 3)

tm.set_next_command("1", "jump 50 0 60 60 0 m1 m2")
tm.set_next_command("2", "jump 50 0 60 60 0 m3 m4")
tm.action("向前", 3)

tm.set_next_command("1", "jump 0 -50 80 60 0 m2 m1")
tm.set_next_command("2", "jump 0 -50 80 60 0 m4 m3")
tm.action("向右", 3)

tm.set_next_command("1", "go 0 0 120 60 m1")
tm.set_next_command("2", "go 0 0 40 60 m3")
tm.action("上下浮動", 1)

tm.set_next_command("1", "go 0 0 40 60 m1")
tm.set_next_command("2", "go 0 0 120 60 m3")
tm.action("", 1)

tm.set_next_command("1", "go 0 0 80 60 m1")
tm.set_next_command("2", "go 0 0 80 60 m3")
tm.action("", 1)

tm.set_next_command("*", "land")
tm.action("降落")
