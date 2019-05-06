import bpy
import time
import json


FRAME_INTERVAL = 0.0333333
CLEAN_AFTER_FINISH = True

ROOT_FOLDER = '/Users/rightpeter/Development/study/UIUC/CS543/Project/CS543/data/coords'
PIC_ORIENTATION = (1.57, 0, 0)
scale = (2, 2, 2)
IMAGE_NUM = 2639

with open(ROOT_FOLDER + '/coords.json') as f:
    coord = json.load(f)


def create_worker(worker):
    obj = bpy.data.objects.new(worker['id'], None)

    obj.location = (worker['coord'][0] / 100, -1 * worker['coord'][1] / 100, 0)

    obj.rotation_euler = PIC_ORIENTATION
    obj.scale = scale
    obj.empty_draw_type = 'IMAGE'
    pic_name = worker['id'] + '.png'
    img = bpy.data.images.load(ROOT_FOLDER + '/corpped/' + pic_name)
    obj.data = img

    return obj


class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def __init__(self):
        self.k = 0
        self.objs = bpy.data.objects
        self.scene = bpy.context.scene 
        self.previous_workers = []
        self.play = True
        self.start_time = time.time()
        #self.coord = coord

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            if CLEAN_AFTER_FINISH:
                for worker in self.previous_workers:
                    self.objs.remove(self.objs[worker], True)
            return {'CANCELLED'}

        if self.k == IMAGE_NUM:
            self.cancel(context)
            return {'END'}

        if event.type == 'SPACE':
            self.play = not self.play

        if event.type == 'TIMER':
            if not self.play:
                return {'PASS_THROUGH'}

            # print('previous_workers: ', self.previous_workers)
            for worker in self.previous_workers:
                self.objs.remove(self.objs[worker], True)

            self.scene.update()
            self.previous_workers = []
            worers = coord[str(self.k)]
            # print('workers: ', worers)
            for _, worker in worers.items():
                # print(worker)
                self.previous_workers.append(worker['id'])
                self.obj = create_worker(worker)
                self.scene.objects.link(self.obj)
            self.k += 1

        return {'PASS_THROUGH'}

    def execute(self, context):

        wm = context.window_manager
        self._timer = wm.event_timer_add(FRAME_INTERVAL, context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def register():

    bpy.utils.register_class(ModalTimerOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.wm.modal_timer_operator()
