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

## Key Features

1. **Financial Email Processing**: Automatically searches and processes Gmail financial emails (invoices, orders, statements)
2. **Currency Conversion**: Converts foreign currencies to USD using real-time exchange rates
3. **Database Storage**: Stores processed data in PostgreSQL database
4. **Statistical Analysis**: Provides statistical analysis and queries on financial data
5. **WhatsApp Integration**: Send WhatsApp messages using AWS End User Messaging Social
6. **LLM Enhancement**: Uses LLM for deep analysis of email content
7. **Memory Management**: Implements long-term memory for conversation context

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

3. Run the agent:
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.
