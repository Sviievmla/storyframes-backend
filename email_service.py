import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.admin_email = os.getenv("ADMIN_EMAIL", self.smtp_username)
        
        # Check if email is configured
        self.is_configured = bool(self.smtp_username and self.smtp_password)
        
        if not self.is_configured:
            logger.warning("Email service is not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
    
    def send_order_confirmation(self, order_data: Dict, customer_email: str) -> bool:
        """Send order confirmation email to customer."""
        if not self.is_configured:
            logger.warning("Email not configured. Skipping order confirmation email.")
            return False
        
        try:
            subject = f"Order Confirmation - #{order_data['id']}"
            
            # Build items HTML
            items_html = ""
            for item in order_data.get('items', []):
                items_html += f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['product_name']}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item['quantity']}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">{item['currency']} {item['unit_price']:.2f}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">{item['currency']} {item['total_price']:.2f}</td>
                </tr>
                """
            
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4CAF50;">Thank You for Your Order!</h2>
                    <p>Your order has been confirmed and is being processed.</p>
                    
                    <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Order Details</h3>
                        <p><strong>Order ID:</strong> #{order_data['id']}</p>
                        <p><strong>PayPal Order ID:</strong> {order_data['paypal_order_id']}</p>
                        <p><strong>Status:</strong> {order_data['status']}</p>
                        <p><strong>Total:</strong> {order_data['currency']} {order_data['total']:.2f}</p>
                    </div>
                    
                    <h3>Order Items</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #f5f5f5;">
                                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Product</th>
                                <th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Qty</th>
                                <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Unit Price</th>
                                <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p>If you have any questions about your order, please contact us.</p>
                        <p style="color: #666; font-size: 12px;">This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(customer_email, subject, html)
            
        except Exception as e:
            logger.error(f"Error sending order confirmation email: {str(e)}")
            return False
    
    def send_admin_notification(self, order_data: Dict) -> bool:
        """Send new order notification to admin."""
        if not self.is_configured or not self.admin_email:
            logger.warning("Email not configured or admin email not set. Skipping admin notification.")
            return False
        
        try:
            subject = f"New Order Received - #{order_data['id']}"
            
            # Build items text
            items_text = ""
            for item in order_data.get('items', []):
                items_text += f"- {item['product_name']} x{item['quantity']} @ {item['currency']} {item['unit_price']:.2f} = {item['currency']} {item['total_price']:.2f}\n"
            
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2196F3;">New Order Received</h2>
                    
                    <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Order Information</h3>
                        <p><strong>Order ID:</strong> #{order_data['id']}</p>
                        <p><strong>PayPal Order ID:</strong> {order_data['paypal_order_id']}</p>
                        <p><strong>Status:</strong> {order_data['status']}</p>
                        <p><strong>Total:</strong> {order_data['currency']} {order_data['total']:.2f}</p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Customer Information</h3>
                        <p><strong>Name:</strong> {order_data.get('customer_name', 'N/A')}</p>
                        <p><strong>Email:</strong> {order_data.get('customer_email', 'N/A')}</p>
                        <p><strong>Phone:</strong> {order_data.get('customer_phone', 'N/A')}</p>
                    </div>
                    
                    <h3>Order Items</h3>
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px;">{items_text}</pre>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(self.admin_email, subject, html)
            
        except Exception as e:
            logger.error(f"Error sending admin notification email: {str(e)}")
            return False
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using SMTP."""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

# Singleton instance
email_service = EmailService()
