from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from .models import EmailList, Email

def create_email_list(request):
    if request.method == 'POST':
        list_name = request.POST.get('name')
        if EmailList.objects.filter(name=list_name).exists():
            messages.error(request, "An email list with this name already exists.")
        else:
            EmailList.objects.create(name=list_name)
            messages.success(request, "Email list created successfully.")
        return redirect('create_email_list')
    
    email_lists = EmailList.objects.all()
    return render(request, 'createlist.html', {'email_lists': email_lists})


def add_email_to_list(request, list_id):
    email_list = get_object_or_404(EmailList, id=list_id)
    if request.method == 'POST':
        email_address = request.POST.get('email_address')
        if Email.objects.filter(email_address=email_address, email_list=email_list).exists():
            messages.error(request, "This email is already in the list.")
        else:
            Email.objects.create(email_list=email_list, email_address=email_address)
            messages.success(request, "Email added successfully.")
        return redirect('add_email_to_list', list_id=list_id)
    
    emails = email_list.emails.all()
    return render(request, 'add_email_to_list.html', {'email_list': email_list, 'emails': emails})


def send_bulk_email(request):
    if request.method == 'POST':
        selected_list_id = request.POST.get('email_list')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        from_email = request.POST.get('from_email')

        if not selected_list_id:
            messages.error(request, "Please select an email list.")
            return redirect('send_bulk_email')

        email_list = EmailList.objects.filter(id=selected_list_id).first()
        if not email_list:
            messages.error(request, "Selected email list does not exist.")
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

        return redirect('send_bulk_email')

    email_lists = EmailList.objects.all()
    return render(request, 'send_bulk_email.html', {'email_lists': email_lists})