from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import EmailList, Email
from django.utils.timezone import now, timedelta
import csv
from io import TextIOWrapper


def homepage(request):
    """Render the homepage with an overview of the tool."""
    return render(request, 'homepage.html')

@login_required
def email_dashboard(request):
    user = request.user
    email_lists = EmailList.objects.filter(user=user)
    sent_emails = Email.objects.filter(user=user)

    # Email counts for the last 7 days
    email_data = []
    date_labels = []
    for i in range(6, -1, -1):  # Last 7 days
        day = now() - timedelta(days=i)
        date_labels.append(day.strftime('%Y-%m-%d'))
        email_data.append(sent_emails.filter(added_at__date=day.date()).count())

    # Today's email count
    today_email_count = sent_emails.filter(added_at__date=now().date()).count()

    context = {
        'email_lists': email_lists,
        'email_dates': date_labels,
        'email_counts': email_data,
        'total_emails': sent_emails.count(),
        'today_email_count': today_email_count,
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
        # Handle individual email addition
        email_address = request.POST.get('email_address')
        if email_address:
            if Email.objects.filter(email_address=email_address, email_list=email_list).exists():
                messages.error(request, "This email is already in the list.")
            else:
                Email.objects.create(email_list=email_list, email_address=email_address)
                messages.success(request, "Email added successfully.")
        
        # Handle CSV file upload
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            try:
                csv_reader = csv.reader(TextIOWrapper(csv_file.file, encoding='utf-8'))
                for row in csv_reader:
                    if len(row) > 0:  # Ensure the row is not empty
                        email = row[0].strip()  # Get the first column as email
                        if email and not Email.objects.filter(email_address=email, email_list=email_list).exists():
                            Email.objects.create(email_list=email_list, email_address=email)
                messages.success(request, "Emails added from CSV file successfully.")
            except Exception as e:
                messages.error(request, f"Error processing CSV file: {str(e)}")
        
        return redirect('add_email_to_list', list_id=list_id)
    
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
