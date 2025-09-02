"""
Test script for AWS WhatsApp tool
"""
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from whatsapp_tool import send_whatsapp_message_tool

def test_aws_whatsapp_tool():
    """Test the AWS WhatsApp tool"""
    print("Testing AWS WhatsApp tool...")
    
    # Test with missing credentials (should fail)
    result = send_whatsapp_message_tool(
        to_phone="+1234567890",
        message_body="Test message"
    )
    
    print("Result with missing credentials:", result)
    
    # Test with invalid credentials (should fail)
    result = send_whatsapp_message_tool(
        to_phone="+1234567890",
        message_body="Test message",
        origination_identity="invalid_number",
        application_id="invalid_app_id"
    )
    
    print("Result with invalid credentials:", result)
    
    print("Test completed.")

if __name__ == "__main__":
    test_aws_whatsapp_tool()
