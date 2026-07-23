from memory.conversation_manager import ConversationManager
from memory.conversation_repository import MemoryConversationRepository
from services.audit_services import AuditService
from services.csv_export_service import CsvExportService
from services.metadata_service import MetadataService
from services.vertex_search_service import VertexSearchService
from services.bigquery_service import BigQueryService
from services.sql_validator import SQLValidator
from services.cost_service import CostService

from agents.router_agent import RouterAgent
from agents.information_agent import InformationAgent
from agents.table_identifier import TableIdentifier
from agents.sql_generator import SQLGenerator

class ServiceRegistry:

    def __init__(self):
        self.metadata = MetadataService()
        self.vector_search = VertexSearchService()
        self.bigquery = BigQueryService()
        self.validator = SQLValidator()
        self.router = RouterAgent()
        self.validator = SQLValidator()
        self.cost = CostService()
        self.information = InformationAgent()
        self.table_identifier = TableIdentifier()
        self.sql_generator = SQLGenerator()
        self.csv_export = CsvExportService()
        self.audit = AuditService()
        self.conversation_repository = (MemoryConversationRepository())
        self.conversation_manager = (ConversationManager(self.conversation_repository))