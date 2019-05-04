import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


import cv2
import numpy as np
import argparse

import skimage
import skimage.transform
import pickle

marked_points = []
premarked_points = [[214, 147], [309, 146], [513, 107], [325, 190], [599, 208],
                    [462, 302], [593, 301]]
target_points = [[0, 605], [336, 605], [1152, 0], [411, 1066.5], [1162, 1241.5],
                 [742, 1778.5], [1001, 1778.5]]


def show_image(img, name="", gray=False, dpi=300):
    plt.figure(dpi=dpi)
    if gray:
        plt.imshow(img, "gray")
    else:
        plt.imshow(img)

    if name:
        if gray:
            plt.imsave(output_folder + name, img, cmap='gray')
        else:
            plt.imsave(output_folder + name, img)


def draw_circle(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(f'x: {x}, y: {y}')
        marked_points.append([x, y])
        cv2.circle(img_global, (x, y), 2, (0, 0, 255), -1)
        cv2.imshow("image", img_global)


def calculate_homography(marked_points, target_points):
    A = []
    for i in range(7):
        pt1 = marked_points[i]
        pt2 = target_points[i]
        A.append([
            0, 0, 0, pt1[0], pt1[1], 1, -pt1[0] * pt2[1], -pt1[1] * pt2[1],
            -pt2[1]
        ])
        A.append([
            pt1[0], pt1[1], 1, 0, 0, 0, -pt1[0] * pt2[0], -pt1[1] * pt2[0],
            -pt2[0]
        ])

    A = np.matrix(A)

    U, S, V = np.linalg.svd(A)

    H = np.reshape(V[-1], (3, 3))
    H = H / H[2, 2]

    return np.array(H)


def show_res(img, transform):
    r, c = img.shape[:2]
    # corners = np.array([[0, 0], [0, r], [c, 0], [c, r]])
    # warped_corners = transform(corners)

    # corner_min = np.min(warped_corners, axis=0)
    corner_min = np.array([-40, -40])
    print(f'corner_min: {corner_min}')
    # corner_max = np.max(warped_corners, axis=0)
    corner_max = np.array([1200, 1900])
    print(f'corner_max: {corner_max}')

    output_shape = (corner_max - corner_min)
    output_shape = np.ceil(output_shape[::-1])

    offset = skimage.transform.SimilarityTransform(translation=-corner_min)

    img_ = skimage.transform.warp(img, (transform + offset).inverse, output_shape=output_shape, cval=-1)
    # img_ = img_.astype('uint8')
    # img_ = cv2.cvtColor(img_, cv2.COLOR_BGR2RGB)
    # show_image(img_, "test.jpg")
    # plt.show()

    # print(f'img_: \n{img_}')
    print(np.max(img_))
    cv2.imwrite("test.png", img_)
    cv2.imshow("image", img_)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def fit_transmission(img, marked_points, target_points):
    print(f'marked_points: {marked_points}')
    H = calculate_homography(marked_points, target_points)
    print(f'H: {H}')

    with open('H.pk', 'wb') as f:
        pickle.dump(H, f)

    transform = skimage.transform.ProjectiveTransform(H)
    show_res(img, transform)


def mark_points(img):
    global img_global
    img_global = img.copy()

    cv2.imshow("image", img_global)
    cv2.setMouseCallback("image", draw_circle)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    global marked_points
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="Path to the image")
    ap.add_argument("-m", "--mark", default=False, help="Path to the image")
    args = vars(ap.parse_args())

    img = cv2.imread(args['image'])

    if args["mark"]:
        mark_points(img)
    else:
        marked_points = premarked_points

    fit_transmission(img, marked_points, target_points)


if __name__ == '__main__':
    main()
