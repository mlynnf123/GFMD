# GFMD Swarm Agent System - Vertex AI Implementation

A comprehensive AI-powered sales automation platform for Global Forensic Medical Devices (GFMD) built with **Vertex AI** and **LangGraph**.

## 🎯 Overview

This system manages the entire sales lifecycle from lead discovery through customer success using specialized AI agents that collaborate seamlessly. The implementation leverages Google Cloud's Vertex AI platform for enterprise-grade AI capabilities with LangGraph for sophisticated multi-agent workflows.

### Key Components

- **🏥 Hospital Prospecting Agent**: Qualification and analysis of hospital laboratory opportunities
- **🚀 Multi-Channel Outreach Agent**: Automated email, LinkedIn, and phone campaigns  
- **🤖 Swarm Orchestrator**: Coordinates agent handoffs and workflow execution
- **🗃️ Data Models**: Comprehensive schemas for healthcare organizations and sales processes

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                Swarm Orchestrator                       │
│  • Workflow coordination and agent handoffs            │
│  • State management and context preservation           │
│  • Performance monitoring and metrics                  │
└─────────────────────────┬───────────────────────────────┘
                          │
                ┌─────────┴─────────┐
                │                   │
┌───────────────▼─────────────┐   ┌─▼─────────────────────────┐
│  Hospital Prospecting Agent │   │ Multi-Channel Outreach    │
│  • Qualification scoring    │   │ • Email campaigns         │
│  • Product recommendations │   │ • LinkedIn outreach       │
│  • Decision maker ID        │   │ • Phone call sequences    │
│  • Approach strategy        │   │ • Response monitoring     │
└─────────────────────────────┘   └───────────────────────────┘
                │                           │
┌───────────────▼─────────────────────────────────────────────┐
│                   Data Models Layer                         │
│  • Organization, Contact, Prospect models                  │
│  • Workflow execution tracking                             │
│  • Performance metrics and analytics                       │
│  • Integration schemas and configurations                  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Google Cloud Project** with Vertex AI API enabled
2. **Authentication** configured (service account or gcloud auth)
3. **Python 3.9+** installed

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd gfmd_swarm_agent

# Install dependencies
pip install -r vertex_ai_requirements.txt

# Set up environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### Basic Usage

```python
from vertex_ai_swarm_orchestrator import GFMDSwarmOrchestrator
import asyncio

async def main():
    # Initialize the orchestrator
    orchestrator = GFMDSwarmOrchestrator(project_id="your-project-id")
    
    # Process a new prospect
    prospect_data = {
        "organization_name": "Regional Medical Center",
        "contact_name": "Dr. Sarah Johnson",
        "contact_title": "Laboratory Director",
        "email": "s.johnson@regional.org",
        "phone": "555-0123",
        "bed_count": 300,
        "lab_type": "Clinical Chemistry, Hematology"
    }
    
    result = await orchestrator.process_new_prospect(prospect_data)
    print(f"Qualification Score: {result['qualification_score']}")
    print(f"Outreach Touchpoints: {result['touchpoints_executed']}")

# Run the example
asyncio.run(main())
```

## 📋 System Components

### 1. Hospital Prospecting Agent (`vertex_ai_hospital_prospecting.py`)

**Purpose**: Intelligent qualification and analysis of hospital prospects

**Features**:
- 10-point qualification scoring system
- Product recommendations based on hospital profile
- Decision maker identification and mapping
- Competitive positioning analysis
- Automated approach strategy generation

**Workflow**:
```
Prospect Data → Analysis → Qualification → Product Recommendations → Decision Makers → Strategy → Handoff
```

### 2. Multi-Channel Outreach Agent (`vertex_ai_outreach_agent.py`)

**Purpose**: Execute personalized communication campaigns

**Channels**:
- **Email**: Personalized templates with dynamic content
- **LinkedIn**: Professional connection requests and messaging
- **Phone**: Call scripts and voicemail templates

**Sequences**:
- **New Hospital Prospect**: 8 touchpoints over 28 days
- **Existing Customer Expansion**: 6 touchpoints over 21 days
- **Nurture Campaign**: Extended relationship building

### 3. Swarm Orchestrator (`vertex_ai_swarm_orchestrator.py`)

**Purpose**: Coordinate multi-agent workflows

**Capabilities**:
- Dynamic agent routing and handoffs
- Context preservation across agents
- Performance monitoring and metrics
- Error handling and recovery
- Concurrent workflow management

### 4. Data Models (`vertex_ai_data_models.py`)

**Purpose**: Comprehensive data schemas and validation

**Models**:
- `Organization`: Healthcare facility information
- `Contact`: Decision maker details and roles
- `Prospect`: Complete prospect lifecycle tracking
- `OutreachSequence`: Communication campaign management
- `WorkflowExecution`: Multi-agent workflow tracking

## 📊 GFMD Product Portfolio

### Silencer Centrifuge Series

| Series | Models | Applications | Price Range |
|--------|--------|-------------|-------------|
| **MACH** | H8, H12, H6, F10, PPP, SC | Small-medium labs | $15K-25K |
| **ELITE** | H12, F24, PPP, SC | High-performance labs | $18K-28K |
| **STEALTH** | H34 | Specialized applications | $22K-32K |
| **TANK** | TANK, TANK-R | High-volume, blood banks | $25K-35K |
| **ROVER** | ROVER, ROVER-R | Large-scale operations | $30K-45K |

### Target Markets

- **Primary**: Hospital/Medical Centers (80.5% of customer base)
- **Secondary**: Laboratories (5.8%), Military/Government (2.7%)
- **Specialties**: Blood banks, clinical chemistry, hematology, stat labs

## 🎯 Qualification System

### Scoring Criteria (10-point scale)

| Factor | Weight | Scoring |
|--------|--------|---------|
| **Bed Count** | 25% | 500+ beds = 10pts, 200-499 = 8pts, 100-199 = 6pts |
| **Lab Types** | 20% | Blood bank = 3.0x, Clinical = 2.5x, Stat = 3.0x |
| **Equipment Age** | 20% | 10+ years = 10pts, 7-10 years = 8pts |
| **Budget Readiness** | 15% | Expansion projects, fiscal timing |
| **Contact Quality** | 10% | Decision maker access, complete info |
| **Geographic** | 10% | Strategic location factors |

### Priority Levels

- **High Priority** (≥8.0): Immediate outreach, enterprise approach
- **Medium Priority** (6.0-7.9): Standard outreach, strategic account
- **Low Priority** (<6.0): Nurture campaign, future follow-up

## 🔄 Workflow Types

### 1. New Prospect Processing

```
Input → Hospital Prospecting Agent → Qualification → Multi-Channel Outreach → Response Monitoring
```

**Steps**:
1. Prospect analysis and profiling
2. Qualification scoring and product matching
3. Decision maker identification
4. Outreach sequence creation
5. Multi-channel campaign execution
6. Response tracking and follow-up

### 2. Existing Customer Expansion

```
Input → Multi-Channel Outreach Agent → Account Review → Expansion Campaign
```

**Steps**:
1. Account relationship assessment
2. Expansion opportunity identification
3. Customized outreach sequence
4. Special offers and incentives
5. Closing and next steps

### 3. Nurture Campaign

```
Input → Multi-Channel Outreach Agent → Long-term Relationship Building
```

**Steps**:
1. Industry insights and thought leadership
2. Educational content delivery
3. Periodic check-ins and updates
4. Relationship maintenance

## 📈 Performance Metrics

### System-Level KPIs

- **Qualification Rate**: Target 60%+
- **Response Rate**: Target 5-8%
- **Meeting Conversion**: Target 2-3%
- **Email Open Rate**: Target 25-30%
- **LinkedIn Connection Rate**: Target 40-50%

### Agent Performance

- **Hospital Prospecting**: Average 8.5s execution time
- **Multi-Channel Outreach**: 8-touchpoint sequence completion
- **Swarm Orchestrator**: 2+ agent coordination per workflow

## 🧪 Testing

### Run Test Suite

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
python -m pytest test_vertex_ai_swarm.py -v

# Run specific test categories
python -m pytest test_vertex_ai_swarm.py::TestDataModels -v
python -m pytest test_vertex_ai_swarm.py::TestHospitalProspectingAgent -v
python -m pytest test_vertex_ai_swarm.py::TestSwarmOrchestrator -v
```

### Run Demo

```bash
# Complete system demonstration
python vertex_ai_main_demo.py

# Individual agent testing
python vertex_ai_hospital_prospecting.py
python vertex_ai_outreach_agent.py
python vertex_ai_swarm_orchestrator.py
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
GOOGLE_CLOUD_PROJECT="your-project-id"
GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"

# Optional
VERTEX_AI_MODEL="gemini-2.0-flash-exp"  # Default model
VERTEX_AI_REGION="us-central1"           # Default region
```

### Model Configuration

```python
# Custom model settings
orchestrator = GFMDSwarmOrchestrator(
    model_name="gemini-2.0-flash-exp",
    project_id="your-project-id"
)

# Agent-specific configuration
hospital_agent = HospitalProspectingAgent(
    model_name="gemini-2.0-flash-exp",
    project_id="your-project-id"
)
```

## 🔌 Integration

### CRM Integration

```python
from vertex_ai_data_models import IntegrationConfig

crm_config = IntegrationConfig(
    integration_name="salesforce",
    integration_type="crm",
    endpoint_url="https://your-instance.salesforce.com",
    api_key="your-api-key"
)
```

### Email Platform Integration

```python
email_config = IntegrationConfig(
    integration_name="outlook",
    integration_type="email",
    credentials={"client_id": "...", "client_secret": "..."}
)
```

## 📚 API Reference

### Core Classes

#### `GFMDSwarmOrchestrator`

```python
class GFMDSwarmOrchestrator:
    async def process_new_prospect(prospect_data: Dict) -> Dict
    async def process_existing_customer(customer_data: Dict) -> Dict
    def get_system_metrics() -> Dict
```

#### `HospitalProspectingAgent`

```python
class HospitalProspectingAgent:
    async def process_prospect(prospect_data: Dict) -> Dict
    def _calculate_qualification_score(prospect_data: Dict) -> float
    def _recommend_products(prospect_data: Dict) -> List[str]
```

#### `MultiChannelOutreachAgent`

```python
class MultiChannelOutreachAgent:
    async def execute_outreach_sequence(request: Dict) -> Dict
    def _determine_persona_type(title: str) -> PersonaType
```

## 🛠️ Development

### File Structure

```
gfmd_swarm_agent/
├── vertex_ai_requirements.txt          # Vertex AI dependencies
├── vertex_ai_hospital_prospecting.py   # Hospital prospecting agent
├── vertex_ai_outreach_agent.py         # Multi-channel outreach agent
├── vertex_ai_swarm_orchestrator.py     # Swarm coordination system
├── vertex_ai_data_models.py            # Data schemas and validation
├── test_vertex_ai_swarm.py             # Comprehensive test suite
├── vertex_ai_main_demo.py              # Complete system demonstration
└── README_VERTEX_AI.md                 # This documentation
```

### Adding New Agents

1. Create agent class extending base patterns
2. Implement LangGraph workflow structure
3. Define handoff protocols and data schemas
4. Add integration to swarm orchestrator
5. Write comprehensive tests

### Best Practices

- **Error Handling**: Implement robust error recovery
- **Performance**: Monitor execution times and token usage  
- **Security**: Never log or expose sensitive data
- **Scalability**: Design for concurrent workflow execution
- **Testing**: Maintain >90% test coverage

## 🔒 Security

### Data Protection

- All PII data encrypted in transit and at rest
- HIPAA-compliant data handling procedures
- Audit logging for all prospect interactions
- Access controls and authentication

### API Security

- Service account authentication required
- Rate limiting and quota management
- Input validation and sanitization
- Error message sanitization

## 📖 Troubleshooting

### Common Issues

#### Authentication Error

```bash
Error: Could not automatically determine credentials
Solution: Set GOOGLE_APPLICATION_CREDENTIALS environment variable
```

#### Model Access Error

```bash
Error: Model not available in region
Solution: Check model availability in your Vertex AI region
```

#### Rate Limiting

```bash
Error: Rate limit exceeded
Solution: Implement exponential backoff or reduce concurrency
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose agent logging
orchestrator = GFMDSwarmOrchestrator(debug=True)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-agent`)
3. Implement changes with tests
4. Update documentation
5. Submit pull request

### Code Standards

- Python 3.9+ compatibility
- Type hints for all functions
- Comprehensive docstrings
- Unit tests for new features
- Performance benchmarks for agents

## 📄 License

This project is proprietary software developed for Global Forensic Medical Devices (GFMD). All rights reserved.

## 📞 Support

- **Technical Issues**: Create GitHub issue
- **Business Questions**: Contact GFMD Sales Operations
- **Integration Support**: Refer to API documentation

---

**Built with ❤️ for GFMD using Vertex AI and LangGraph**

*Last updated: January 2025*