import pyglet
from pyglet.gl import *
from Drone import Drone
from Vector import Vector
from DronePhysics import DronePhysics

pos = [0, 0, -10]
rot_y = 0


class Scene(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.camera_position = [0, 0, -20]
        self.drones = []

    def add_drones(self):
        for index in range(1, 10):
            self.drones.append(Drone(Vector(10, 50 * index, 0), Vector(15, 0, 0), Vector(500, 50 * index, 0), index))

        for index in range(1, 10):
            self.drones.append(
                Drone(Vector(480, 50 * (index + 0.5), 0), Vector(7, 0, 0), Vector(-500, 50 * (index + 0.5), 0), index))

        self.drones.append(Drone(Vector(150, 50 * 3, 0), Vector(0, 0, 0), Vector(500, 50 * 7, 0), 7))
        self.drones.append(Drone(Vector(120, 50 * 1, 0), Vector(0, 0, 0), Vector(500, 50 * 8, 0), 8))
        self.drones.append(Drone(Vector(150, 50 * 2 + 17 * 3, 0), Vector(0, 0, 0), Vector(500, 50 * 9, 0), 10))

        self.addNeighbors()

    def addNeighbors(self):
        for drone1 in self.drones:
            for drone2 in self.drones:
                if drone1 != drone2:
                    drone1.neighbors.append(drone2)

    def gl_init(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, 1, 0.1, 100)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glTranslatef(*pos)
        glRotatef(rot_y, 0, 1, 0)

    def on_draw(self):
        self.clear()


        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, 1, 0.1, 100)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glTranslatef(*pos)
        glRotatef(rot_y, 0, 1, 0)

        glBegin(GL_SPHERE_MAP)
        glBegin(GL_POLYGON)
        glVertex3f(-5, -5, 0)
        glVertex3f(5, -5, 0)
        glVertex3f(0, 5, 0)
        glEnd()

        glFlush()

    # def on_key_press(self, m):
    #     global pos_z, rot_y
    #
    #     if self == pyglet.window.key.W:
    #         pos[2] -= 1
        # if s == pyglet.window.key.S:
        #     pos[2] += 1
        # if s == pyglet.window.key.A:
        #     rot_y += 5
        # if s == pyglet.window.key.D:
        #     rot_y -= 5

    def run_app(self):
        pyglet.app.run()

