import pyglet

class Model:
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        color = ('c3f', (1, 1, 1)*4)
        x, y, z = 0, 0, -1
        x1, y1, z1 = x+1, y+1, z+1
        self.batch.add(4, pyglet.gl.GL_QUADS, None, ('v3f', (x,y,z, x1,y,z, x1,y1,z, x,y1,z)), color)

    def draw(self):
        self.batch.draw()


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_maximum_size(500, 500)

        self.model = Model()

    def projection(self):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()

    def model_f(self):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()

    def set3d(self):
        self.projection()
        pyglet.gl.gluPerspective(70, self.width/self.height, 0.05, 1000)
        self.model_f()

    def on_draw(self):
        self.clear()
        self.set3d()
        self.model.draw()

