from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import EmailList, Email

@login_required
def email_dashboard(request):
    """Display the user's email dashboard."""
    user = request.user
    
    # Fetch the user's email lists and emails
    email_lists = EmailList.objects.filter(user=user)
    sent_emails = Email.objects.filter(user=user)
    
    # Count the total number of lists and emails
    total_lists = email_lists.count()
    total_emails = sent_emails.count()
    
    # Get a list of recent sent emails (optional, e.g., last 5)
    recent_emails = sent_emails.order_by('-added_at')[:5]
    
    context = {
        'total_lists': total_lists,
        'total_emails': total_emails,
        'recent_emails': recent_emails,
        'email_lists': email_lists,  # for sidebar navigation if needed
        'sent_emails': sent_emails,  # for showing email data
    }
    
    return render(request, 'email_dashboard.html', context)

@login_required
def create_email_list(request):
    """Create a new email list for the logged-in user."""
    if request.method == 'POST':
        list_name = request.POST.get('name')
        if EmailList.objects.filter(name=list_name, user=request.user).exists():
            messages.error(request, "An email list with this name already exists.")
        else:
            EmailList.objects.create(name=list_name, user=request.user)
            messages.success(request, "Email list created successfully.")
        return redirect('email_dashboard')  # Redirect to dashboard after adding list
    
    # Fetch only the email lists created by the logged-in user
    email_lists = EmailList.objects.filter(user=request.user)
    return render(request, 'createlist.html', {'email_lists': email_lists})

@login_required
def add_email_to_list(request, list_id):
    """Add emails to the selected email list of the logged-in user."""
    email_list = get_object_or_404(EmailList, id=list_id, user=request.user)
    if request.method == 'POST':
        email_address = request.POST.get('email_address')
        if Email.objects.filter(email_address=email_address, email_list=email_list).exists():
            messages.error(request, "This email is already in the list.")
        else:
            Email.objects.create(email_list=email_list, email_address=email_address)
            messages.success(request, "Email added successfully.")
        return redirect('email_dashboard')  # Redirect to dashboard after adding email
    
    # Fetch only the emails from the user's selected email list
    emails = email_list.emails.all()
    return render(request, 'add_email_to_list.html', {'email_list': email_list, 'emails': emails})

@login_required
def send_bulk_email(request):
    """Send emails to a selected list owned by the logged-in user."""
    if request.method == 'POST':
        selected_list_id = request.POST.get('email_list')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        from_email = request.POST.get('from_email')

        if not selected_list_id:
            messages.error(request, "Please select an email list.")
            return redirect('send_bulk_email')

        # Ensure the selected list belongs to the logged-in user
        email_list = EmailList.objects.filter(id=selected_list_id, user=request.user).first()
        if not email_list:
            messages.error(request, "You do not have permission to access this list.")
            return redirect('send_bulk_email')

        recipient_list = [email.email_address for email in email_list.emails.all()]
        if not recipient_list:
            messages.warning(request, "The selected email list is empty.")
            return redirect('send_bulk_email')

        failed_recipients = []
        for recipient in recipient_list:
            try:
                send_mail(subject, message, from_email, [recipient])
            except Exception as e:
                failed_recipients.append(recipient)

        if not failed_recipients:
            messages.success(request, f"Emails sent successfully to {len(recipient_list)} recipients.")
        else:
            failed_count = len(failed_recipients)
            messages.warning(request, f"Emails sent to {len(recipient_list) - failed_count} recipients, "
                                      f"but failed for {failed_count}: {', '.join(failed_recipients)}.")

        return redirect('email_dashboard')  # Redirect to dashboard after sending emails

    # Fetch only the email lists created by the logged-in user
    email_lists = EmailList.objects.filter(user=request.user)
    return render(request, 'send_bulk_email.html', {'email_lists': email_lists})
