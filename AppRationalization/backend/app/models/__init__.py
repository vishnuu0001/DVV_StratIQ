# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AppRationalization — backend/app/models (__init__.py)
# Date: 2025-12-12
# ---------------------------------------------------------------------------
from .infrastructure import Infrastructure, Server, Container, NetworkLink, InfrastructureDiscovery
from .application import Application, ApplicationDependency
from .code import CodeRepository, ArchitectureComponent, InternalDependency
from .capability import BusinessCapability, CapabilityApplication, CapabilityMapping
from .analysis import AnalysisResult, RationalizationScenario
from .pdf_report import PDFReport
from .correlation import CorrelationResult, MasterMatrixEntry
from .cast import CASTAnalysis, ApplicationInventory, ApplicationClassification, InternalArchitecture
from .industry_data import IndustryTemplate, IndustryData
from .corent_data import CorentData
from .consolidated_app import ConsolidatedApp
from .technical_assessment import (
    TechnicalAssessmentImport,
    BusinessValidation,
    WaveInput,
    TechnicalEvaluationCategorizeMeta,
    TechnicalEvaluationCategorizeRow,
)
from .wave_plan import WavePlan, WavePlanEntry
from .wave_schedule import WaveSchedule, WaveScheduleWave, WaveScheduleTask, WaveScheduleApp, WaveScheduleJob
from .auth import (
    User,
    UserAppPermission,
    UserSession,
    DesktopLaunchTicket,
    APP_RATIONALIZATION,
    CODE_ANALYSIS,
    INFRA_SCAN,
    NOVASTRA_ITSM,
    DASHBOARD,
    INTUNE_AUTOMATION,
    TOOL_ANALYSIS_QUALIFICATION,
    SSDLC_PROCESS_ASSESSMENT,
    MICROSITE_DATA_ANALYSIS,
    AI_REMAN_CORE,
    AI_VEHICLE_LOAN,
    OPPORTUNITY_TRACKER,
    SUPPLY_CHAIN_DISRUPTION_MANAGER,
)

__all__ = [
    'Infrastructure',
    'Server',
    'Container',
    'NetworkLink',
    'InfrastructureDiscovery',
    'Application',
    'ApplicationDependency',
    'CodeRepository',
    'ArchitectureComponent',
    'InternalDependency',
    'BusinessCapability',
    'CapabilityApplication',
    'CapabilityMapping',
    'AnalysisResult',
    'RationalizationScenario',
    'PDFReport',
    'CorrelationResult',
    'MasterMatrixEntry',
    'CASTAnalysis',
    'ApplicationInventory',
    'ApplicationClassification',
    'InternalArchitecture',
    'IndustryTemplate',
    'IndustryData',
    'CorentData',
    'ConsolidatedApp',
    'TechnicalAssessmentImport',
    'BusinessValidation',
    'WaveInput',
    'TechnicalEvaluationCategorizeMeta',
    'TechnicalEvaluationCategorizeRow',
    'WavePlan',
    'WavePlanEntry',
    'WaveSchedule',
    'WaveScheduleWave',
    'WaveScheduleTask',
    'WaveScheduleApp',
    'WaveScheduleJob',
    'User',
    'UserAppPermission',
    'UserSession',
    'DesktopLaunchTicket',
    'APP_RATIONALIZATION',
    'CODE_ANALYSIS',
    'INFRA_SCAN',
    'NOVASTRA_ITSM',
    'DASHBOARD',
    'INTUNE_AUTOMATION',
    'TOOL_ANALYSIS_QUALIFICATION',
    'SSDLC_PROCESS_ASSESSMENT',
    'MICROSITE_DATA_ANALYSIS',
    'AI_REMAN_CORE',
    'AI_VEHICLE_LOAN',
    'OPPORTUNITY_TRACKER',
    'SUPPLY_CHAIN_DISRUPTION_MANAGER',
]
