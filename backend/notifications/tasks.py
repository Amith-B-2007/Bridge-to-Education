"""
SMS notification tasks. Wrapped to work with or without Celery.
- If Celery is installed and broker is running, tasks run async via .delay()
- Otherwise, they run synchronously (good for local dev)
"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try to import celery; fall back to a no-op decorator for local dev
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    def shared_task(func):
        # Make the function callable both synchronously AND with .delay()
        func.delay = lambda *args, **kwargs: func(*args, **kwargs)
        return func


def _safe_send_sms(phone, message):
    """Send SMS via Fast2SMS if configured, otherwise just log."""
    try:
        from .sms_client import Fast2SMSClient
        from .models import SMSLog
        client = Fast2SMSClient()
        if not client.is_available():
            logger.info(f'[SMS DISABLED] Would send to {phone}: {message}')
            return {'return': False, 'message': 'SMS not configured'}
        result = client.send(phone, message)
        SMSLog.objects.create(
            phone=phone,
            message=message,
            status='sent' if result.get('return') else 'failed',
            api_response=result,
        )
        return result
    except Exception as e:
        logger.error(f'SMS send error: {e}')
        return {'return': False, 'error': str(e)}


@shared_task
def send_quiz_notification(parent_phone, student_name, score, total, subject, date_str):
    msg = f"Dear Parent, {student_name} scored {int(score)}/{int(total)} in {subject} Quiz on {date_str}. — RuralShiksha"
    return _safe_send_sms(parent_phone, msg)


@shared_task
def send_marks_notification(parent_phone, student_name, marks, subject):
    msg = f"Dear Parent, {student_name}'s {subject} marks have been updated to {marks}%. — RuralShiksha"
    return _safe_send_sms(parent_phone, msg)


@shared_task
def send_doubt_resolved_notification(parent_phone, student_name, doubt_title):
    msg = f"Dear Parent, {student_name}'s doubt '{doubt_title}' has been resolved. — RuralShiksha"
    return _safe_send_sms(parent_phone, msg)


@shared_task
def retry_failed_sms():
    try:
        from .models import SMSLog
        from .sms_client import Fast2SMSClient
        client = Fast2SMSClient()
        for log in SMSLog.objects.filter(status='failed', retries__lt=3) if hasattr(SMSLog, 'retries') else []:
            result = client.send(log.phone, log.message)
            log.api_response = result
            log.status = 'sent' if result.get('return') else 'failed'
            log.save()
    except Exception as e:
        logger.error(f'Retry SMS error: {e}')
