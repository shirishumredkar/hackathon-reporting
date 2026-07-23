import logging
from pathlib import Path
import yaml
from langgraph.graph import END, StateGraph
from models.workflow_state import WorkflowState, WorkflowStatus
from core.node_registry import NodeRegistry
from core.service_registry import ServiceRegistry
import nodes  # Import nodes to trigger registry decorators

logger = logging.getLogger(__name__)

# --- Universal Routing Functions ---

def _route_after_node(state: WorkflowState, next_node: str):
    """
    Checks if the workflow has failed. If so, it ends the graph.
    Otherwise, it proceeds to the specified next node.
    """
    if state.status == WorkflowStatus.FAILED:
        logger.warning(f"Workflow failed at node {state.current_node}. Ending execution. Error: {state.error}")
        return END
    logger.debug(f"Workflow continuing from {state.current_node} to {next_node}")
    return next_node

def _route_conditional(state: WorkflowState, transitions: dict):
    """
    Handles explicit conditional routing defined in the YAML (e.g., for router and approval).
    Also includes the universal failure check.
    """
    if state.status == WorkflowStatus.FAILED:
        logger.warning(f"Workflow failed at node {state.current_node}. Ending execution. Error: {state.error}")
        return END

    logger.debug(f"Evaluating conditional route. State route: {state.route}, Approved: {state.approved}")
    if state.route in transitions:
        target = transitions[state.route]
        logger.debug(f"Routing to: {target}")
        return target

    if state.approved:
        target = transitions.get("APPROVED")
        logger.debug(f"Routing approved state to: {target}")
        return target

    target = transitions.get("REJECTED", END)
    logger.debug(f"Routing rejected/default state to: {target}")
    return target


# --- Workflow Builder Class ---

class WorkflowBuilder:
    def __init__(self, workflow_file: str = None):
        logger.debug("Initializing WorkflowBuilder")
        self.registry = ServiceRegistry()

        if workflow_file is None:
            workflow = Path(__file__).parent / "workflow.yaml"
        else:
            workflow = workflow_file

        logger.info(f"Loading workflow configuration from {workflow}")
        try:
            with open(workflow) as fp:
                self.workflow = yaml.safe_load(fp)
            logger.debug(f"Workflow configuration loaded successfully: {list(self.workflow.get('nodes', {}).keys())}")
        except Exception as e:
            logger.error(f"Failed to load workflow yaml from {workflow}: {e}", exc_info=True)
            raise

    def build(self):
        logger.info("Building LangGraph StateGraph")
        graph = StateGraph(WorkflowState)

        try:
            # 1. Add all nodes to the graph
            for node_name, config in self.workflow["nodes"].items():
                logger.debug(f"Adding node to graph: {node_name}")
                node = NodeRegistry.create(node_name, self.registry)
                graph.add_node(node_name, node.execute)

            # 2. Set the entry point (ONCE, outside the loop)
            entry_point = self.workflow["entry_point"]
            logger.debug(f"Setting graph entry point: {entry_point}")
            graph.set_entry_point(entry_point)

            # 3. Add edges with the universal failure check (SIBLING loop, not nested)
            for node_name, config in self.workflow["nodes"].items():
                if config.get("end", False):
                    logger.debug(f"Adding end edge for node: {node_name}")
                    graph.add_edge(node_name, END)
                    continue

                next_node_config = config.get("next")

                # Handle standard, linear transitions
                if isinstance(next_node_config, str):
                    next_node_name = next_node_config
                    logger.debug(f"Adding conditional failure check edge: {node_name} -> {next_node_name}")
                    graph.add_conditional_edges(
                        node_name,
                        lambda state, next_node=next_node_name: _route_after_node(state, next_node),
                        path_map={next_node_name: next_node_name, END: END},
                    )

                # Handle explicit conditional transitions (like router and approval)
                elif isinstance(next_node_config, dict):
                    logger.debug(
                        f"Adding explicit conditional edges for node: {node_name} "
                        f"with transitions: {list(next_node_config.keys())}"
                    )
                    graph.add_conditional_edges(
                        node_name,
                        lambda state, transitions=next_node_config: _route_conditional(state, transitions),
                    )

            compiled_graph = graph.compile()
            logger.info("LangGraph compiled successfully")
            return compiled_graph

        except Exception as e:
            logger.error(f"Error building graph: {e}", exc_info=True)
            raise

    # def build(self):
    #     logger.info("Building LangGraph StateGraph")
    #     graph = StateGraph(WorkflowState)
    #
    #     try:
    #         # 1. Add all nodes to the graph
    #         for node_name, config in self.workflow["nodes"].items():
    #             logger.debug(f"Adding node to graph: {node_name}")
    #             node = NodeRegistry.create(node_name, self.registry)
    #             graph.add_node(node_name, node.execute)
    #
    #             # 2. Set the entry point
    #             entry_point = self.workflow["entry_point"]
    #             logger.debug(f"Setting graph entry point: {entry_point}")
    #             graph.set_entry_point(entry_point)
    #
    #             # 3. Add edges with the new universal failure check
    #             for node_name, config in self.workflow["nodes"].items():
    #                 if config.get("end", False):
    #                     logger.debug(f"Adding end edge for node: {node_name}")
    #                     graph.add_edge(node_name, END)
    #                     continue
    #
    #                 next_node_config = config.get("next")
    #
    #                 # Handle standard, linear transitions
    #                 if isinstance(next_node_config, str):
    #                     next_node_name = next_node_config
    #                     logger.debug(f"Adding conditional failure check edge: {node_name} -> {next_node_name}")
    #                     graph.add_conditional_edges(
    #                         node_name,
    #                         lambda state, next_node=next_node_name: _route_after_node(state, next_node),
    #                         path_map={next_node_name: next_node_name, END: END}
    #                     )
    #
    #                 # Handle explicit conditional transitions (like router and approval)
    #                 elif isinstance(next_node_config, dict):
    #                     logger.debug(f"Adding explicit conditional edges for node: {node_name} with transitions: {list(next_node_config.keys())}")
    #                     graph.add_conditional_edges(
    #                         node_name,
    #                      lambda state, transitions=next_node_config: _route_conditional(state, transitions),
    #                     )
    #
    #         compiled_graph = graph.compile()
    #         logger.info("LangGraph compiled successfully")
    #         return compiled_graph
    #
    #     except Exception as e:
    #         logger.error(f"Error building graph: {e}", exc_info=True)
    #         raise
