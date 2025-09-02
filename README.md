# AWS Bedrock AgentCore - Financial Email Processor

This project implements a financial email processor agent built on AWS Bedrock AgentCore. It processes Gmail financial emails (invoices, orders, statements) and provides analysis and storage capabilities.

## Project Structure

```
.
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── src/                         # Source code
│   ├── main.py                  # Main entry point
│   ├── agents/                  # Agent implementations
│   │   ├── customer_support.py  # Main financial email processor agent
│   │   ├── customer_support_backup.py  # Backup agent implementation
│   │   ├── email_processor.py   # Email processing functionality
│   │   ├── database_service.py  # Database service integration
│   │   ├── llm_email_analyzer.py # LLM-based email analysis
│   │   └── session_manager.py   # Session management
│   ├── tools/                   # Custom tools
│   │   ├── tool_manager.py      # Tool management system
│   │   └── whatsapp_tool.py     # WhatsApp messaging tool
│   ├── utils/                   # Utility functions
│   │   ├── credential_manager.py # Credential management
│   │   ├── permission_controller.py # Permission control
│   │   ├── exchange_service.py   # Exchange rate service
│   │   ├── session_manager.py    # Session management
│   │   ├── deploy.sh            # Deployment script
│   │   ├── run_local.py         # Local execution script
│   │   ├── setup_config.py      # Configuration setup
│   │   ├── check_deployment_status.py # Deployment status checker
│   │   └── deploy_gateway_memory.py # Gateway memory deployment
│   ├── memory/                  # Memory examples
│   │   └── examples/
│   │       ├── long_term_memory_ops.py
│   │       └── memory_client.py
│   ├── config/                  # Configuration files
│   │   ├── .bedrock_agentcore.yaml
│   │   ├── credentials.json
│   │   ├── permissions.json
│   │   └── policies/
│   ├── Dockerfile               # Docker configuration
│   └── docker-compose.yml       # Docker Compose configuration
├── tests/                       # Test files
│   ├── test_aws_whatsapp.py     # AWS WhatsApp tool tests
│   ├── test_whatsapp.py         # WhatsApp tool tests
│   └── test_llm_enhancement.py  # LLM enhancement tests
└── docs/                        # Documentation
    ├── README.md                # Main documentation
    ├── DEPLOYMENT_GUIDE.md      # Deployment guide
    └── ...                      # Other documentation files
```

## Detailed Features and Functionality

### 1. Financial Email Processing
The core functionality of this agent is to automatically process financial emails from Gmail, including:
- **Invoice Processing**: Extract details such as invoice number, amount, currency, due date, and vendor information
- **Order Confirmation Processing**: Parse order details including items, quantities, prices, and delivery information
- **Statement Processing**: Analyze bank and credit card statements to extract transaction details
- **Receipt Processing**: Extract purchase details from digital receipts

### 2. Advanced Email Analysis with LLM
The agent uses Amazon Bedrock LLMs to perform deep analysis of financial emails:
- **Intelligent Data Extraction**: Uses advanced natural language processing to extract structured financial information
- **Anomaly Detection**: Identifies unusual patterns or discrepancies in financial documents
- **Semantic Understanding**: Comprehends the context and meaning behind financial communications
- **Confidence Scoring**: Provides confidence levels for extracted information to help with validation

### 3. Multi-Currency Support with Real-Time Exchange Rates
- **Automatic Currency Conversion**: Converts foreign currencies to USD using real-time exchange rates
- **Exchange Rate Service**: Integrates with financial APIs to fetch current exchange rates
- **Historical Rate Support**: Can use historical rates for accurate financial reporting
- **Multiple Currency Handling**: Supports transactions in various currencies simultaneously

### 4. Database Integration
- **PostgreSQL Storage**: Stores processed financial data in a structured PostgreSQL database
- **Data Schema Management**: Implements proper database schema for financial information
- **Query Interface**: Provides tools to query and analyze stored financial data
- **Data Integrity**: Ensures data consistency and prevents duplicates

### 5. Statistical Analysis and Reporting
- **Financial Summaries**: Generates summaries of financial activities by category, time period, and vendor
- **Spending Patterns**: Identifies trends and patterns in spending behavior
- **Budget Tracking**: Compares actual spending against budget allocations
- **Custom Queries**: Allows custom analysis through flexible query interfaces

### 6. WhatsApp Messaging Integration
- **AWS End User Messaging Social**: Uses AWS Pinpoint for WhatsApp messaging instead of third-party services
- **Notification System**: Sends alerts and summaries via WhatsApp
- **Two-Way Communication**: Supports receiving commands and queries via WhatsApp
- **Secure Authentication**: Implements proper authentication for WhatsApp interactions

### 7. Session Management
- **Multi-User Support**: Handles multiple users with separate data isolation
- **Conversation Context**: Maintains context across multiple interactions
- **Interactive Processing**: Supports guided email processing workflows
- **Data Validation**: Allows users to confirm or correct extracted information

### 8. Memory Management
- **Long-Term Memory**: Implements persistent memory for storing user preferences and historical data
- **Contextual Recall**: Remembers important information from previous conversations
- **Semantic Search**: Enables searching through stored memories using natural language
- **Memory Strategies**: Uses different strategies for organizing and retrieving information

### 9. Security Features
- **Credential Management**: Securely stores and manages API credentials and sensitive information
- **Encryption**: Uses cryptography to protect sensitive data at rest
- **Permission Control**: Implements role-based access control for different functionalities
- **Audit Logging**: Maintains logs of all activities for security monitoring

### 10. Deployment and Infrastructure
- **Docker Support**: Containerized deployment for easy scaling and management
- **AWS Integration**: Designed to work seamlessly with AWS services
- **Configuration Management**: Flexible configuration system for different environments
- **Health Monitoring**: Built-in health checks and status reporting

## Key Tools and Capabilities

### Core Tools
1. **Calculator**: Basic mathematical calculations
2. **Current Time**: Get current time and date information
3. **Customer ID Lookup**: Find customer information by email address
4. **Order Management**: Query and manage customer orders
5. **Knowledge Base**: Access to product and service information

### Financial Tools
1. **Email Processing**: Search and process Gmail financial emails
2. **Financial Summary**: Generate statistical summaries of financial data
3. **Database Queries**: Query stored financial information
4. **Interactive Processing**: Guided email processing with user interaction
5. **Data Confirmation**: Allow users to confirm or modify extracted data
6. **Session Status**: Check the status of processing sessions

### Communication Tools
1. **WhatsApp Messaging**: Send messages via WhatsApp using AWS services
2. **Notification System**: Automated alerts and updates

### Memory Tools
1. **Long-Term Memory**: Persistent storage for conversation context
2. **Memory Retrieval**: Search and retrieve stored information

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure credentials:
   ```bash
   cp src/config/credentials_template.json src/config/credentials.json
   # Edit src/config/credentials.json with your credentials
   ```

3. Set up database:
   ```bash
   # Create PostgreSQL database and run src/init.sql to set up schema
   ```

4. Run the agent:
   ```bash
   python src/main.py
   ```

## WhatsApp Tool Usage

The WhatsApp tool uses AWS End User Messaging Social API. To use it:

1. Set up AWS Pinpoint with End User Messaging Social
2. Configure environment variables:
   ```bash
   export WHATSAPP_ORIGINATION_IDENTITY=your_whatsapp_business_number
   export WHATSAPP_APPLICATION_ID=your_application_id
   ```

3. Use the tool in your agent:
   ```python
   from src.tools.whatsapp_tool import send_whatsapp_message
   
   result = send_whatsapp_message(
       to_phone="+1234567890",
       message_body="Hello from WhatsApp!"
   )
   ```

## API Endpoints

### Agent Invocation
- **POST /**: Main endpoint for invoking the agent with a prompt

### Health and Monitoring
- **GET /health**: Health check endpoint for monitoring service status
- **GET /ready**: Readiness check for deployment verification

## Configuration

The agent can be configured through:
1. **Environment Variables**: For sensitive information like API keys
2. **Configuration Files**: JSON files in the src/config directory
3. **Runtime Parameters**: Command-line arguments when starting the service

## Testing

Run tests using:
```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
