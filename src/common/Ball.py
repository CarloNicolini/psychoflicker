class Ball():

    """
    Class to handle ball position and handle ball collisions, will be part
    """

    def __init__(self, win, position, direction, speed, radius, color):
        from psychopy import visual
        self.direction = direction
        self.radius = radius
        self.shape = visual.Circle(win, radius=self.radius, edges=128,
                                   lineWidth=1, lineColor=color,
                                   fillColor=color,
                                   closeShape=True,
                                   interpolate=True, pos=position, units='cm')
        self.shape.setFillColor(color)
        self.shape.setLineColor(color)

    def setPos(self, newpos):
        self.shape.setPos(newpos)

    def move(self, disp):
        newPos = self.pos() + disp
        self.shape.setPos(newPos)

    def draw(self):
        self.shape.draw()

    def pos(self):
        import numpy as np
        return np.array(self.shape.pos)

    """ Change the color of the ball to draw"""

    def setColor(self, newColor):
        # self.shape.setUseShaders(True)
        self.shape.setFillColor(newColor)
        self.shape.setLineColor(newColor)
