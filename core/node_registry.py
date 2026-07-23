import logging
from typing import Callable, Dict, Type

from models.workflow_nodes import WorkflowNode
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RegisteredNode:
    workflow_node: WorkflowNode
    node_class: type


class NodeRegistry:
    """
    Stores node classes and creates node instances.
    The workflow builder never imports any node directly.
    """

    _registry = {}

    @classmethod
    def register(cls, workflow_node: WorkflowNode):
        def decorator(node_class):
            logger.debug(f"Registering node class {node_class.__name__} for workflow_node: {workflow_node.value}")
            cls._registry[workflow_node.value] = RegisteredNode(
                workflow_node=workflow_node,
                node_class=node_class)
            return node_class

        return decorator

    @classmethod
    def create(cls, workflow_node: str, services):
        logger.debug(f"Creating node instance for: {workflow_node}")
        try:
            registered = cls._registry[workflow_node]
            node = registered.node_class(services)
            node.workflow_node = registered.workflow_node
            logger.info(f"Successfully instantiated node: {workflow_node}")
            return node
        except KeyError:
            logger.error(msg=f"Node '{workflow_node}' not found in registry. Ensure it is imported and registered.",
                         exc_info=True)
            raise
        except Exception as e:
            logger.error(msg=f"Error creating node '{workflow_node}': {e}", exc_info=True)
            raise

    @classmethod
    def nodes(cls):
        return cls._registry
