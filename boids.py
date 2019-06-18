#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

"""
Boids algorithm:
http://www.red3d.com/cwr/boids/

http://www.algorytm.org/sztuczna-inteligencja/boidy.html
"""

import sys
import curses
import locale
import time
import copy
import math
import numpy as np


BODY_COUNT = 50
VIEW_ANGLE = math.radians(120)
MIN_DIST = 20
VIEW_RADIUS = 50
WEIGHT_VEL = 0.1
WEIGHT_NEIGHB_DIST = 0.15
WEIGHT_MIN_DIST = 0.15
WEIGHT_NOISE = 0.1
MAX_VEL = 4
MAX_VEL_SQUARED = MAX_VEL**2
DT = 1

TONE_SYMBOLS = '@%#x+=:-. '


class Body:
    def __init__(self, screen_size):
        self.pos = np.array([np.random.uniform(0, screen_size[0]),
                             np.random.uniform(0, screen_size[1])])
        self.vel = np.random.uniform(-2, 2, size=[2])
        self.avg_vel = np.copy(self.vel)
        self.avg_dist = 0
        self.neighb_count = 1
        self.neighbors = []

    def reset(self):
        self.avg_vel = np.copy(self.vel)
        self.avg_dist = 0
        self.neighb_count = 1
        self.neighbors = []

    def adjust(self, screen_size):
        self.adjust_vel()
        self.adjust_pos(screen_size)

    def adjust_vel(self):
        if self.vel[0] == 0:
            self.vel[0] = MAX_VEL / 1000
        if self.vel[1] == 0:
            self.vel[1] = MAX_VEL / 1000

        return self.vel

    def adjust_pos(self, screen_size):
        if self.pos[0] < 0:
            self.pos[0] = self.pos[0] % -screen_size[0] + screen_size[0]
        elif self.pos[0] > screen_size[0]:
            self.pos[0] = self.pos[0] % screen_size[0]

        if self.pos[1] < 0:
            self.pos[1] = self.pos[1] % -screen_size[1] + screen_size[1]
        elif self.pos[1] > screen_size[1]:
            self.pos[1] = self.pos[1] % screen_size[1]

        return self.pos

    def mag_vel_squared(self):
        return self.vel[0]**2 + self.vel[1]**2

    def mag_vel(self):
        return math.sqrt(self.mag_vel_squared())


class KdTree:
    Y_AXIS = 0
    X_AXIS = 1

    class Node:
        def __init__(self, body):
            self.body = body
            self.rect = None
            self.lb = None
            self.rt = None

    class Task:
        def __init__(self, node, dim):
            self.node = node
            self.dim = dim

    def __init__(self, bodies, screen_size):
        self.root = None

        for body in bodies:
            self.insert(body, screen_size)

    def insert(self, body, screen_size):
        new_node = KdTree.Node(body)

        pointer = self.root
        dim = KdTree.Y_AXIS

        parent = None
        parent_dim = None

        while pointer:
            parent = pointer
            parent_dim = dim

            if np.all(parent.body.pos == new_node.body.pos):
                return

            if (parent_dim == KdTree.Y_AXIS and new_node.body.pos[0] < parent.body.pos[0]) or \
               (parent_dim == KdTree.X_AXIS and new_node.body.pos[1] < parent.body.pos[1]):
                pointer = pointer.lb
            else:
                pointer = pointer.rt
            dim = self._next_dimension(dim)

        if not parent:
            new_node.rect = Rect(0, 0, screen_size[0], screen_size[1])
            self.root = new_node
        else:
            new_node.rect = self._create_rect(parent, new_node.body.pos, parent_dim)
            if (parent_dim == KdTree.Y_AXIS and new_node.body.pos[0] < parent.body.pos[0]) or \
               (parent_dim == KdTree.X_AXIS and new_node.body.pos[1] < parent.body.pos[1]):
                parent.lb = new_node
            else:
                parent.rt = new_node

    def _create_rect(self, parent, insert_pt, parent_dim):
        rect = copy.copy(parent.rect)

        if parent_dim == KdTree.Y_AXIS:
            if insert_pt[0] < parent.body.pos[0]:
                rect.ymax = parent.body.pos[0]
            else:
                rect.ymin = parent.body.pos[0]
        else:
            if insert_pt[1] < parent.body.pos[1]:
                rect.xmax = parent.body.pos[1]
            else:
                rect.xmin = parent.body.pos[1]

        return rect

    def nearest(self, body, radius):
        # https://www.cs.cmu.edu/~ckingsf/bioinfo-lectures/kdtrees.pdf
        if self.root == None:
            return []

        result = []
        radius_squared = radius**2

        stack = [KdTree.Task(self.root, KdTree.Y_AXIS)]
        while stack:
            task = stack.pop()

            if task.node != None and task.node.body is body:
                stack.extend(self._new_tasks(task, body))
                continue

            if task.node == None or \
              task.node.rect.distance_squared(body.pos) >= radius_squared:
                continue

            dist_squared = distance_squared(body.pos, task.node.body.pos)
            if dist_squared < radius_squared:
                result.append((task.node.body, math.sqrt(dist_squared)))

            stack.extend(self._new_tasks(task, body))

        return result

    def _new_tasks(self, task, body):
        result = []
        next_dim = self._next_dimension(task.dim)

        if (task.dim == KdTree.Y_AXIS and body.pos[0] < task.node.body.pos[0]) or \
           (task.dim == KdTree.X_AXIS and body.pos[1] < task.node.body.pos[1]):
            result.append(KdTree.Task(task.node.rt, next_dim))
            result.append(KdTree.Task(task.node.lb, next_dim))
        else:
            result.append(KdTree.Task(task.node.lb, next_dim))
            result.append(KdTree.Task(task.node.rt, next_dim))

        return result

    def _next_dimension(self, dim):
        if dim == KdTree.Y_AXIS:
            return KdTree.X_AXIS
        return KdTree.Y_AXIS


class Rect:
    def __init__(self, ymin, xmin, ymax, xmax):
        self.ymin = ymin
        self.xmin = xmin
        self.ymax = ymax
        self.xmax = xmax

    def distance_squared(self, pos):
        dx = 0
        dy = 0

        if pos[0] < self.ymin:
            dy = pos[0] - self.ymin
        elif pos[0] > self.ymax:
            dy = pos[0] - self.ymax

        if pos[1] < self.xmin:
            dx = pos[1] - self.xmin
        elif pos[1] > self.xmax:
            dx = pos[1] - self.xmax

        return dx**2 + dy**2


def main3(scr):
    setup_stderr('/dev/pts/1')
    setup_curses(scr)

    np.random.seed(3145)
    screen_size = np.array([curses.LINES*4, (curses.COLS-1)*2])
    # screen_size = np.array([128, 238])
    bodies = [Body(screen_size) for _ in range(BODY_COUNT)]

    while True:
        tree = KdTree(bodies, screen_size)

        for body in bodies:
            body.reset()
            candidates = tree.nearest(body, VIEW_RADIUS)

            for neighb_body, dist in candidates:
                angle = view_angle2(body, neighb_body)
                if angle < VIEW_ANGLE:
                    body.neighbors.append((neighb_body, dist))

            body.v1 = rule1_fly_to_center(body)
            body.v2 = rule2_keep_save_dist(body)
            body.v3 = rule3_adjust_velocity(body)

        for body in bodies:
            body.vel += body.v1 + body.v2 + body.v3
            body.pos += body.vel * DT
            body.adjust(screen_size)

        draw(scr, bodies)


def rule1_fly_to_center(body):
    avg_dist = sum([dist for neighb_body, dist in body.neighbors])
    if len(body.neighbors):
        avg_dist /= len(body.neighbors)
        weight = WEIGHT_MIN_DIST/len(body.neighbors)

    # return (avg_dist - body.pos) * 0.1
    v = 0
    for neighb_body, dist in body.neighbors:
        if dist > MIN_DIST:
            v += weight * (((neighb_body.pos - body.pos) * (dist - avg_dist)) / dist)

    return v


def rule2_keep_save_dist(body):
    # c = -sum([dist for _, dist in body.neighbors if dist < MIN_DIST])
    if len(body.neighbors):
        weight = WEIGHT_NEIGHB_DIST/len(body.neighbors)

    v = 0
    for neighb_body, dist in body.neighbors:
        v += -weight * ((((neighb_body.pos - body.pos) * MIN_DIST) / dist) - (neighb_body.pos - body.pos))

    return v


def rule3_adjust_velocity(body):
    avg_vel = sum([neighb_body.vel for neighb_body, _ in body.neighbors])
    if len(body.neighbors):
        avg_vel /= len(body.neighbors)
    # return (avg_vel - body.vel) * (1/8)

    return WEIGHT_VEL * (avg_vel - body.vel)


def main2(scr):
    setup_stderr('/dev/pts/2')
    setup_curses(scr)

    np.random.seed(3145)
    screen_size = np.array([curses.LINES*4, (curses.COLS-1)*2])
    # screen_size = np.array([128, 238])
    bodies = [Body(screen_size) for _ in range(BODY_COUNT)]

    while True:
        tree = KdTree(bodies, screen_size)

        for body in bodies:
            body.reset()
            candidates = tree.nearest(body, VIEW_RADIUS)

            # visible_neighbors = []
            for neighb_body, dist in candidates:
                # angle = view_angle(body, neighb_body, dist)
                angle = view_angle2(body, neighb_body)
                if angle < VIEW_ANGLE:
                    body.avg_vel += neighb_body.vel
                    body.avg_dist += dist
                    body.neighb_count += 1
                    body.neighbors.append((neighb_body, dist))
        #           eprint('neighb_body.pos', neighb_body.pos)

        #     eprint('body.pos', body.pos)

        #     eprint('L:', body.neighb_count)
        #     # exit()


        eprint('-----')
        for body in bodies:
            body.vel += WEIGHT_VEL * ((body.avg_vel / body.neighb_count) - body.vel)
            # body.vel += WEIGHT_NOISE * np.random.uniform(0, 0.5, size=[2]) * MAX_VEL

            if body.neighb_count > 1:
                body.avg_dist /= body.neighb_count - 1

            for neighb_body, dist in body.neighbors:
                # angle = view_angle(body, neighb_body, dist)
                angle = view_angle2(body, neighb_body)
                eprint(' dist, ang: ', dist, angle)
                if angle < VIEW_ANGLE:
                    if math.fabs(neighb_body.pos[1] - body.pos[1]) > MIN_DIST:
                        body.vel += (WEIGHT_NEIGHB_DIST / body.neighb_count) * (((neighb_body.pos - body.pos) * (dist - body.avg_dist)) / dist)
                        eprint('vel', body.vel)
                    else:
                        body.vel -= (WEIGHT_MIN_DIST / body.neighb_count) * (((neighb_body.pos - body.pos) * MIN_DIST) / dist) - (neighb_body.pos - body.pos)

            if body.mag_vel_squared() > MAX_VEL_SQUARED:
                body.vel = 0.75 * body.vel


        eprint('====')
        for body in bodies:
            body.pos += body.vel * DT
            body.adjust(screen_size)

        draw(scr, bodies)


def main(scr):
    setup_stderr('/dev/pts/1')
    setup_curses(scr)

    np.random.seed(3145)
    screen_size = np.array([curses.LINES*4, (curses.COLS-1)*2])
    # screen_size = np.array([128, 238])

    bodies = [Body(screen_size) for _ in range(BODY_COUNT)]

    while True:
        for body in bodies:
            body.reset()

            for neighb_body in bodies:
                if body is neighb_body:
                    continue

                dist = distance(body.pos, neighb_body.pos)
                # angle = view_angle(body, neighb_body, dist)
                angle = view_angle2(body, neighb_body)
                # eprint(' dist, ang: ', dist, angle)
                if dist < VIEW_RADIUS and angle < VIEW_ANGLE:
                    # eprint(' ENTER')
                    body.neighb_count += 1
                    body.avg_vel += neighb_body.vel
                    body.avg_dist += dist
            #         eprint('neighb_body.pos', neighb_body.pos)

            # eprint('body.pos', body.pos)
            # eprint('L:', body.neighb_count)
            # exit()


        eprint('-----')
        for body in bodies:
            body.vel += WEIGHT_VEL * ((body.avg_vel / body.neighb_count) - body.vel)
            # body.vel += WEIGHT_NOISE * np.random.uniform(0, 0.5, size=[2]) * MAX_VEL

            if body.neighb_count > 1:
                body.avg_dist /= body.neighb_count - 1

            for neighb_body in bodies:
                if body is neighb_body:
                    continue

                dist = distance(body.pos, neighb_body.pos)
                # angle = view_angle(body, neighb_body, dist)
                angle = view_angle2(body, neighb_body)
                eprint(' dist, ang: ', dist, angle)
                if dist < VIEW_RADIUS and angle < VIEW_ANGLE:
                    if math.fabs(neighb_body.pos[1] - body.pos[1]) > MIN_DIST:
                        body.vel += (WEIGHT_NEIGHB_DIST / body.neighb_count) * (((neighb_body.pos - body.pos) * (dist - body.avg_dist)) / dist)
                        eprint('vel', body.vel)
                    else:
                        body.vel -= (WEIGHT_MIN_DIST / body.neighb_count) * (((neighb_body.pos - body.pos) * MIN_DIST) / dist) - (neighb_body.pos - body.pos)

            if body.mag_vel_squared() > MAX_VEL_SQUARED:
                body.vel = 0.75 * body.vel


        eprint('====')
        for body in bodies:
            body.pos += body.vel * DT
            body.adjust(screen_size)

        draw(scr, bodies)
        # time.sleep(0.1)


def setup_curses(scr):
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)
    scr.clear()


def setup_stderr(output):
    """Hard-coded console for debug prints (stderr)."""
    sys.stderr = open(output, 'w')


def eprint(*args, **kwargs):
    """Debug print function (on std err)."""
    print(*args, file=sys.stderr)


def distance_squared(pos1, pos2):
    return (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2


def distance(pos1, pos2):
    return math.sqrt(distance_squared(pos1, pos2))


def view_angle(body1, body2, dist):
    mag_vel = body1.mag_vel()
    k = body1.vel[1] / mag_vel * \
        ((body2.pos[1] - body1.pos[1]) / dist) + \
        body1.vel[0] / mag_vel * \
        ((body2.pos[0] - body1.pos[0]) / dist)

    if k < -1:
        k = -1
    elif k > 1:
        k = 1
    angle = math.fabs((180 * math.acos(k)) / math.pi)

    return angle


def view_angle2(body1, body2):
    k1 = math.atan2(body1.vel[0], body1.vel[1])
    k2 = math.atan2(body1.pos[0] - body2.pos[0], body1.pos[1] - body2.pos[1])

    diff = math.fabs(k1 - k2)
    return diff


def draw(scr, bodies):
    # https://dboikliev.wordpress.com/2013/04/20/image-to-ascii-conversion/
    # http://mkweb.bcgsc.ca/asciiart/
    shape = [curses.LINES, curses.COLS - 1]
    count = np.zeros(shape=shape)

    for b in bodies:
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
    curses.wrapper(main3)
    # main3(None)