#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import time

from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

# Laplacian(T) = 0   ---  Laplace equation

WALL_EPSILON = 0.05
DICE_ROLLS_PER_DOT = 10**3


class TemperatureProblem:
    """
    Given temperatures in four walls of 2-dimensional rectangle calculates temperature in specified point.

    Workflow:
    After passing Point Of Interest coordinates, class initiates a list of specified length.
    Points are generated with get_circle_and_rnd_point() method.
    get_poi_temp() builds trajectory until point hits a wall.
    Once point has hit the wall, temperature value is appended to the array.
    Once array reaches needed length, calculation stops and returns mean value of array.

    Usage:
    Class is called with conventional __init__:
    temp_calc = TemperatureProblem(x_len, y_len, bottom_w_temp, right_w_temp, left_w_temp, upper_w_temp)
    Rectangle walls layout:
       _______
      |   3   |
     2|_______|1
          0
    Calculate temperature for the point of interest:
    t = temp_calc.get_poi_temp(x_poi, y_poi)

    Plot 3d figure of temperature on given task:
    t.plot3d()

    """
    def __init__(self, xdim, ydim, temp):
        self.xDim, self.yDim, self.borderTemps = xdim, ydim, temp   # floats x, y, [t1, t2, t3, t4]
        self.xPOI, self.yPOI = None, None       # floats x, y
        self.CalculatedPOIArray = None          # array of floats [x, y, T]
        self.CurrentPointArray = []           # array of floats [T_i]

    @property
    def poi_is_inside(self):
        return True if 0 <= self.xPOI <= self.xDim or 0 <= self.yPOI <= self.yDim else False

    def point_is_next_to_wall(self, x, y):
        """
        Returns
        :param x:   x point coordinate
        :param y:   y point coordinate
        :return:    number of wall point is next to, None if point is not next to any wall
        """
        if x <= WALL_EPSILON:
            return 2
        elif y <= WALL_EPSILON:
            return 0
        elif self.xDim - x <= WALL_EPSILON:
            return 1
        elif self.yDim - y <= WALL_EPSILON:
            return 3
        else:
            return None

    def get_circle_and_rnd_point(self, x_pr, y_pr):
        # select circle radius and calculate random angle
        cir_rad = min(self.xDim - x_pr, self.yDim - y_pr, x_pr, y_pr)
        angle = np.random.rand() * 2 * np.pi
        # calculate new point coordinates
        return np.array([x_pr, y_pr]) + np.array([cir_rad * np.cos(angle), cir_rad * np.sin(angle)])

    def get_poi_temp(self, x, y):
        """
        Calculates POI temperature with Monte-Carlo wanderings method.
        :param x: x coordinate of POI
        :param y: y coordinate of POI
        :return: temperature of point with specified coordinates
        """
        start_time = time.time()
        # read values of POI and assign to the processing variables
        self.xPOI, self.yPOI = curr_x, curr_y = x, y
        if not self.poi_is_inside:
            # stop execution if POI is not inside rectangle
            raise Exception("POI must be inside initial rectangle!")

        while len(self.CurrentPointArray) < DICE_ROLLS_PER_DOT:
            # rolling random search until generated enough results
            try:
                # time.sleep(1)
                # can be used for debugging purposes
                curr_x, curr_y = self.get_circle_and_rnd_point(curr_x, curr_y)
                wall = self.point_is_next_to_wall(curr_x, curr_y)
                # print("Collected {0} points of {1}".format(len(self.CurrentPointArray), DICE_ROLLS_PER_DOT))
                # can be used for debugging purposes
                if wall is not None:
                    curr_x, curr_y = self.xPOI, self.yPOI
                    self.CurrentPointArray.append(self.borderTemps[wall])
            except KeyboardInterrupt:
                # Interrupt execution if needed without stopping the kernel
                print("Calculation manually interrupted through KeyboardInterrupt")
                self.CurrentPointArray = []
                self.xPOI, self.yPOI = None, None
                return None

        temp = np.mean(np.array(self.CurrentPointArray))
        # print("Calculated through %.4f seconds" % (time.time() - start_time))
        self.CurrentPointArray = []
        return temp

    def plot3d(self, plot_step=0.2):
        # generating X axis
        X = np.arange(0, self.xDim, plot_step, dtype=float)
        # generating Y axis
        Y = np.arange(0, self.yDim, plot_step, dtype=float)
        TEMP = np.zeros([len(Y), len(X)])

        # calculating data for X, Y
        points_count = 0
        print("Points to calculate: ", len(X) * len(Y))
        for i in range(len(X)):
            for j in range(len(Y)):
                TEMP[j, i] = self.get_poi_temp(X[i], Y[j])
                points_count += 1
                print(points_count)

        # plotting
        X, Y = np.meshgrid(X, Y)
        fig = plt.figure()
        ax = Axes3D(fig)

        # adjusting plot
        ax.plot_surface(X, Y, TEMP, cmap=cm.coolwarm, antialiased=False)
        plt.show()


if __name__ == '__main__':
    t = TemperatureProblem(15, 10, [10, 5, 5, 20])
    print("Calculated temperature for point:", t.get_poi_temp(5, 5))
    print("Plotting...")
    t.plot3d(plot_step=0.1)
