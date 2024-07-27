from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserDetailsForm, FeedbackForm
from .models import UserDetails
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os

# Define the scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def index(request):
    """View for collecting user details."""
    if request.method == 'POST':
        form = UserDetailsForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session['user_id'] = user.id
            return redirect('get_emails')
    else:
        form = UserDetailsForm()
    return render(request, 'user_details/index.html', {'form': form})

def get_emails(request):
    """View for fetching and selecting emails from Gmail."""
    user_id = request.session.get('user_id')
    user = UserDetails.objects.get(id=user_id)

    # Check if credentials are available
    if 'credentials' not in request.session:
        return redirect('authorize')

    creds = Credentials(**request.session['credentials'])
    service = build('gmail', 'v1', credentials=creds)

    try:
        # Fetch email messages
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
        messages = results.get('messages', [])
    except Exception as e:
        return HttpResponse(f"An error occurred while fetching emails: {e}")

    email_data = []
    for msg in messages:
        try:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            email_data.append({
                'id': msg['id'],
                'snippet': msg_data['snippet']
            })
        except Exception as e:
            return HttpResponse(f"An error occurred while fetching email details: {e}")

    if request.method == 'POST':
        selected_email_id = request.POST.get('email_id')
        if selected_email_id:
            try:
                email = service.users().messages().get(userId='me', id=selected_email_id).execute()
                user.email_id = email['id']
                user.email_subject = next(header['value'] for header in email['payload']['headers'] if header['name'] == 'Subject')
                user.email_body = email['snippet']
                user.save()
                return redirect('feedback')
            except Exception as e:
                return HttpResponse(f"An error occurred while fetching the selected email: {e}")

    return render(request, 'user_details/get_emails.html', {'emails': email_data})

def feedback(request):
    """View for providing feedback on the selected email."""
    user_id = request.session.get('user_id')
    user = UserDetails.objects.get(id=user_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('thank_you')
    else:
        form = FeedbackForm()

    return render(request, 'user_details/feedback.html', {'form': form, 'email_body': user.email_body})

def thank_you(request):
    """View to display a thank-you message after feedback submission."""
    return render(request, 'user_details/thank_you.html')

def authorize(request):
    """View to handle OAuth2 authorization with Gmail API."""
    flow = InstalledAppFlow.from_client_secrets_file(
        os.path.join(os.path.dirname(__file__), 'credentials.json'), SCOPES)
    
    # Check if credentials are in the session
    if 'credentials' in request.session:
        creds = Credentials(**request.session['credentials'])
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        request.session['credentials'] = creds_to_dict(creds)
        return redirect('get_emails')

    # For local server, open the browser and complete the authorization
    authorization_url, state = flow.authorization_url(
        access_type='offline', 
        include_granted_scopes='true'
    )
    
    # Redirect the user to the authorization URL
    return redirect(authorization_url)

def callback(request):
    """Callback view to handle the OAuth2 authorization response."""
    state = request.GET.get('state')
    flow = InstalledAppFlow.from_client_secrets_file(
        os.path.join(os.path.dirname(__file__), 'credentials.json'), SCOPES)
    
    # Complete the authorization flow
    flow.fetch_token(authorization_response=request.get_full_path())

    creds = flow.credentials
    request.session['credentials'] = creds_to_dict(creds)
    
    # Redirect to the get_emails view
    return redirect('get_emails')


def creds_to_dict(creds):
    """Convert OAuth2 credentials to a dictionary."""
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
