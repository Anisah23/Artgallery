import os
import requests
import json

class EmailService:
    @staticmethod
    def send_welcome_email(to_email, full_name, role):
        """Send welcome email to new users"""
        subject = "Welcome to ArtMarket!"
        
        role_message = "showcase your artwork to collectors worldwide" if role == "artist" else "discover and collect amazing artworks"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 20px; }}
                .button {{ background: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to ArtMarket!</h1>
                </div>
                <div class="content">
                    <h2>Hello {full_name}!</h2>
                    <p>Thank you for joining ArtMarket as a {role.title()}. We're excited to have you in our community!</p>
                    
                    <p>As a {role}, you can {role_message}.</p>
                    
                    <p>Here's what you can do next:</p>
                    <ul>
                        {'<li>Upload your first artwork and start selling</li><li>Set up your artist profile</li><li>Connect with collectors</li>' if role == 'artist' else '<li>Browse our gallery of unique artworks</li><li>Create your wishlist</li><li>Start collecting amazing art</li>'}
                    </ul>
                    
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    
                    <p>Happy {'creating' if role == 'artist' else 'collecting'}!</p>
                    <p>The ArtMarket Team</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService._send_email(to_email, subject, html_content)

    @staticmethod
    def send_password_reset(to_email, full_name, reset_token):
        """Send password reset email"""
        subject = "Reset Your ArtMarket Password"
        
        # In production, this should be your frontend URL
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #DC2626; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 20px; }}
                .button {{ background: #DC2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                .warning {{ background: #FEF3C7; border: 1px solid #F59E0B; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hello {full_name}!</h2>
                    <p>We received a request to reset your ArtMarket password.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    <a href="{reset_url}" class="button">Reset Password</a>
                    
                    <div class="warning">
                        <strong>Important:</strong> This link will expire in 1 hour for security reasons.
                    </div>
                    
                    <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
                    
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p>{reset_url}</p>
                    
                    <p>Best regards,<br>The ArtMarket Team</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService._send_email(to_email, subject, html_content)

    @staticmethod
    def send_order_confirmation(to_email, order):
        """Send order confirmation email"""
        subject = f"Order Confirmation - #{order.id}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 20px; }}
                .order-item {{ border-bottom: 1px solid #e5e7eb; padding: 10px 0; }}
                .total {{ font-weight: bold; font-size: 18px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>ArtMarket</h1>
                    <h2>Order Confirmation</h2>
                </div>
                <div class="content">
                    <p>Thank you for your order! Here are your order details:</p>
                    
                    <h3>Order #{order.id}</h3>
                    <p><strong>Status:</strong> {order.status}</p>
                    <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y')}</p>
                    
                    <h4>Items Ordered:</h4>
                    {"".join([f'''
                    <div class="order-item">
                        <strong>{getattr(item.artwork, 'title', 'Unknown')}</strong><br>
                        by {getattr(getattr(item.artwork, 'artist', None), 'username', 'Unknown Artist')}<br>
                        Quantity: {item.quantity} × ${getattr(item.artwork, 'price', 0)}<br>
                        Total: ${item.price}
                    </div>
                    ''' for item in order.items if item.artwork])}
                    
                    <div class="total">
                        Total Amount: ${order.total_amount}
                    </div>
                    
                    <p>We'll notify you when your order ships.</p>
                    <p>Thank you for shopping with ArtMarket!</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService._send_email(to_email, subject, html_content)

    @staticmethod
    def send_order_shipped(to_email, order, tracking_number=None):
        """Send order shipped notification"""
        subject = f"Your Order Has Shipped - #{order.id}"
        
        tracking_info = ""
        if tracking_number:
            tracking_info = f"<p><strong>Tracking Number:</strong> {tracking_number}</p>"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10B981; color: white; padding: 20px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>ArtMarket</h1>
                    <h2>Order Shipped!</h2>
                </div>
                <div class="content">
                    <p>Great news! Your order has been shipped.</p>
                    <p><strong>Order #:</strong> {order.id}</p>
                    {tracking_info}
                    <p>Your artwork is on its way to you. Please allow 5-7 business days for delivery.</p>
                    <p>Thank you for your patience!</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService._send_email(to_email, subject, html_content)

    @staticmethod
    def _send_email(to_email, subject, html_content):
        """Send email using Postmark"""
        postmark_token = os.getenv('POSTMARK_API_TOKEN', '35d30282-b672-47b0-aa50-109d97b65f2c')
        from_email = os.getenv('FROM_EMAIL', 'noreply@artmarket.com')
        
        try:
            url = 'https://api.postmarkapp.com/email'
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Postmark-Server-Token': postmark_token
            }
            
            data = {
                'From': from_email,
                'To': to_email,
                'Subject': subject,
                'HtmlBody': html_content,
                'MessageStream': 'outbound'
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data))
            return response.status_code == 200
            
        except Exception as e:
            print(f'Email sending failed: {str(e)}')
            return False