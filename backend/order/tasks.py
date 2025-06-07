import imaplib
import email
import re
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
from email.header import decode_header
from transformers import pipeline

logger = logging.getLogger(__name__)

logger.info("Loading zero-shot classification model")
nlp = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
logger.info("Model loaded successfully")

@shared_task
def process_confirmation_email():
    logger.info("Starting process_confirmation_email task")
    try:
        logger.info("Connecting to IMAP server")
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        logger.info("Logged in to IMAP server")
        mail.select('inbox')
        logger.info("Selected inbox")

        logger.info('Searching for emails with subject "Order Confirmation Received"')
        _, message_numbers = mail.search(None, '(UNSEEN FROM "%s" SUBJECT "Order Confirmation Received")' % settings.EMAIL_HOST_USER)
        logger.info(f"Found {len(message_numbers[0].split())} matching emails")


        for num in message_numbers[0].split():
            logger.info(f"Fetching email number {num}")
            _, msg_data = mail.fetch(num, '(RFC822)')
            email_body = msg_data[0][1]
            msg = email.message_from_bytes(email_body)

            subject, encoding = decode_header(msg['subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8')
            logger.info(f"Processing email with subject: {subject}")

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()
            logger.info(f"Email body: {body[:100]}...")

            candidate_labels = ["order confirmation", "order cancellation", "inquiry", "spam"]
            logger.info("Running LLM classification")
            result = nlp(body, candidate_labels)
            logger.info(f"LLM classification result: {result}")

            if result['labels'][0] == "order confirmation" and result['scores'][0] > 0.7:
                logger.info("Positive intent detected, extracting order ID")
                match = re.search(r'Order ID: (\w+)', body)
                if match:
                    order_id = match.group(1)
                    logger.info(f"Found order ID: {order_id}")
                    try:
                        order = Order.objects.get(order_id=order_id, status='Order Placed')
                        order.status = 'Confirmed'
                        order.save()
                        logger.info(f"Order {order_id} status updated to Confirmed")

                        send_mail(
                            subject=f'Order {order_id} Confirmed',
                            message=(
                                f"Dear {order.customer_name},\n"
                                f"Your order {order_id} has been confirmed.\n"
                                f"Product: {order.product.name}\n"
                                f"Quantity: {order.quantity}\n"
                                f"Total Cost: {order.total_cost}"
                            ),
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[order.customer_email],
                            html_message=(
                                f"<p>Dear {order.customer_name},</p>"
                                f"<p>Your order {order_id} has been confirmed.</p>"
                                f"<ul>"
                                f"<li>Product: {order.product.name}</li>"
                                f"<li>Quantity: {order.quantity}</li>"
                                f"<li>Total Cost: {order.total_cost}</li>"
                                f"</ul>"
                            ),
                        )
                        logger.info(f"Confirmation email sent to {order.customer_email}")
                    except Order.DoesNotExist:
                        logger.info(f"Order {order_id} not found or already confirmed")
                else:
                    logger.warning("No order ID found in email body")
            else:
                logger.info(f"Email not classified as positive (label: {result[0]['label']}, score: {result[0]['score']})")

        mail.logout()
        logger.info("Logged out from IMAP server")
    except Exception as e:
        logger.error(f"Error processing emails: {str(e)}", exc_info=True)