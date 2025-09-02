"""
Test script for WhatsApp tool
"""
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from whatsapp_tool import send_whatsapp_message_tool

def test_whatsapp_tool():
    """Test the WhatsApp tool"""
    print("Testing WhatsApp tool...")
    
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
        account_sid="invalid_sid",
        auth_token="invalid_token",
        from_phone="+0987654321"
    )
    
    print("Result with invalid credentials:", result)
    
    print("Test completed.")

if __name__ == "__main__":
    test_whatsapp_tool()
