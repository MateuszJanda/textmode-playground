#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import sys
import curses
import locale
import time
import math
import numpy as np


BODY_COUNT = 200
VIEWING_ANGLE = 120
MIN_DIST = 20
NEIGHB_RADIUS = 50
WEIGHT_VEL = 0.1
WEIGHT_NEIGHB_DIST = 0.15
WEIGHT_MIN_DIST = 0.15
WEIGHT_NOISE = 0.1
MAX_VEL = 4
DT = 1
TONE_SYMBOLS = '@%#x+=:-. '


class Body:
    def __init__(self, size):
        self.pos = np.array([np.random.uniform(0, size[0]),
                             np.random.uniform(0, size[1])])
        self.vel = np.random.uniform(-2, 2, size=[2])
        self.avg_vel = np.copy(self.vel)
        self.avg_dist = 0
        self.l = 1

class KdTree:
    Y_AXIS = 0
    X_AXIS = 1

    class Node:
        def __init__(self, point):
            self.point = point
            self.rect = (0, 0, 0, 0)
            self.lb = None
            self.rt = None

    class Task:
        def __init__(self, node, dim):
            self.node = node
            self.dim = dim

    def __init__(self):
        self.node_counter = 0
        self.root = None

    def insert(self, point):
        insert_node = Node(point)

        pointer = root
        dim = Y_AXIS

        parent = None
        parent_dim = None

        while pointer:
            parent = pointer
            parent_dim = dim

            if np.all(parent.point == insert_node.point):
                return

            if (parent_dim == Y_AXIS and insert_node.point[0] < parent.point[0]) or \
               (parent_dim == X_AXIS and insert_node.point[1] < parent.point[1]):
                pointer = pointer.lb
            else:
                pointer = pointer.rt
            dim = self._next_dimension(dim)

        if parent:
            insert_node.rect = RectHV(0.0, 0.0, 1.0, 1.0)
            root = insert_node
        else:
            insert_node.rect = self._create_rect(parent, insert_node.point, parent_dim)
            if (parent_dim == Y_AXIS and insert_node.point[0] < parent.point[0]) or \
               (parent_dim == X_AXIS and insert_node.point[1] < parent.point[1]):
                parent.lb = insert_node
            else:
                parent.rt = insert_node

        self.node_counter += 1

    def _create_rect(self, parent, insert_pt, parent_dim):
        if parent_dim == Y_AXIS:
            if insert_pt[0] < parent.point[0]:
                return RectHV(parent.rect.xmin(), parent.rect.ymin(), parent.rect.xmax(), parent.point[0])
            else:
                return RectHV(parent.rect.xmin(), parent.point[0], parent.rect.xmax(), parent.rect.ymax())
        else:
            if insert_pt[1] < parent.point[1]:
                return RectHV(parent.rect.xmin(), parent.rect.ymin(), parent.point[1], parent.rect.ymax())
            else:
                return RectHV(parent.point[1], parent.rect.ymin(), parent.rect.xmax(), parent.rect.ymax())

    def contains(self, point):
        pointer = root
        dim = Y_AXIS
        while pointer:
            if np.all(pointer.point == point):
                return True

            if (dim == Y_AXIS and point[0] < pointer.point[0]) or \
               (dim == X_AXIS and point[1] < pointer.point[1]):
                pointer = pointer.lb
            else:
                pointer = pointer.rt
            dim = self._next_dimension(dim)

        return False

    def range(self, rect):
        result = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node == None or rect.intersects(node.rect):
                continue

            if rect.contains(node.point):
                result.append(node.point)

            stack.append(node.rt)
            stack.append(node.lb)

        return result

    def nearest(self, point):
        # https://www.cs.cmu.edu/~ckingsf/bioinfo-lectures/kdtrees.pdf
        if root == None:
            return None

        best_point = self.root.point
        best_dist = self.root.point.distanceSquaredTo(point)

        stack = [Task(self.root, Y_AXIS)]
        while stack:
            task = stack.pop()
            if task.node == None or task.node.rect.distanceSquaredTo(p) > best_dist:
                continue

            dist = task.node.point.distanceSquaredTo(point)
            if dist < best_dist:
                bestDist = dist
                bestPoint = task.node.point

            next_dim = self._next_dimension(task.dim)
            if (task.dim == Y_AXIS and point[0] < task.node.point[0]) or \
               (task.dim == X_AXIS and point[1] < task.node.point[1]):
                stack.append(Task(task.node.rt, next_dim))
                stack.append(Task(task.node.lb, next_dim))
            else:
                stack.append(Task(task.node.lb, next_dim))
                stack.append(Task(task.node.rt, next_dim))

        return best_dist

    def _next_dimension(self, dim):
        if dim == Y_AXIS:
            return X_AXIS
        return Y_AXIS


def main(scr):
    setup_stderr()
    setup_curses()
    scr.clear()

    np.random.seed(3145)
    size = np.array([curses.LINES*4, (curses.COLS-1)*2])
    bodies = [Body(size) for _ in range(BODY_COUNT)]

    while True:
        for b1 in bodies:
            for b2 in bodies:
                if b1 is b2:
                    continue

                dist = math.sqrt((b1.pos[1] - b2.pos[1])**2 + (b1.pos[0] - b2.pos[0])**2)
                k = b1.vel[1] / math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) * \
                    ((b2.pos[1] - b1.pos[1]) / dist) + \
                    b1.vel[0] / math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) * \
                    ((b2.pos[0] - b1.pos[0]) / dist)

                if k < -1:
                    k = -1
                elif k > 0:
                    k = 1
                k = math.fabs(180*math.acos(k)) / math.pi
                if dist < NEIGHB_RADIUS and k > VIEWING_ANGLE:
                    b1.l += 1
                    b1.avg_vel += b2.vel
                    b1.avg_dist += dist

        for b1 in bodies:
            b1.vel += WEIGHT_VEL * ((b1.avg_vel / b1.l) - b1.vel)
            b1.vel += WEIGHT_NOISE * (np.random.uniform(0, 0.5, size=[2]) * MAX_VEL)
            if b1.l > 1:
                b1.avg_dist /= b1.l - 1

            for b2 in bodies:
                if b1 is b2:
                    continue

                dist = math.sqrt((b1.pos[1] - b2.pos[1])**2 + (b1.pos[0] - b2.pos[0])**2)
                k = b1.vel[1] / math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) * \
                    ((b2.pos[1] - b1.pos[1]) / dist) + \
                    b1.vel[0] / math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) * \
                    ((b2.pos[0] - b1.pos[0]) / dist)

                if k < -1:
                    k = -1
                elif k > 1:
                    k = 1
                k = math.fabs(180*math.acos(k)) / math.pi
                if dist < NEIGHB_RADIUS and k > VIEWING_ANGLE:
                    if math.fabs(b2.pos[1] - b1.pos[1]) > MIN_DIST:
                        b1.vel += (WEIGHT_NEIGHB_DIST / b1.l) * (((b2.pos - b1.pos) * (dist - b1.avg_dist)) / dist)
                    else:
                        b1.vel -= (WEIGHT_MIN_DIST / b1.l) * (((b2.pos - b1.pos) * MIN_DIST) / dist) - (b2.pos - b1.pos)

            if math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) > MAX_VEL:
                b1.vel = 0.75 * b1.vel

        for b in bodies:
            b.pos += b.vel * DT
            if b.vel[0] == 0:
                b.vel[0] = MAX_VEL / 1000
            if b.vel[1] == 0:
                b.vel[1] = MAX_VEL / 1000

            if b.pos[1] < 0:
                b.pos[1] = b.pos[1] % -size[1] + size[1]
            elif b.pos[1] > size[1]:
                b.pos[1] = b.pos[1] % size[1]

            if b.pos[0] < 0:
                b.pos[0] = b.pos[0] % -size[0] + size[0]
            elif b.pos[0] > size[0]:
                b.pos[0] = b.pos[0] % size[0]

            b.avg_vel = np.copy(b.vel)
            b.avg_dist = 0
            b.l = 1

        draw(scr, bodies)

        # time.sleep(0.1)


def setup_curses():
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)


def setup_stderr():
    """Hard-coded console for debug prints (stderr)"""
    sys.stderr = open('/dev/pts/1', 'w')


def eprint(*args, **kwargs):
    """Debug print function (on std err)"""
    print(*args, file=sys.stderr)


def draw(scr, bodies):
    # https://dboikliev.wordpress.com/2013/04/20/image-to-ascii-conversion/
    # http://mkweb.bcgsc.ca/asciiart/
    shape = [curses.LINES, curses.COLS - 1]
    count = np.zeros(shape=shape)

    for b in bodies:
        if b.pos[0]//4 >= curses.LINES or b.pos[1]//2 >= curses.COLS - 1:
            continue
        count[int(b.pos[0]//4), int(b.pos[1]//2)] += 1

    buf = np.full(shape=shape, fill_value=' ')
    for y in range(count.shape[0]):
        for x in range(count.shape[1]):
            if count[y][x] > 50:
                buf[y][x] = TONE_SYMBOLS[0]
            elif count[y][x] > 40:
                buf[y][x] = TONE_SYMBOLS[1]
            elif count[y][x] > 30:
                buf[y][x] = TONE_SYMBOLS[2]
            elif count[y][x] > 20:
                buf[y][x] = TONE_SYMBOLS[3]
            elif count[y][x] > 10:
                buf[y][x] = TONE_SYMBOLS[4]
            elif count[y][x] > 5:
                buf[y][x] = TONE_SYMBOLS[5]
            elif count[y][x] > 3:
                buf[y][x] = TONE_SYMBOLS[6]
            elif count[y][x] > 1:
                buf[y][x] = TONE_SYMBOLS[7]
            elif count[y][x] != 0:
                buf[y][x] = TONE_SYMBOLS[8]

    dtype = np.dtype('U' + str(buf.shape[1]))
    for num, line in enumerate(buf):
        scr.addstr(num, 0, line.view(dtype)[0])
    scr.refresh()


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
