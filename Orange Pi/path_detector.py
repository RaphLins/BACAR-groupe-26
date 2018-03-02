import logging
import numpy as np
import cv2

from scipy import ndimage
from math import sin, cos, pi

logging.info('Path detector 1.0 has been initialized')


def detect(mask):

    img_height, img_width = mask.shape
    car_center = (img_width // 2, img_height)
    path_img = np.zeros((img_height, img_width, 3), np.uint8)
    cv2.circle(path_img, car_center, 4, (0, 0, 252), -1)

    # recherche des directions possible et les met dans path_dict:
    # la partie importante du code se trouve dans la fonction find_directions()
    path_dict, path_img = find_directions(mask, path_img, car_center)
    max_left, max_right = find_min_max(mask, path_img, car_center)
    for key in path_dict.keys():
        angle = path_dict[key]
        if angle is not None:
            if angle < max_right:
                path_dict[key] = max_right
            elif angle > max_left:
                path_dict[key] = max_left
    path_dict["max_right"] = max_right
    path_dict["max_left"] = max_left
    return (path_dict, path_img)


def find_directions(mask, path_img, car_center):
    """renvoie un dictionnaire avec des listes des directions possibles
    triees en 3 directions principales: gauche, tout droit et droite"""
    last = False
    img_height, img_width = mask.shape
    path_dict = {'left': None, 'straight': None, 'right': None}
    currentDirection = []
    center = img_width//2, int(img_height*0.4)
    r = img_height*0.4
    # la boucle for recherche les chemins libres dans chaque direction
    angle = -10
    while angle < 190:
        p = int(center[0]+r*cos(angle*pi/180)), int(center[1]-r*sin(angle*pi/180))
        # verifie si le chemin dans la direction de p est libre
        edge = find_edge(mask, center, p)
        if edge[1] == 100:
            # si le chemin est libre, on ajoute le point dans la liste currentDirection
            if not last:
                currentDirection = [(edge[0], angle)]
            else:
                currentDirection.append((edge[0], angle))
            last = True
        else:
            if last:
                # on passe d'une ligne libre a une ligne non-libre
                # donc c'est la fin de la liste currentDirection
                # donc on prend le milieu de currentDirection comme direction moyenne
                middle = currentDirection[len(currentDirection)//2]
                midle_angle = middle[1]
                direction = "straight"
                if midle_angle > 130:
                    direction = "left"
                elif midle_angle < 50:
                    direction = "right"
                cv2.circle(path_img, middle[0], 4, (0, 0, 255), -1)
                # on ajoute l'angle correspondant a cette direction dans le dictionnaire
                # utilise la fonction regularize() pour que l'angle ne soit pas dirige vers l'exterieur de la route
                path_dict[direction] = model_to_heading(middle[0], car_center)
            last = False

        cv2.circle(path_img, edge[0], 4, (0, 255, 0), -1)
        cv2.line(path_img, center, p, (255, 0, 0))
        angle += 6
    return (path_dict, path_img)


def find_min_max(mask, path_img, car_center):
    img_height, img_width = mask.shape
    right_edge = (0, 0)
    left_edge = (0, 0)
    r = img_height*0.4
    center = car_center
    lst = []
    angle = 45
    while angle < 135:
        origin = p = int(center[0]+r*cos(angle*pi/180)*0.4), int(center[1]-r*sin(angle*pi/180)*0.4)
        p = int(center[0]+r*cos(angle*pi/180)), int(center[1]-r*sin(angle*pi/180))
        # verifie si le chemin dans la direction de p est libre
        edge = find_edge(mask, origin, p)
        if edge[1] == 100:
            lst.append(edge[0])
        cv2.line(path_img, origin, p, (255, 0, 0))
        angle += 5
    if len(lst) > 3:
        right_edge = lst[3]
        left_edge = lst[-3]
    else:
        right_edge = left_edge = img_width//2, 0
    cv2.circle(path_img, right_edge, 4, (0, 255, 0), -1)
    cv2.circle(path_img, left_edge, 4, (0, 255, 0), -1)
    return model_to_heading(left_edge, car_center), model_to_heading(right_edge, car_center)


def find_edge(mask, p0, p1):
    """trouve le bord de la route dans la direction p0->p1, renvoie un tuple avec le point et sa distance (de 0 100)"""
    x_tab, y_tab, line_tab = profile(mask, p0, p1, 100)
    non_zero = np.nonzero(line_tab)[0]
    while non_zero.size > 4:
        n = non_zero[0]
        found=True
        for i in range(1,4):
        	if not n==non_zero[i]-i and found:
        		non_zero=np.delete(non_zero,0)
        		found=False
        if found:
        	return [(int(x_tab[n]), int(y_tab[n])), n]

    return [p1, 100]


def model_to_heading(model_xy, car_center_xy):
    """Calculate the angle (in degrees) between the vertical line that
       passes through the point `car_center_xy` and the line that connects
       `car_center_xy` with `model_xy`.
       A negative angle means that the car should turn clockwise; a positive
       angle that the car should move counter-clockwise."""
    dx = 1. * model_xy[0] - car_center_xy[0]
    dy = 1. * model_xy[1] - car_center_xy[1]
    heading = -np.arctan2(dx, -dy)*180/np.pi
    return heading


def profile(mask, p0, p1, num):
    """Takes `num` equi-distance samples on the straight line between point `p0`
       and point `p2` on binary image `mask`.

       Here, points p0 and p1 are 2D points (x-coord,y-coord)

       Returns: a triple (n, m, vals) where:
       - n is a numpy array of size `num` containing the x-coordinates of
         sampled points
       - m is a numpy array of size `num` containing the y-coordinates of
         sampled points
       - vals is a numpy array of size `num` containing the sampled point
         values, i.e.  vals[i] = mask[m[i], n[i]]
         (recall that images are indexed first on y-coordinate, then on
          x-coordinate)
     """
    n = np.linspace(p0[0], p1[0], num)
    m = np.linspace(p0[1], p1[1], num)
    return [n, m, ndimage.map_coordinates(mask, [m, n], order=0)]
