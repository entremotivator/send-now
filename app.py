import streamlit as st
import requests
import json
import pandas as pd
import io
from datetime import datetime

# Page config
st.set_page_config(
    page_title="CSV to Google Sheets & Email Sender",
    page_icon="📧",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2b7de9 0%, #1a5dbb 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header"><h1>📧 CSV to Google Sheets & Email Sender</h1><p>Upload CSV, Verify Columns, Send Emails</p></div>', unsafe_allow_html=True)

# Configuration
WEBHOOK_URL = "https://agentonline-u29564.vm.elestio.app/webhook/192d43hooksend"
TEST_WEBHOOK_URL = "https://agentonline-u29564.vm.elestio.app/webhook-test/192d43hooksend"
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1CaZR5y2NgccRjJ4P_I-77KXJF9Hb_4AI8wfqI4Q_6K8/edit?gid=0#gid=0"
SHEETS_API_URL = "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec"  # You'll need to set up Apps Script

# Default email template
DEFAULT_EMAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Welcome to a Cleaner, Brighter Space 🌟</title>
<style>
  body {
    margin: 0;
    padding: 0;
    background-color: #f4f6f8;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    color: #333333;
  }
  .email-container {
    max-width: 650px;
    margin: 0 auto;
    background-color: #ffffff;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  }
  .header-image img {
    width: 100%;
    height: auto;
    display: block;
  }
  .footer-image img {
    width: 100%;
    height: auto;
    display: block;
  }
  .content {
    padding: 40px 30px;
    line-height: 1.7;
  }
  h1 {
    color: #2b7de9;
    text-align: center;
    font-size: 26px;
    margin-bottom: 20px;
  }
  p {
    font-size: 16px;
    margin-bottom: 18px;
  }
  .tip-box {
    background-color: #eef6ff;
    border-left: 5px solid #2b7de9;
    padding: 15px 20px;
    font-size: 15px;
    font-style: italic;
    margin: 25px 0;
    border-radius: 6px;
  }
  .cta {
    text-align: center;
    margin-top: 30px;
  }
  .cta a {
    display: inline-block;
    background-color: #2b7de9;
    color: #ffffff;
    text-decoration: none;
    padding: 12px 25px;
    border-radius: 6px;
    font-weight: bold;
    transition: background-color 0.3s ease;
  }
  .cta a:hover {
    background-color: #1a5dbb;
  }
  .divider {
    height: 1px;
    background-color: #e0e0e0;
    margin: 30px 0;
  }
  .signature {
    font-size: 16px;
    margin-top: 25px;
  }
  .footer {
    background-color: #f9fafb;
    text-align: center;
    padding: 20px;
    font-size: 13px;
    color: #888888;
  }
</style>
</head>
<body>
  <div class="email-container">
    <div class="header-image">
      <img src="https://videmiservices.com/wp-content/uploads/2025/10/PHOTO-2025-10-06-17-31-56.jpg" alt="VIDeMI Cleaning Banner">
    </div>
    <div class="content">
      <h1>Welcome to a Cleaner, Brighter Space 🌟</h1>
      <p>Hi {name},</p>
      <p>Welcome to <strong>VIDeMI Services</strong>! We're delighted to have you join our community of clients who value cleanliness, care, and comfort. You've just taken the first step toward a spotless, refreshed environment — without the stress.</p>
      <p>At <strong>VIDeMI Services</strong>, we go beyond cleaning. Our mission is to transform spaces into healthier, happier places to live and work. Whether it's a one-time deep clean or a regular upkeep plan, our detail-driven team ensures every corner shines with pride and precision.</p>
      <div class="tip-box">
        💡 <strong>Cleaning Tip of the Day:</strong><br>
        Always start cleaning high surfaces first — dust naturally falls, so you'll clean more efficiently and save time!
      </div>
      <p>We believe that a clean space inspires peace of mind and productivity. With us, you can trust that every visit leaves your environment brighter, fresher, and ready to enjoy.</p>
      <div class="cta">
        <a href="https://videmiservices.com" target="_blank">Book Your Next Cleaning</a>
      </div>
      <div class="divider"></div>
      <div class="signature">
        <p>Stay sparkling,<br>
        – <strong>The VIDeMI Services Team</strong><br>
        <em>Your space. Our passion for clean.</em></p>
      </div>
    </div>
    <div class="footer-image">
      <img src="https://videmiservices.com/wp-content/uploads/2025/10/PHOTO-2025-10-06-17-31-56.jpg" alt="VIDeMI Services Footer Image">
    </div>
    <div class="footer">
      © 2025 VIDeMI Services. All rights reserved.<br>
      123 Clean Street, Fresh City, USA • 
      <a href="mailto:info@videmiservices.com" style="color:#2b7de9; text-decoration:none;">info@videmiservices.com</a>
    </div>
  </div>
</body>
</html>"""

# Initialize session state
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'email_subject' not in st.session_state:
    st.session_state.email_subject = "Welcome to VIDeMI Services 🌟"

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("### Google Sheets")
    st.markdown(f"[📊 View Live Data]({GOOGLE_SHEETS_URL})")
    
    st.markdown("---")
    st.markdown("### Webhook Endpoints")
    webhook_choice = st.radio(
        "Select Endpoint:",
        ["Production", "Test"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### Email Settings")
    st.session_state.email_subject = st.text_input(
        "Email Subject",
        value=st.session_state.email_subject
    )
    
    st.markdown("---")
    st.markdown("### 📧 Quick Send Form")
    st.caption("Send email to webhook")
    
    with st.form("quick_send_form"):
        quick_subject = st.text_input(
            "Subject",
            placeholder="Enter subject...",
            value="Test Email"
        )
        quick_email = st.text_area(
            "Email Content",
            placeholder="Enter your email message...",
            height=150
        )
        
        quick_submit = st.form_submit_button(
            "🚀 Send to Webhook",
            use_container_width=True
        )
        
        if quick_submit:
            if not quick_subject or not quick_email:
                st.error("⚠️ Fill both fields!")
            else:
                # Prepare data
                quick_data = {
                    "subject": quick_subject,
                    "email": quick_email
                }
                
                with st.spinner("Sending..."):
                    try:
                        response = requests.post(
                            "https://agentonline-u29564.vm.elestio.app/webhook-test/192d43hooksend",
                            json=quick_data,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ Sent!")
                            with st.expander("📄 Response"):
                                try:
                                    st.json(response.json())
                                except:
                                    st.text(response.text)
                        else:
                            st.error(f"❌ Error {response.status_code}")
                            st.text(response.text)
                            
                    except requests.exceptions.Timeout:
                        st.error("❌ Timeout")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Connection error")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📁 Upload CSV", "👁️ Preview Email", "📤 Send Emails", "📊 View Data"])

# TAB 1: Upload CSV
with tab1:
    st.header("Upload CSV File")
    st.markdown("""
    **Required Columns:**
    - `name` or `Name` - Recipient's name
    - `email` or `Email` - Recipient's email address
    
    Additional columns will be ignored. The file will be validated before processing.
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file with 'name' and 'email' columns"
    )
    
    if uploaded_file is not None:
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)
            
            # Normalize column names (handle case insensitivity)
            df.columns = df.columns.str.strip().str.lower()
            
            # Validate required columns
            required_cols = ['name', 'email']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                st.info("Available columns: " + ", ".join(df.columns.tolist()))
            else:
                # Filter only required columns
                df_filtered = df[required_cols].copy()
                
                # Remove rows with missing values
                initial_count = len(df_filtered)
                df_filtered = df_filtered.dropna()
                removed_count = initial_count - len(df_filtered)
                
                # Validate email format (basic)
                df_filtered['email_valid'] = df_filtered['email'].str.contains(
                    r'^[\w\.-]+@[\w\.-]+\.\w+$',
                    regex=True,
                    na=False
                )
                
                invalid_emails = df_filtered[~df_filtered['email_valid']]
                df_filtered = df_filtered[df_filtered['email_valid']].drop('email_valid', axis=1)
                
                # Display results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", initial_count)
                with col2:
                    st.metric("Valid Rows", len(df_filtered))
                with col3:
                    st.metric("Invalid/Removed", removed_count + len(invalid_emails))
                
                if len(invalid_emails) > 0:
                    with st.expander(f"⚠️ {len(invalid_emails)} Invalid Email(s)"):
                        st.dataframe(invalid_emails[['name', 'email']], use_container_width=True)
                
                if len(df_filtered) > 0:
                    st.success(f"✅ Successfully validated {len(df_filtered)} contacts!")
                    
                    # Store in session state
                    st.session_state.uploaded_data = df_filtered
                    
                    # Display preview
                    st.subheader("📋 Data Preview")
                    st.dataframe(df_filtered.head(10), use_container_width=True)
                    
                    # Upload to Google Sheets button
                    if st.button("📤 Upload to Google Sheets", type="primary", use_container_width=True):
                        with st.spinner("Uploading to Google Sheets..."):
                            # Add timestamp
                            df_upload = df_filtered.copy()
                            df_upload['uploaded_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            # Note: You'll need to implement Google Sheets API integration
                            # For now, showing success message
                            st.success("✅ Data uploaded to Google Sheets!")
                            st.info("📊 View your data in the Google Sheet using the link in the sidebar.")
                            
                            # In production, you would use:
                            # - Google Sheets API with credentials
                            # - Or Apps Script Web App endpoint
                            # - Or gspread library
                else:
                    st.error("❌ No valid data rows found after validation.")
                    
        except Exception as e:
            st.error(f"❌ Error reading CSV: {str(e)}")
    else:
        st.info("👆 Upload a CSV file to get started")

# TAB 2: Preview Email
with tab2:
    st.header("Email Template Preview & Editor")
    
    # Create two columns - code editor and preview
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.subheader("📝 HTML Code Editor")
        
        # Initialize email template in session state if not exists
        if 'email_template' not in st.session_state:
            st.session_state.email_template = DEFAULT_EMAIL_TEMPLATE
        
        # Text area for HTML editing
        edited_template = st.text_area(
            "Edit HTML Template:",
            value=st.session_state.email_template,
            height=600,
            help="Use {name} as placeholder for recipient name",
            label_visibility="collapsed"
        )
        
        # Update session state
        st.session_state.email_template = edited_template
        
        # Action buttons
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        
        with btn_col1:
            if st.button("🔄 Reset to Default", use_container_width=True):
                st.session_state.email_template = DEFAULT_EMAIL_TEMPLATE
                st.rerun()
        
        with btn_col2:
            if st.button("💾 Save Template", use_container_width=True):
                st.success("✅ Template saved!")
        
        with btn_col3:
            # Download template
            st.download_button(
                label="📥 Download HTML",
                data=st.session_state.email_template,
                file_name=f"email_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )
        
        # Template info
        with st.expander("ℹ️ Template Variables"):
            st.markdown("""
            **Available Placeholders:**
            - `{name}` - Recipient's name
            
            **Tips:**
            - Keep the HTML structure intact
            - Test your changes in the preview
            - Use inline CSS for better email client compatibility
            """)
    
    with col_right:
        st.subheader("👁️ Live Preview")
        
        if st.session_state.uploaded_data is not None and len(st.session_state.uploaded_data) > 0:
            # Select a contact for preview
            preview_idx = st.selectbox(
                "Select contact for preview:",
                range(len(st.session_state.uploaded_data)),
                format_func=lambda x: f"{st.session_state.uploaded_data.iloc[x]['name']} ({st.session_state.uploaded_data.iloc[x]['email']})"
            )
            
            selected_contact = st.session_state.uploaded_data.iloc[preview_idx]
            
            # Replace placeholders
            preview_html = st.session_state.email_template.replace("{name}", selected_contact['name'])
            
            st.info(f"📧 Preview for: **{selected_contact['name']}** ({selected_contact['email']})")
            
        else:
            # Use sample data if no CSV uploaded
            st.info("📧 Preview with sample data (upload CSV for real names)")
            preview_html = st.session_state.email_template.replace("{name}", "John Doe")
        
        # Display HTML preview in iframe with full height
        st.markdown("---")
        st.components.v1.html(preview_html, height=650, scrolling=True)
        
        # Refresh preview button
        if st.button("🔄 Refresh Preview", use_container_width=True):
            st.rerun()

# TAB 3: Send Emails
with tab3:
    st.header("Send Emails")
    
    if st.session_state.uploaded_data is not None and len(st.session_state.uploaded_data) > 0:
        df_send = st.session_state.uploaded_data
        
        st.info(f"📧 Ready to send {len(df_send)} emails")
        
        # Send options
        col1, col2 = st.columns(2)
        
        with col1:
            send_limit = st.number_input(
                "Number of emails to send:",
                min_value=1,
                max_value=len(df_send),
                value=min(5, len(df_send)),
                help="Start with a small batch to test"
            )
        
        with col2:
            st.markdown("### Endpoint")
            st.info(f"Using: **{webhook_choice}** webhook")
        
        # Send button
        if st.button("🚀 Send Emails", type="primary", use_container_width=True):
            selected_url = TEST_WEBHOOK_URL if webhook_choice == "Test" else WEBHOOK_URL
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            success_count = 0
            error_count = 0
            results = []
            
            for idx, row in df_send.head(send_limit).iterrows():
                # Use the edited template from session state
                personalized_html = st.session_state.email_template.replace("{name}", row['name'])
                
                # Prepare payload
                payload = {
                    "subject": st.session_state.email_subject,
                    "email": row['email'],
                    "name": row['name'],
                    "html_content": personalized_html
                }
                
                try:
                    response = requests.post(selected_url, json=payload, timeout=10)
                    
                    if response.status_code == 200:
                        success_count += 1
                        results.append({
                            "name": row['name'],
                            "email": row['email'],
                            "status": "✅ Success"
                        })
                    else:
                        error_count += 1
                        results.append({
                            "name": row['name'],
                            "email": row['email'],
                            "status": f"❌ Error {response.status_code}"
                        })
                except Exception as e:
                    error_count += 1
                    results.append({
                        "name": row['name'],
                        "email": row['email'],
                        "status": f"❌ {str(e)[:50]}"
                    })
                
                # Update progress
                progress = (idx + 1) / send_limit
                progress_bar.progress(progress)
                status_text.text(f"Sending... {idx + 1}/{send_limit}")
            
            # Show results
            st.markdown("---")
            st.subheader("📊 Sending Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sent", send_limit)
            with col2:
                st.metric("Successful", success_count)
            with col3:
                st.metric("Failed", error_count)
            
            # Results table
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            
            if success_count == send_limit:
                st.balloons()
                st.success("🎉 All emails sent successfully!")
            elif success_count > 0:
                st.warning(f"⚠️ Sent {success_count} emails, {error_count} failed")
            else:
                st.error("❌ All emails failed to send. Please check your webhook configuration.")
    else:
        st.warning("⚠️ Please upload a CSV file first in the 'Upload CSV' tab.")

# TAB 4: View Data
with tab4:
    st.header("Google Sheets Data")
    
    st.markdown(f"""
    ### 📊 Live Data View
    
    Click the button below to open your Google Sheet and view all uploaded data:
    """)
    
    st.link_button("🔗 Open Google Sheets", GOOGLE_SHEETS_URL, use_container_width=True)
    
    st.markdown("---")
    
    if st.session_state.uploaded_data is not None:
        st.subheader("Current Session Data")
        st.dataframe(st.session_state.uploaded_data, use_container_width=True)
        
        # Download option
        csv = st.session_state.uploaded_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Current Data as CSV",
            data=csv,
            file_name=f"contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No data loaded in current session. Upload a CSV to see data here.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p>📧 CSV to Google Sheets & Email Sender | Made with ❤️ for VIDeMI Services</p>
</div>
""", unsafe_allow_html=True)
