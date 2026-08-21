"""
File for the class `SimulationManager`,
the handler for interfacing and adding objects to panad3d
"""

from typing import Any

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from sim.rendering.renderable_object import RenderableObjectBuilder
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape
from panda3d.core import Vec3


class SimulationManager:
    """Handler for simulation utilities. Modifies groups of nodes for tasks"""

    def __init__(self, show_base: ShowBase):
        self.world = show_base
        self.renderable_builder = RenderableObjectBuilder(self.world)


    def update_physics(self, task):
        """Updates PyBullet's Physics Engine"""
        self.world.bullet_world.doPhysics(self.world.dt)
        return Task.cont
    
    def enable_debug_collision_geometry(self):
        """Renders debug geometry for physics"""
        debugNode = BulletDebugNode("Debug")
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(True)
        debugNode.showNormals(False)
        debugNP = self.world.render.attachNewNode(debugNode)
        debugNP.show()
        self.world.bullet_world.setDebugNode(debugNP.node())

    def load_debug_plane(self):
        """Creates a flat plane to debug on"""
        # Plane
        shape = BulletPlaneShape(Vec3(0, 0, 1), 1)
        node = BulletRigidBodyNode("Ground")
        node.addShape(shape)
        np = self.world.render.attachNewNode(node)
        np.setPos(0, 0, -2)
        self.world.bullet_world.attachRigidBody(node)
        
    def load_debug_physics_object(self):
        """Loads a model with collisions into the simulation """

        shape = BulletBoxShape(Vec3(6, 6, 6))
        node = BulletRigidBodyNode("Box")
        node.setMass(1.0)
        node.addShape(shape)
        np = self.world.render.attachNewNode(node)
        np.setPos(0, 0, 100)
        self.world.bullet_world.attachRigidBody(node)
        model = self.world.loader.loadModel(
            "assets/Sensors/SLR_Camera/10124_SLR_Camera_SG_V1_Iteration2.obj"
        )
        model.flattenLight()
        model.setScale(0.1)
        model.reparentTo(np)
        model.setPos(np, 0, 3, -5)
