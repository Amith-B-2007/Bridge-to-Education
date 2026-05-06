import requests
import os
import logging

logger = logging.getLogger(__name__)

class Fast2SMSClient:
    def __init__(self):
        self.api_key = os.getenv('FAST2SMS_API_KEY', '')
        self.url = 'https://www.fast2sms.com/dev/bulkV2'

    def send(self, phone, message):
        """Send SMS via Fast2SMS API."""
        if not self.api_key:
            logger.warning('Fast2SMS API key not configured')
            return {'success': False, 'error': 'API key not configured'}
        
        # Normalize phone number
        if isinstance(phone, str):
            phone = phone.strip()
            if not phone.startswith('+'):
                if len(phone) == 10:
                    phone = f'+91{phone}'
                elif not phone.startswith('91'):
                    phone = f'+{phone}'
        
        headers = {
            'authorization': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        payload = {
            'variables_values': phone,
            'route': 'otp',
            'numbers': phone,
            'message': message
        }
        
        try:
            response = requests.post(self.url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f'Fast2SMS error: {str(e)}')
            return {'success': False, 'error': str(e)}

    def is_available(self):
        """Check if SMS service is configured."""
        return bool(self.api_key)
