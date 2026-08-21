"""Script that handles all the object rendering."""

import numpy
import functools
from panda3d.core import PandaNode, NodePath
from direct.showbase.ShowBase import ShowBase
from sim.utils.functions import (
    set_attr_from_configuration,
    accept_ndarrays,
    unbox_1d_ndarray_list,
)
from sim.utils.builder import BuilderTemplate

from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletDebugNode
from panda3d.core import Vec3


class RenderableObject:
    """Configuration and Panda3D node references shared by rendered objects."""

    def __init__(self):
        self.name = ""

        self._position = [0, 0, 0]
        self._orientation = [0, 0, 0]
        self._color = [255, 255, 255]  # In the format of RGB
        self._scale = 1

        self._model_orientation = [0, 0, 0]
        self._model_position = [0, 0, 0]

        self.object_node = None
        self.object_node_path = None
        self.parent_node_path = None

        self.geometry_body = None
        self._mass = None

        self.model_node = None
        self.model_node_path = None

        self.model: str = ""
        self.animations: list = []
        self.textures: list = []
        
        self.geometry_shape = None
        self.geometry_args = None

        self.hidden = False

        # This class does all physics and math done by PyBullet

    @property
    def position(self):
        return self._position

    @position.setter
    @accept_ndarrays
    def position(self, value):
        if not isinstance(value, (list, numpy.ndarray)):
            raise TypeError(
                f"Position must be a list in [x, y, z] format, not type {type(value)}"
            )
        if len(value) != 3:
            raise ValueError("Position must be a list in [x, y, z] format.")


        self._position = unbox_1d_ndarray_list(value)

        if self.object_node_path is not None:
            self.object_node_path.setPos(
                self._position[0], self._position[1], self._position[2]
            )

    @accept_ndarrays
    def set_global_position(self, position):
        """Sets the position of a node relitive to render"""
        # Alias to pair with relative version
        self.position = position
    
    @accept_ndarrays
    @staticmethod
    def set_relative_position(self, nodePath, position: list):
        """Sets the position of a node relitive to another node"""
        if not isinstance(position, (list, numpy.ndarray)):
            raise TypeError(
                f"Position must be a list in [x, y, z] format, not type {type(position)}"
            )
        if len(position) != 3:
            raise ValueError("Position must be a list in [x, y, z] format.")
            
        self.object_node_path.setPos(
            nodePath,
            position[0],
            position[1],
            position[2],
        )
        self._position = self.object_node_path.getPos()

    @property
    def orientation(self):
        """Getter for a RenderableObjectBuilder's orientation"""
        return self._orientation

    @orientation.setter
    @accept_ndarrays
    def orientation(self, value):
        """Setter for a RenderableObjectBuilder's orientation"""
        if not isinstance(value, list):
            raise TypeError("Orientation must be a list in [x, y, z] format.")
        if len(value) != 3:
            raise ValueError("Orientation must be a list in [x, y, z] format.")
        self._orientation = unbox_1d_ndarray_list(value)
        if self.object_node_path is not None:
            self.object_node_path.setHpr(
                self._orientation[0], self._orientation[1], self._orientation[2]
            )
            
    @accept_ndarrays
    def set_relative_orientation(self, nodePath, orientation: list):
        """Sets the orientation of a node relitive to another node"""
        if not isinstance(orientation, (list, numpy.ndarray)):
            raise TypeError(
                f"Position must be a list in [x, y, z] format, not type {type(orientation)}"
            )
        if len(orientation) != 3:
            raise ValueError("Position must be a list in [x, y, z] format.")
            
        self.object_node_path.setPos(
            nodePath,
            orientation[0],
            orientation[1],
            orientation[2],
        )
        self._orientation = self.object_node_path.getHpr()


    @property
    def color(self):
        """Getter for a RenderableObjectBuilder's color array"""
        return self._color

    @color.setter
    @accept_ndarrays
    def color(self, value):
        """Setter for a RenderableObjectBuilder's color array"""
        if not isinstance(value, list):
            raise TypeError("Color must a list in the format of [R, G, B]")
        if len(value) != 3:
            raise ValueError("Color must a list in the format of [R, G, B]")
        for i in value:
            # if not isinstance(value, (int, float)):
            #     raise TypeError(f"Color values must be either an integer or float, not {type(i)}")
            if i > 255:
                raise ValueError("Color values cannot go over 255")
            if i < 0:
                raise ValueError("Color values cannot be negative")
        self._color = unbox_1d_ndarray_list(value)
        if self.object_node_path is not None:
            self.object_node_path.setColor(
                self._color[0], self._color[1], self._color[2], 1
            )

    @property
    def scale(self):
        """Getter for a RenderableObjectBuilder's scale"""
        return self._scale

    @scale.setter
    def scale(self, value):
        """Setter for a RenderableObjectBuilder's scale"""
        if value == 0:
            raise ValueError("Scale cannot be zero!")
        if value < 0:
            raise ValueError("Scale cannot be negative.")
        self._scale = value
        if self.model_node_path is not None:
            self.model_node_path.setScale(self._scale)

    @property
    def mass(self):
        return self._mass

    @mass.setter
    @accept_ndarrays
    def mass(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("something something something")
        if isinstance(value, list):
            value = value[0]  # Pull out the singular value if a numpy array

        self._mass = value
        if self.object_node is not None:
            self.object_node.setMass(value)
        
    @property
    def model_orientation(self):
        """The model orientation in reference to the object's physics body"""
        return self._model_orientation

    @model_orientation.setter
    @accept_ndarrays    
    def model_orientation(self, value):
        if not isinstance(value, list):
            raise TypeError("Orientation must be a list in [x, y, z] format.")
        if len(value) != 3:
            raise ValueError("Orientation must be a list in [x, y, z] format.")
        self._model_orientation = unbox_1d_ndarray_list(value)
        if self.model_node_path is not None:
            self.model_node_path.setHpr(self.object_node_path, self._model_orientation[0], self._model_orientation[1], self._model_orientation[2])

    @property
    def model_position(self):
        """The model orientation in reference to the object's physics body"""
        return self._model_position

    @model_position.setter
    @accept_ndarrays    
    def model_position(self, value):
        if not isinstance(value, list):
            raise TypeError("Orientation must be a list in [x, y, z] format.")
        if len(value) != 3:
            raise ValueError("Orientation must be a list in [x, y, z] format.")
        self._model_position = unbox_1d_ndarray_list(value)
        
        if self.model_node_path is not None:        
            self.model_node_path.setHpr(self.object_node_path, self._model_position[0], self._model_position[1], self._model_position[2])

    @staticmethod
    def parent_object_models(parent, child) -> None:
        """Parent a child simulation object to another object's root."""

        child.parent_node_path = parent.object_node_path
        child.object_node_path.reparentTo(parent.object_node_path)

    def parent_node_to(self, parent) -> None:
        self.parent_node_path = parent
        self.parent_object_models(parent, self)

    def hide(self):
        """Hides the object from view"""
        self.object_node_path.hide()
        self.hidden = True

    def unhide(self):
        """Shows the object if hidden"""
        self.object_node_path.show()
        self.hidden = False


class RenderableObjectBuilder(BuilderTemplate):
    """Builder to construct RenderableObjects"""

    def __init__(self, show_base: ShowBase):
        """
        Creates a builder to create renderable objects with default configs.
        You must configure the model for the object to render.
        """

        self.show_base = show_base
        self._renderable_object: RenderableObject = (
            RenderableObject()
        )  # Empty object to modify

        # Below are default configurations

        self._position = [0, 0, 0]
        self._orientation = [0, 0, 0]
        self._color = [255, 255, 255]  # In the format of RGB
        self._scale = 1

        self._is_actor = False
        self._has_model = True
        self._using_animations = False

        self._parent_node_path = None

        self._model: str = ""
        self._animations: list = []
        self._textures: list = []

        self._geometry_body = None
        self._model_position = [0, 0, 0]
        self._model_orientation = [0, 0, 0]
        self._mass = None

        self._model_shape = "box"
        self._shape_args = [5, 5, 5]
        self._given_body = False
        
        # REMINDER: Add new attributes from configure_from_object function

    def chainable(method):
        """
        Decorator to enable a function to be chained on others when calling the builder.
        """

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            method(self, *args, **kwargs)
            return self

        return wrapper

    @property
    def mass(self):
        """Getter for mass"""
        return self._mass

    @mass.setter
    def mass(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("something something something")
        self._mass = value

    @property
    def position(self):
        """Getter for position"""
        return self._position

    @position.setter
    @accept_ndarrays
    def position(self, value):
        if not isinstance(value, list):
            raise TypeError("Position must be a list in [x, y, z] format.")
        if len(value) != 3:
            raise ValueError("Position must be a list in [x, y, z] format.")

        self._position = unbox_1d_ndarray_list(value)

    @property
    def orientation(self):
        """Getter for a RenderableObjectBuilder's orientation"""
        return self._orientation

    @orientation.setter
    @accept_ndarrays
    def orientation(self, value):
        """Setter for a RenderableObjectBuilder's orientation"""
        if not isinstance(value, (list, numpy.ndarray)):
            raise TypeError("Orientation must be a list in [x, y, z] format.")
        if len(value) != 3:
            raise ValueError("Orientation must be a list in [x, y, z] format.")
        self._orientation = unbox_1d_ndarray_list(value)

    @property
    def color(self):
        """Getter for a RenderableObjectBuilder's color array"""
        return self.color

    @color.setter
    @accept_ndarrays
    def color(self, value):
        """Setter for a RenderableObjectBuilder's color array"""
        if not isinstance(value, (list, numpy.ndarray)):
            raise TypeError("Color must a list in the format of [R, G, B]")
        if len(value) != 3:
            raise ValueError("Color must a list in the format of [R, G, B]")
        for i in list:
            if i is not (isinstance(i, (int, float, numpy.ndarray))):
                raise Warning("Color values must be either an integer or float.")
            if i > 255:
                raise ValueError("Color values cannot go over 255")
            if i < 0:
                raise ValueError("Color values cannot be negative")
        self._color = unbox_1d_ndarray_list(value)

    @property
    def scale(self):
        """Getter for a RenderableObjectBuilder's scale"""
        return self._scale

    @scale.setter
    @accept_ndarrays
    def scale(self, value):
        """Setter for a RenderableObjectBuilder's scale"""
        if value == 0:
            raise ValueError("Scale cannot be zero!")
        if value < 0:
            raise ValueError("Scale cannot be negative.")
        self._scale = value

    # Chainable version of setters

    @chainable
    def set_mass(self, value):
        self.mass = value

    @chainable
    def set_position(self, value):
        self.position = value

    @chainable
    def set_orientation(self, value):
        self.orientation = value

    @chainable
    def set_color(self, color):
        self.color = color

    @chainable
    def set_scale(self, scale):
        self.scale = scale

    @chainable
    def is_actor(self, value: bool):
        """Sets whether the object is an actor or not"""
        self._is_actor = value

    @chainable
    def has_model(self, value: bool):
        """Sets whether the object has a renderable model or not"""
        self._has_model = value
        return self  # Allows for chaining in constructor

    @chainable
    def with_object(self, object_to_modify):
        """
        Allows the builder to modify the object instead  of building an object
        from scratch. The object must inherit from RenderableObject.
        """

        self._renderable_object = object_to_modify
        return self  # Allows to chain function calls

    @chainable
    def with_configurations(self, config: dict, *args, **kwargs):
        """
        Apply one or more nested configuration mappings onto the builder at
        once. This will match configurations to configs of the builder
        """
        set_attr_from_configuration(self, config, args, kwargs)
        return self

    @chainable
    def config_from_object(self, object):
        """
        Use configurations from the object specified.
        If applicable, the attributes will be applied to the builder.
        The object must inherit from RenderableObject
        """

        # TODO: Safety check on whether object has it
        # The object should have these attributes because it's a
        # renderable object
        self._position = object.position
        self._orientation = object.orientation
        self._color = object.color
        self._scale = object.scale
        self._model = object.model
        self._model_orientation = object.model_orientation
        self._model_position = object.model_position
        self._mass = object.mass
        self._geometry_body = object.geometry_body
        self._model_shape = object.geometry_shape
        self._shape_args = object.geometry_args

    @chainable
    def with_parent(self, parent_object_node):
        """Attaches the parent object node to the object"""
        self._parent_node_path = parent_object_node

    @chainable
    def with_model(self, model_path: str):
        """Creates the node with the model given"""
        self._model = model_path
        return self

    @chainable
    def with_animations(self, *args, **kwargs):
        """ "Sets animation for the created model"""
        self._is_actor = True

        return self

    @chainable
    def with_textures(self, *args, **kwargs):
        """Sets textures of the created object"""

    @chainable
    def with_collision_shape(self, shape: str, *args):
        """
        Sets the collision shape with the given args.
        The arguments are directly passed to panda3D. Primitives only.
        See panda3d bullet documentation for arguments for each shape.

        Available:
        - "sphere"
        - "plane"
        - "box"
        - "cylinder"
        - "capsule"
        - "cone"
        """

        # TODO Validate Inputs

        self._model_shape = shape
        self._shape_args = args

    @chainable
    def set_collision_shape(self, shape):
        """Sets the object's collision shape with a pybullet `BulletShape`"""
        self._given_body = True
        self._geometry_body = shape

    def _reset(self):
        """Resets the builder to build a new object"""
        self.__init__(self.show_base)

    def _generate_simulation_node(self):
        """Create a transform root and optionally load its visible model."""

        # Some cases only need a transform anchor, not visible geometry.
        if not self._has_model:
            self._renderable_object.model_node = None
            self._renderable_object.model_node_path = None

        if self._model == "":
            raise AttributeError(
                "Rendering an object must have a model. If you do not want a model, ensure that it is disabled."
            )

        try:
            self._renderable_object.model_node = self.show_base.loader.loadModel(
                self._model
            )
            self._renderable_object.model_node_path = NodePath(
                self._renderable_object.model_node
            )
            self._renderable_object.model_node_path.reparentTo(
                self._renderable_object.object_node_path
            )
        except TypeError:
            raise TypeError(
                "No path for the model was listed. Check your configurations again!"
            )

    def _create_physics_body(self):
        """Takes an input shape and creates it using the given arguements"""
        match self._model_shape:
            case "sphere":
                from panda3d.bullet import BulletSphereShape

                self._geometry_body = BulletSphereShape(*self._shape_args)
            case "plane":
                from panda3d.bullet import BulletBoxShape

                self._geometry_body = BulletBoxShape(Vec3(*self._shape_args))
            case "cylinder":
                from panda3d.bullet import BulletCylinderShape

                self._geometry_body = BulletCylinderShape(*self._shape_args)
            case "capsule":
                from panda3d.bullet import BulletCapsuleShape

                self._geometry_body = BulletCapsuleShape(*self._shape_args)
            case "cone":
                from panda3d.bullet import BulletConeShape

                self._geometry_body = BulletConeShape(*self._shape_args)
            case _:
                # Default shape
                self._renderable_object.geometry_body = BulletBoxShape(Vec3(10.5, 10.5, 10.5))

    def _setup_physics(self):
        self._renderable_object.object_node = BulletRigidBodyNode(
            self._renderable_object.name
        )
        self._renderable_object.object_node_path = NodePath(
            self._renderable_object.object_node
        )
        if self._mass:
            self._renderable_object.mass = self._mass

        self._renderable_object.geometry_body = self._geometry_body
        self._renderable_object.object_node.addShape(self._geometry_body)
        self.show_base.bullet_world.attachRigidBody(self._renderable_object.object_node)

    def _generate_simulation_actor(self, *args, **kwargs):
        """Creates a panda3d actor, which can have it's model move"""

        if not self._is_actor:
            raise AttributeError(
                "This object is not an actor. Ensure that this node is configured to be an actor"
            )

        if not self._has_model:
            print("Actors must have models!")
            raise AttributeError

    def _configure_object(self) -> None:
        """Apply configured transform and display color to the scene node."""
        if self._renderable_object.object_node_path is None:
            raise RuntimeError("generate a simulation node before configuring it")

        if self._parent_node_path is not None:
            self._renderable_object.parent_node_path = self._parent_node_path
            self._renderable_object.set_relative_position(self._parent_node_path, self._renderable_object.position)
        else:
            self._renderable_object.position = self._position

        self._renderable_object.orientation = self._orientation

        self._renderable_object.color = self._color
        if self._mass is not None:
            self._renderable_object.mass = self._mass

    def _render_object(self):
        """Attach an object's transform root to its parent or the world root."""
        if self._parent_node_path is not None:
            self._renderable_object.object_node_path.reparentTo(self._parent_node_path)
        else:
            self._renderable_object.object_node_path.reparentTo(self.show_base.render)
            
    def _model_adjustments(self):
        """For adjusting the model on the physics node"""
        if self._has_model: 
            self._renderable_object.model_position = self._model_position
            self._renderable_object.model_orientation = self._model_orientation
            
            # Scale won't apply earlier because it only impacts the model
            self._renderable_object.scale = self._scale


    def _load_animations(self, *args, **kwargs):
        """_summary_ Loads animations into the model"""
        self._using_animations = True

    def _attach_textures(self, *args, **kwargs):
        """Attaches textures onto the model of the RenderableObject"""

    def build(self):
        """Builds with created configurations"""

        if not self._given_body:
            self._create_physics_body()
        self._setup_physics()

        self._configure_object()
        
        if self._is_actor:
            self._generate_simulation_actor()
        else:
            self._generate_simulation_node()
        self._attach_textures()
        
        self._model_adjustments()

        if self._using_animations:
            self._load_animations()

        self._render_object()

        # For creating new objects
        # The return section is dropped when modifying an object
        product = self._renderable_object
        self._reset()
        return product
