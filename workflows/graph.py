# Change these lines at the top of graph.py
from core.node_registry import NodeRegistry
from models.workflow_state import WorkflowState
from langgraph.graph import StateGraph

from nodes.router_node import RouterNode
from nodes.table_identifier_node import TableIdentifierNode
from nodes.metadata_node import MetadataNode
from nodes.sql_generation_node import SQLGeneratorNode
from nodes.validation_node import ValidationNode
from nodes.information_node import InformationNode
from nodes.approval_node import ApprovalNode
from nodes.dryrun_node import DryRunNode



# Do NOT import nodes manually anymore. Let NodeRegistry handle it.

router = RouterNode()
identifier = TableIdentifierNode()
metadata = MetadataNode()
generator = SQLGeneratorNode()
validator = ValidationNode()
dryrun = DryRunNode()
approval = ApprovalNode()

builder = StateGraph(WorkflowState)
builder.add_node("router", router.execute)
builder.add_node("table_identifier", identifier.execute)
builder.add_node("metadata", metadata.execute)
builder.add_node("generator", generator.execute)
builder.add_node("validator", validator.execute)
builder.add_node("dryrun", dryrun.execute)
builder.add_node("approval", approval.execute)

builder.set_entry_point("router")
builder.add_edge(  "router",  "table_identifier")
builder.add_edge(  "table_identifier",  "metadata")
builder.add_edge(  "metadata",  "generator")
builder.add_edge(  "generator",  "validator")
builder.add_edge(  "validator",  "dryrun")
builder.add_edge(  "dryrun",  "approval")


def approval_router(state):
    if state.approved:
        return "execute"
    return "end"

