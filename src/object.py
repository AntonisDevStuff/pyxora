from .scene import Scene
import pymunk

from inspect import stack as inspect_stack
def get_scene():
    for frame_info in inspect_stack():
        local_self = frame_info.frame.f_locals.get('self')
        if isinstance(local_self,Scene):
            return local_self
    raise RuntimeError("You can create Objects only inside a Scene")

class ObjectScript:
    def __init__(self,obj,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def start(self,obj): pass
    def update(self,obj,dt): pass
    def on_destroy(self,obj): pass
    def on_collision(self,obj,other): pass

class ObjectsPhysics:
    def __init__(self):
        self.space = pymunk.Space()
        self.shape_method = {
            1: self.add_rect,
            2: self.add_circle,
        }

    def add(self, Object):
        physics = Object.physics
        static = Object.static
        shape_type = Object.shape_type
        self.shape_method[shape_type](Object, static, **physics)

    def add_rect(self, Object, static, **rigidshape_kwargs):
        body_type = pymunk.Body.STATIC if static else pymunk.Body.DYNAMIC

        rigidbody = pymunk.Body(body_type=body_type)
        rigidbody.position = (
            Object.start_pos[0] + Object.size[0] / 2,
            Object.start_pos[1] + Object.size[1] / 2
        )

        rigidshape = pymunk.Poly.create_box(rigidbody, Object.size)
        for key, value in rigidshape_kwargs.items():
            setattr(rigidshape, key, value)

        self.space.add(rigidbody, rigidshape)

        Object.rigidbody = rigidbody
        Object.rigidshape = rigidshape

    def add_circle(self, Object, static, **rigidshape_kwargs):
        body_type = pymunk.Body.STATIC if static else pymunk.Body.DYNAMIC

        rigidbody = pymunk.Body(body_type=body_type)
        rigidbody.position = (
            Object.start_pos[0],
            Object.start_pos[1]
        )
        rigidshape = pymunk.Circle(body=rigidbody, radius=Object.size)
        for key, value in rigidshape_kwargs.items():
            setattr(rigidshape, key, value)

        self.space.add(rigidbody, rigidshape)

        Object.rigidbody = rigidbody
        Object.rigidshape = rigidshape

    def update(self, step):
        self.space.step(step)


class Objects:
    show_hitbox = pyxora.debug
    def __init__(self,render=None):
        self.data = []
        self.counter = 0

        self.Physics = ObjectsPhysics()

        scene = self.__get_scene()
        if not render:
            render = scene.Camera

        self.scene = scene
        self.render = render

    def __iter__(self):
        return iter(self.data)

    def add(self, Object):
        self.counter += 1
        Object.id = self.counter
        Object.Manager = self
        self.Physics.add(Object)
        self.data.append(Object)

    def toggle_hitbox(self):
        self.show_hitbox = not self.show_hitbox

    def remove(self, Object):
        return self.data.remove(Object)

    def pop(self, index):
        return self.data.pop(index)

    def clear(self):
        self.data.clear()
        self.Physics = ObjectsPhysics()
        self.counter = 0

    def set_gravity(self,gravity):
        self.Physics.space.gravity = gravity

    def update(self):
        dt = self.scene.dt
        self.Physics.update(dt)

        for obj in self:
            obj.update(dt)

    def draw(self):
        for obj in self:
            if not obj.visable:
                continue

            obj.image and self.render.draw_image(obj.image)
            self.show_hitbox and self.render.draw_shape(obj.hitbox,1)

class Object:
    shape = {
        1: pyxora.Rect,
        2: pyxora.Circle,
    }

    def __init__(self, pos, size, image=None, shape_type=1):
        pos = (pos[0] - size, pos[1] - size) if shape_type == 2 else (pos[0] - size[0] / 2, pos[1] - size[1] / 2)
        img_size = (size*2,size*2) if shape_type == 2 else size
        if image == "default":
            default = pyxora.Assets.data["images"]["pygame"]
            image =  pyxora.Image(pos,default,custom_size=img_size,shape_type=shape_type)
        self.image = image
        self.start_pos = pos
        self.size = size
        self.shape_type = shape_type
        self.rigidbody = self.rigidshape = None
        self.id = None
        self.visable = True

        self.scripts = []

        self.Manager = None

        self.add_physics(static=True)

    def move(self,new_pos):
        pos = self.rigidbody.position
        self.move_at(
            (pos[0]+new_pos[0],pos[1]+new_pos[1])
        )

    def move_at(self,new_pos):
        self.rigidbody.position = (new_pos[0],new_pos[1])
        self.Manager.Physics.space.reindex_shapes_for_body(self.rigidbody)
        self.static and self.Manager.Physics.space.reindex_static()

    def add_physics(self, mass=1, friction=0, elasticity=0, static=False):
        self.physics = {
            "mass": mass,
            "friction": friction,
            "elasticity": elasticity,
            "collision_type": self.shape_type,
        }
        self.static = static

    def add_script(self,script,**kwargs):
        script = script(self,**kwargs)
        self.scripts.append(script)

    def update(self, dt):
        for script in self.scripts:
            script.update(self,dt)

        if self.image:
            self.image.move_at(self.rigidbody.position)
            self.shape_type == 1 and self.image.move((-self.size[0]/2,-self.size[1]/2))
            self.shape_type == 2 and self.image.move((-self.size,-self.size))

    @property
    def hitbox(self):
        return self.shape[self.shape_type](self.pos, self.size, "red")

    @property
    def pos(self):
        pos = pyxora.vector(self.rigidbody.position[0],self.rigidbody.position[1])
        if self.shape_type == 1:
            pos.x -= self.size[0]/2
            pos.y -= self.size[1]/2
        return pos
