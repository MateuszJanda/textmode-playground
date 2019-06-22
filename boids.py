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
http://www.kfish.org/boids/pseudocode.html
"""

import sys
import curses
import locale
import time
import copy
import math
import heapq
import numpy as np


BODY_COUNT = 100
VIEW_ANGLE = math.radians(120)
MIN_DIST = 20
VIEW_RADIUS = 30
WEIGHT_VEL = 0.1
WEIGHT_NEIGHB_DIST = 0.15
WEIGHT_MIN_DIST = 0.15
# WEIGHT_NOISE = 0.1
MAX_VEL = 4
MAX_VEL_SQUARED = MAX_VEL**2

NUM_AXIS = 2
Y_AXIS = 0
X_AXIS = 1
DT = 1


# https://dboikliev.wordpress.com/2013/04/20/image-to-ascii-conversion/
# http://mkweb.bcgsc.ca/asciiart/
TONE_SYMBOLS = [
    (15, '@'),
    (14, '%'),
    (13, '$'),
    (12, '#'),
    (11, 'x'),
    (10, '?'),
    (9, '*'),
    (8, '!'),
    (7, '+'),
    (6, ';'),
    (5, '='),
    (4, ':'),
    (3, '-'),
    (2, ","),
    (1, '.'),
]


class Body:
    EPSILON = 0.1
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.pos = np.array([np.random.uniform(0, screen_size[Y_AXIS]),
                             np.random.uniform(0, screen_size[X_AXIS])])
        self.vel = np.random.uniform(-2, 2, size=[NUM_AXIS])
        self.neighbors = []

    def adjust(self):
        self.adjust_vel()
        self.adjust_pos()

    def adjust_vel(self):
        if np.any(np.absolute(self.vel) > Body.EPSILON):
            return

        for axis in range(NUM_AXIS):
            self.vel[axis] = max(self.vel[axis], MAX_VEL / 1000)

    def adjust_pos(self):
        for axis in range(NUM_AXIS):
            if self.pos[axis] < 0:
                self.pos[axis] = self.pos[axis] % -self.screen_size[axis] + self.screen_size[axis]
            elif self.pos[axis] > self.screen_size[axis]:
                self.pos[axis] = self.pos[axis] % self.screen_size[axis]


class KdTree:
    """
    http://web.stanford.edu/class/cs106l/handouts/005_assignment_3_kdtree.pdf
    https://www.cs.cmu.edu/~ckingsf/bioinfo-lectures/kdtrees.pdf
    """

    class Node:
        def __init__(self, body):
            self.body = body
            self.left = None
            self.right = None

    class Task:
        def __init__(self, node, axis):
            self.node = node
            self.axis = axis

    def __init__(self, bodies, k=55):
        self.root = None
        self.k = k
        self.height = 0
        self.compares_count = 0

        for body in bodies:
            self.insert(body)

    def insert(self, body):
        new_node = KdTree.Node(body)

        pointer = self.root
        axis = Y_AXIS
        new_node_height = 1

        parent = None
        parent_axis = None

        while pointer:
            parent = pointer
            parent_axis = axis

            if np.all(parent.body.pos == new_node.body.pos):
                return

            if new_node.body.pos[parent_axis] < parent.body.pos[parent_axis]:
                pointer = pointer.left
            else:
                pointer = pointer.right
            axis = self._next_axis(axis)
            new_node_height += 1

        if not parent:
            self.root = new_node
        else:
            if new_node.body.pos[parent_axis] < parent.body.pos[parent_axis]:
                parent.left = new_node
            else:
                parent.right = new_node

        if new_node_height > self.height:
            self.height = new_node_height

    def nearest(self, body, radius):
        if self.root == None:
            return []

        neighbors = []
        radius_squared = radius**2

        stack = [KdTree.Task(self.root, Y_AXIS)]
        while stack:
            task = stack.pop()
            self.compares_count += 1

            if task.node == None:
                continue

            if task.node.body is body:
                stack.extend(self._new_tasks(task, body, radius))
                continue

            dist_squared = distance_squared(body.pos, task.node.body.pos)
            if dist_squared < radius_squared:
                neighbors.append((dist_squared, task.node.body))

            stack.extend(self._new_tasks(task, body, radius))

        return neighbors

    def _new_tasks(self, task, body, radius):
        tasks = []
        next_axis = self._next_axis(task.axis)

        if body.pos[task.axis] < task.node.body.pos[task.axis]:
            tasks.append(KdTree.Task(task.node.left, next_axis))
            other_subtree = task.node.right
        else:
            tasks.append(KdTree.Task(task.node.right, next_axis))
            other_subtree = task.node.left

        if math.fabs(body.pos[task.axis] - task.node.body.pos[task.axis]) < radius:
            tasks.append(KdTree.Task(other_subtree, next_axis))

        return tasks

    def k_nearest(self, body, radius):
        if self.root == None:
            return []

        neighbors = []
        radius_squared = radius**2

        stack = [KdTree.Task(self.root, Y_AXIS)]
        while stack:
            task = stack.pop()
            self.compares_count += 1

            if task.node == None:
                continue

            if task.node.body is body:
                stack.extend(self._new_knn_tasks(task, body, radius, neighbors))
                continue

            dist_squared = distance_squared(body.pos, task.node.body.pos)
            if dist_squared < radius_squared:
                if len(neighbors) < self.k:
                    heapq.heappush(neighbors, (-dist_squared, task.node.body))
                elif dist_squared < -neighbors[0][0]:
                    heapq.heapreplace(neighbors, (-dist_squared, task.node.body))

            stack.extend(self._new_knn_tasks(task, body, radius, neighbors))

        return neighbors

    def _new_knn_tasks(self, task, body, radius, neighbors):
        tasks = []
        next_axis = self._next_axis(task.axis)

        if body.pos[task.axis] < task.node.body.pos[task.axis]:
            tasks.append(KdTree.Task(task.node.left, next_axis))
            other_subtree = task.node.right
        else:
            tasks.append(KdTree.Task(task.node.right, next_axis))
            other_subtree = task.node.left

        if len(neighbors) < self.k:
            if math.fabs(body.pos[task.axis] - task.node.body.pos[task.axis]) < radius:
                tasks.append(KdTree.Task(other_subtree, next_axis))
        elif math.fabs(body.pos[task.axis] - task.node.body.pos[task.axis]) < -neighbors[0][0]:
            tasks.append(KdTree.Task(other_subtree, next_axis))

        return tasks

    def _next_axis(self, axis):
        return (axis + 1) % NUM_AXIS


def main(scr):
    setup_stderr('/dev/pts/1')
    setup_curses(scr)

    np.random.seed(3145)
    screen_size = np.array([curses.LINES*4, (curses.COLS-1)*2])
    bodies = [Body(screen_size) for _ in range(BODY_COUNT)]

    while True:
        tic = time.time()
        tree = KdTree(bodies)

        for body in bodies:
            candidates = tree.nearest(body, VIEW_RADIUS)

            body.neighbors = []
            for dist_squared, neighb_body in candidates:
                angle = view_angle_2d(body, neighb_body)
                if angle < VIEW_ANGLE:
                    body.neighbors.append((neighb_body, math.sqrt(dist_squared)))

            body.v1 = rule1_fly_to_center(body)
            body.v2 = rule2_keep_safe_dist(body)
            body.v3 = rule3_adjust_velocity(body)

        for body in bodies:
            body.vel += body.v1 + body.v2 + body.v3
            body.pos += body.vel * DT
            body.adjust()

        calc_time = time.time() - tic

        draw(scr=scr, bodies=bodies, tree_height=tree.height,
            optimal_height=math.ceil(math.log(len(bodies), 2)),
            compares_count=tree.compares_count, calc_time=calc_time)


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
    """Debug print function (on stderr)."""
    print(*args, file=sys.stderr)


def rule1_fly_to_center(body):
    avg_dist = sum([dist for _, dist in body.neighbors])
    if len(body.neighbors):
        avg_dist /= len(body.neighbors)
        weight = WEIGHT_MIN_DIST/len(body.neighbors)

    v = 0
    for neighb_body, dist in body.neighbors:
        if dist > MIN_DIST:
            v += weight * (((neighb_body.pos - body.pos) * (dist - avg_dist)) / dist)

    return v


def rule2_keep_safe_dist(body):
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

    return WEIGHT_VEL * (avg_vel - body.vel)


def distance_squared(pos1, pos2):
    return (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2


def distance(pos1, pos2):
    return math.sqrt(distance_squared(pos1, pos2))


def view_angle_2d(body1, body2):
    k1 = math.atan2(body1.vel[0], body1.vel[1])
    k2 = math.atan2(body1.pos[0] - body2.pos[0], body1.pos[1] - body2.pos[1])

    diff = math.fabs(k1 - k2)
    return diff


def view_angle_nd(body1, body2):
    """Terrible, terrible slows."""
    mag_vec1 = np.sum(body1.vel**2)**0.5
    mag_vec2 = np.sum(body2.pos**2)**0.5
    angle = np.arccos(np.dot(body1.vel, body2.pos) / (mag_vec1 * mag_vec2))
    return angle


def draw(scr, bodies, tree_height, optimal_height, compares_count, calc_time):
    buf = symbol_array(bodies)

    dtype = np.dtype('U' + str(buf.shape[1]))
    for num, line in enumerate(buf):
        scr.addstr(num, 0, line.view(dtype)[0])

    scr.addstr(0, 0, 'Total bodies: %d. Tree height: %2d, optimal: %d. Cmp: %5d. Calc time: %.4f sec' %
        (len(bodies), tree_height, optimal_height, compares_count, calc_time))
    scr.refresh()


def symbol_array(bodies):
    shape = [curses.LINES, curses.COLS - 1]
    count = np.zeros(shape=shape)

    for b in bodies:
        count[int(b.pos[0]//4), int(b.pos[1]//2)] += 1

    buf = np.full(shape=shape, fill_value=' ')
    for y in range(count.shape[0]):
        for x in range(count.shape[1]):
            if count[y][x] == 0:
                continue

            for threshold, symbol in TONE_SYMBOLS:
                if count[y][x] >= threshold:
                    buf[y][x] = symbol
                    break
    return buf


def main_test():
    screen_size = [100, 100]

    b1 = Body(screen_size)
    b1.pos = np.array([0,0])
    b1.vel = np.array([0,1])
    b2 = Body(screen_size)
    b2.pos = np.array([1,-1])
    print(math.degrees(view_angle_2d(b1, b2)), math.degrees(view_angle_nd(b1, b2)))
    print(math.degrees(view_angle_nd(b1, b2)))
    print('---')

    tree = KdTree([])

    for pos in [(51,75), (25,40), (70,70), (10,30), (35,90), (55,1), (60,80), (1,10), (50,50) ]:
    # for pos in [(1,9), (2,3),(4,1),(3,7),(5,4),(6,8),(7,2),(8,8),(7,9),(9,6)]:
        b = Body(screen_size)
        b.pos = np.array(pos)
        tree.insert(b)

    b = Body(screen_size)
    b.pos = np.array([53,75])
    # b.pos = np.array([7,4])
    for d, b in tree.nearest(b, 3):
        print('Found', b.pos)
    print('compares_count', tree.compares_count)

    left = tree.root
    while left:
        print(left.body.pos)
        left = left.left
    print('---')

    right = tree.root
    while right:
        print(right.body.pos)
        right = right.right


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
    # main_test()
