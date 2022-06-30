from neoscore.common import *
import numpy as np
import time
import pathlib
import threading

class mover:
    score_x = Unit(0) #Score does not rotate
    score_x_ini = Unit(0) #Point around which rotation occurs

    def __init__(self, xpos, ypos, rot, image_path):
        self.xpos = xpos
        self.xpos_ref = xpos
        self.xpos_ini = xpos
        self.ypos = ypos
        self.ypos_ref = ypos
        self.ypos_ini = ypos
        self.rot = rot
        self.rot_ref = rot
        self.rot_ini = rot
        self.image_path = image_path
        self.rendering = False

    def make_visible(self):
        global reticle
        self.obj = Image((self.xpos,self.ypos),reticle,self.image_path,rotation = self.rot)
        self.rendering = True

    def make_invisible(self):
        self.obj.remove()
        self.rendering = False

    def prep_object(self):
        self.xpos_ini = self.xpos
        self.ypos_ini = self.ypos
        self.xpos = self.xpos - self.score_x_ini
        self.rot_ini = self.rot

    @classmethod
    def score_shift(cls,t):
        cls.score_x = cls.score_x_ini + Unit(t*anim_rate)

    def obj_forward(self,t):
        self.xpos = self.xpos_ini - self.score_x
        if self.rendering:
            self.obj.x = self.xpos
            self.obj.y = self.ypos

    def obj_rotate(self,t,degrees,rot_time):
        self.rot = self.rot_ini + t*degrees/rot_time
        self.xpos = (self.xpos_ini * np.cos(t*np.deg2rad(degrees)/rot_time)-self.ypos_ini * np.sin(t*np.deg2rad(degrees)/rot_time))
        self.ypos = (self.ypos_ini * np.cos(t*np.deg2rad(degrees)/rot_time)+self.xpos_ini * np.sin(t*np.deg2rad(degrees)/rot_time))
        if self.rendering:
            self.obj.rotation = self.rot
            self.obj.x = self.xpos
            self.obj.y = self.ypos

    def confirm_obj_rotate(self,degrees):
        self.rot = self.rot_ini + degrees
        self.xpos = (self.xpos_ini * np.cos(np.deg2rad(degrees))-self.ypos_ini * np.sin(np.deg2rad(degrees)))
        self.ypos = (self.ypos_ini * np.cos(np.deg2rad(degrees))+self.xpos_ini * np.sin(np.deg2rad(degrees)))
        if self.rendering:
            self.obj.rotation = self.rot
            self.obj.x = self.xpos
            self.obj.y = self.ypos

def initialize_rotation(xpos,ypos,rot):
    global movers
    new_x = xpos*np.cos(np.deg2rad(rot))-ypos*np.sin(np.deg2rad(rot))
    new_y = ypos*np.cos(np.deg2rad(rot))+xpos*np.sin(np.deg2rad(rot))
    return new_x, new_y

def check_new():
    global movers
    for i in range(movers.size):
        if movers[i].rendering==False:
            if movers[i].xpos < Unit(300) and movers[i].xpos > Unit(-300) and movers[i].ypos < Unit(300) and movers[i].ypos > Unit(-300):
                movers[i].make_visible()

def check_bounds():
    global movers
    for i in range(movers.size):
        if movers[i].rendering==True:
            if movers[i].obj.x > Unit(300) or movers[i].obj.x < Unit(-300) or movers[i].obj.y > Unit(300) or movers[i].obj.y < Unit(-300):
                movers[i].make_invisible()

def render_area():
    while True:
        check_new()
        check_bounds()
        time.sleep(1)

def new_move():
    global movers
    temp = int(time.time())
    for i in range(movers.size):
        movers[i].prep_object()
    return temp

def forward(t):
    global movers
    mover.score_shift(t)
    for i in range(movers.size):
        movers[i].obj_forward(t)

def rotate(t,degrees,rot_time):
    global movers
    for i in range(movers.size):
        movers[i].obj_rotate(t,degrees,rot_time)

def refresh_func_rot_cw(time:float):
    global movers
    global start_time
    t = time-start_time
    degrees = 30
    rot_time = 2
    rotate(t,degrees,rot_time)
    if t >=2:
        for i in range(movers.size):
            movers[i].confirm_obj_rotate(30)
        check_new()
        check_bounds()
        start_time = new_move()
        neoscore.set_refresh_func(refresh_func_forward, 30)

def refresh_func_forward(time:float):
    global movers
    global start_time
    t = time-start_time
    forward(t)
    if t >=8:
        check_new()
        check_bounds()
        start_time = new_move()
        neoscore.set_refresh_func(refresh_func_rot_cw, 30)


def main():
    global movers
    global reticle
    global start_time
    global anim_rate
    anim_rate = 60

    neoscore.setup()
    window_center_x = Unit(0)
    window_center_y = Unit(-300)

    reticle = Text((window_center_x,window_center_y), None, "O")
    staff = Staff((window_center_x-Unit(20),window_center_y), None, Mm(1))
    clef = Clef(ZERO, staff, 'treble')

    staff_1 = pathlib.Path(".")/"staff_1.png"
    squiggle_1 = pathlib.Path(".")/"squiggle_1.png"
    star_1 = pathlib.Path(".")/"star_1.png"

    movers = np.array([])

    for i in range(20):
        movers = np.append(movers,mover(Unit(0+(74*i)),Unit(0),0,staff_1))

    movers = np.append(movers,mover(Unit(10),Unit(0),0,squiggle_1))
    movers = np.append(movers,mover(Unit(250),Unit(-20),0,star_1))
    movers = np.append(movers,mover(Unit(500),Unit(-20),0,star_1))

    check_new()
    check_bounds()
    start_time = new_move()

    render_thread = threading.Thread(target=render_area)
    render_thread.start()

    neoscore.set_refresh_func(refresh_func_forward, 30)
    neoscore.show(display_page_geometry=False)

if __name__ == '__main__':
    main()
