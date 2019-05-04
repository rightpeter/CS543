#!/usr/bin/env python3

import json
import numpy as np
from PIL import Image
import pickle

FILE_PATH = 'data/'
IMG_NUM = 2639
CONFIDENCE_THRESHOLD = 0.2
X_MARGIN = 5
Y_MARGIN = 10


def cal_footpoint(foot):
    # print("foot: ")
    # print(foot)
    count = 0
    foot_sum = [0, 0, 0]
    for part in foot:
        if part[2] == 0:
            continue

        count += 1
        foot_sum += part

    if count != 0:
        foot_sum /= count
    return foot_sum


def extract_workers(folder_name):
    with open('H.pk', 'rb') as f:
        H = pickle.load(f)

    coords = {}

    for i in range(IMG_NUM + 1):
    # for i in range(2515, 2516):
        json_name = FILE_PATH + f'/{folder_name}/{i}_keypoints.json'
        pic_name = FILE_PATH + f'/{folder_name}/{i}_rendered.png'

        pic = Image.open(pic_name)
        w, h = pic.size

        with open(json_name, 'r') as f:
            keypoints = json.load(f)

        count = 0
        tmp_dict = {}
        for worker in keypoints['people']:
            keypoint = np.array(worker['pose_keypoints_2d']).reshape((-1, 3))[:25]
            # print("keypoint: ")
            # print(keypoint)
            confidence = np.average(keypoint, axis=0)[2]

            if confidence < CONFIDENCE_THRESHOLD:
                continue

            left_footpoint = cal_footpoint(np.vstack(([keypoint[14]], keypoint[19:22])))
            right_footpoint = cal_footpoint(np.vstack(([keypoint[11]], keypoint[22:25])))

            center_footpoint = cal_footpoint([left_footpoint, right_footpoint])[:2]
            print(f'center_footpoint: {center_footpoint}')

            keypoint = keypoint[~np.all(keypoint == 0, axis=1)]
            min_X, min_Y = np.min(keypoint, axis=0)[:2]
            avg_X, avg_Y = np.average(keypoint, axis=0)[:2]
            max_X, max_Y = np.max(keypoint, axis=0)[:2]

            min_X = min_X - X_MARGIN
            min_X = max(min_X, 0)
            min_Y = min_Y - Y_MARGIN
            min_Y = max(min_Y, 0)
            max_X = max_X + X_MARGIN
            max_X = min(max_X, w)
            max_Y = max_Y + Y_MARGIN
            max_Y = min(max_Y, h)

            corpped_pic = pic.crop((min_X, min_Y, max_X, max_Y))
            corpped_pic.save(FILE_PATH + f'/{folder_name}/corpped/{i}_{count}.png')

            if center_footpoint[0] == 0 and center_footpoint[1] == 0:
                center_footpoint[0] = avg_X
                center_footpoint[1] = min(max_Y, h)

            center_footpoint = np.hstack((center_footpoint, [1]))
            center_footpoint = np.dot(H, center_footpoint)
            center_footpoint /= center_footpoint[2]
            center_footpoint = center_footpoint[:2]

            tmp_dict[f'{count}'] = {
                'id': f'{i}_{count}',
                'coord': center_footpoint.tolist()
            }

            count += 1

        print(tmp_dict)
        coords[f'{i}'] = tmp_dict

    with open(FILE_PATH + f'/{folder_name}/coords.json', 'w+') as f:
        json.dump(coords, f)


def main():
    extract_workers('output_186')


if __name__ == '__main__':
    main()
