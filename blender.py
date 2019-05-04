import bpy
import time
import json

ROOT_FOLDER = 'c:\\users\\lhh97\\desktop\\CS543'
SLEEP_TIME = 0.2
PIC_ORIENTATION = (0, 1, 0)


def create_worker(worker):
    obj = bpy.data.objects.new(worker['id'], None)

    obj.location = tuple(worker['coord'])
    obj.rotation_euler = PIC_ORIENTATION
    obj.empty_draw_type = 'IMAGE'
    pic_name = worker['id'] + '.jpg'
    img = bpy.data.images.load(ROOT_FOLDER + '\\' + pic_name)
    obj.data = img

    return obj


def main():
    with open(ROOT_FOLDER + '\\blender.json') as f:
        coord = json.load(f)

    objs = bpy.data.objects
    scene = bpy.context.scene

    previous_workers = []
    for k in sorted(coord.keys()):
        for worker in previous_workers:
            objs.remove(objs[worker], True)

        scene.update()
        previous_workers = []

        workers = coord[k]
        for _, worker in workers.items():
            previous_workers.append(worker['id'])
            obj = create_worker(worker)
            scene.objects.link(obj)

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
