import streamlit as st
import requests
import json

# Page config
st.set_page_config(page_title="Webhook Form", page_icon="📧", layout="centered")

# Title
st.title("📧 Send to Webhook")
st.markdown("---")

# Webhook URL
WEBHOOK_URL = "https://agentonline-u29564.vm.elestio.app/webhook/192d43hooksend"
TEST_WEBHOOK_URL = "https://agentonline-u29564.vm.elestio.app/webhook-test/192d43hooksend"

# Form
with st.form("webhook_form"):
    st.subheader("Enter Your Information")
    
    subject = st.text_input("Subject", placeholder="Enter subject...")
    email = st.text_input("Email", placeholder="Enter your email...")
    
    col1, col2 = st.columns(2)
    
    with col1:
        submit_button = st.form_submit_button("Send to Webhook", use_container_width=True)
    
    with col2:
        test_button = st.form_submit_button("Send to Test Webhook", use_container_width=True)

# Handle form submission
if submit_button or test_button:
    if not subject or not email:
        st.error("⚠️ Please fill in both fields!")
    else:
        # Prepare data
        data = {
            "subject": subject,
            "email": email
        }
        
        # Choose URL
        url = TEST_WEBHOOK_URL if test_button else WEBHOOK_URL
        
        # Show spinner while sending
        with st.spinner("Sending..."):
            try:
                response = requests.post(url, json=data, timeout=10)
                
                if response.status_code == 200:
                    st.success("✅ Successfully sent to webhook!")
                    st.json(data)
                    
                    # Show response if available
                    try:
                        st.subheader("Response from webhook:")
                        st.json(response.json())
                    except:
                        st.text(response.text)
                else:
                    st.error(f"❌ Error: Received status code {response.status_code}")
                    st.text(response.text)
                    
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection error. Please check the webhook URL.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

# Info section
st.markdown("---")
st.info("💡 **Tip:** The form will send your subject and email as JSON to the selected webhook endpoint.")

# Show current webhook URLs
with st.expander("🔗 Webhook URLs"):
    st.code(WEBHOOK_URL, language="text")
    st.code(TEST_WEBHOOK_URL, language="text")
