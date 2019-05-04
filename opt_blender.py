import bpy
import time
import json

def create_worker(worker):
    obj = bpy.data.objects.new(worker['id'], None)

    obj.location = (worker['coord'][0]/100, -1*worker['coord'][1]/100, 0)

    obj.rotation_euler = PIC_ORIENTATION
    obj.scale = scale 
    obj.empty_draw_type = 'IMAGE'
    pic_name = worker['id'] + '.png'
    img = bpy.data.images.load(ROOT_FOLDER + '\\corpped\\' + pic_name)
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
        #self.coord = coord
                

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}
        if self.k == IMAGE_NUM:
            self.cancel(context)
            return {'END'}

        # previous_workers = []
        if event.type == 'TIMER':
            print('previous_workers: ', self.previous_workers)
            for worker in self.previous_workers:
                self.objs.remove(self.objs[worker], True)

            self.scene.update()
            self.previous_workers = []
            worers = coord[str(self.k)]
            print('workers: ', worers)
            for _, worker in worers.items():
                print(worker)
                self.previous_workers.append(worker['id'])
                self.obj = create_worker(worker)
                self.scene.objects.link(self.obj)
            self.k += 1 

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def register():

    bpy.utils.register_class(ModalTimerOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)

ROOT_FOLDER = 'c:\\users\\lhh97\\desktop\\CS543\\coords'
#SLEEP_TIME = 0.2
PIC_ORIENTATION = (1.57, 0, 0)
scale = (2,2,2)
IMAGE_NUM = 2639

with open(ROOT_FOLDER + '\\coords.json') as f:
    coord = json.load(f)

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.wm.modal_timer_operator()
