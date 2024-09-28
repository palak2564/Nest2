from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, NoteUploadForm
from .models import Note , MyNotes ,  Upvote , Order
from django.shortcuts import render, redirect
from .forms import PrintOrderForm
from .models import Order, PrintPricing
from PyPDF2 import PdfReader
from django.core.files.storage import FileSystemStorage
from .models import Note , MyNotes , Profile, Upvote
from datetime import datetime
from .models import Profile

from .models import DownloadedNotes  # Import your model here



def landingpage(request):
    return render(request, 'index.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('landingpage')  # Ensure this URL name is correct
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

@login_required
def upload_note_view(request):
    if request.method == 'POST':
        form = NoteUploadForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.uploaded_by = request.user
            note.save()
            return redirect('success_page')
    else:
        form = NoteUploadForm()
    return render(request, 'upload_note.html', {'form': form})

def success_page(request):
    return render(request, 'success_page.html')

def search_notes_view(request):
    branches = ['CSE', 'ECE', 'ME']  # Replace with actual branches
    semesters = range(1, 9)  # Assuming 8 semesters

    keyword = request.GET.get('keyword', '')
    branch = request.GET.get('branch', '')
    semester = request.GET.get('semester', '')

    notes = Note.objects.filter(is_approved=True)

    if keyword:
        notes = notes.filter(subject__icontains=keyword)

    if branch:
        notes = notes.filter(branch=branch)

    if semester:
        notes = notes.filter(semester=int(semester))

    context = {
        'notes': notes,
        'branches': branches,
        'semesters': semesters,
    }

    return render(request, 'search_notes.html', context)

@login_required
def view_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, is_approved=True)
    
    # Check if the user has already added this note to "My Notes"
    added_to_my_notes = note in request.user.notes.all()  # Ensure you have a many-to-many relationship
    upvote_count = note.upvote_set.count()
    # Build the full URL for the PDF file
    pdf_url = request.build_absolute_uri(note.file.url) if note.file else None
    has_upvoted = note.upvote_set.filter(user=request.user).exists() if request.user.is_authenticated else False

    context = {
        'note': note,
        'added_to_my_notes': added_to_my_notes,
        'pdf_url': pdf_url,
         'upvote_count': upvote_count,
          'has_upvoted': has_upvoted,
    }
    return render(request, 'view_note.html', context)

@login_required
def add_to_my_notes(request, note_id):
    note = get_object_or_404(Note, id=note_id, is_approved=True)
    user = request.user

    # Check if the note is already added to "My Notes"
    if not MyNotes.objects.filter(user=user, note=note).exists():
        MyNotes.objects.create(user=user, note=note)  # Add to My Notes
        print("Note added to My Notes")
    else:
        print("Note already in My Notes")

    # Redirect back to the view_note page after adding the note
    return redirect('view_note', note_id=note.id)

@login_required
def downloaded_notes_view(request):
    # Assuming you have a model or field to track downloaded notes
    downloaded_notes = DownloadedNotes.objects.filter(user=request.user)
    return render(request, 'downloaded_notes.html', {'downloaded_notes': downloaded_notes})

@login_required
def my_notes(request):
    notes = MyNotes.objects.filter(user=request.user)
    return render(request, 'my_notes.html', {'notes': notes})

@login_required
def upvote_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    Upvote.objects.get_or_create(user=request.user, note=note)
    return redirect('view_note', note_id=note.id)


@login_required
def order_printout(request):
    if request.method == 'POST':
        form = PrintOrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user

            # Count pages in the PDF using the updated method
            pdf = request.FILES['pdf_file']
            pdf_reader = PdfReader(pdf)
            order.page_count = len(pdf_reader.pages)  # Updated line

            # Calculate price
            order.calculate_price()

            # Save the order
            order.save()

            return redirect('order_success')  # Redirect to success page
    else:
        form = PrintOrderForm()

    return render(request, 'order_printout.html', {'form': form})



# Add the order_success view if missing
def order_success(request):
    return render(request, 'order_success.html')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'my_orders.html', {'orders': orders})


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_detail.html', {'order': order})
     # Check if the note has 10 upvotes and award badge
    note.check_and_award_badge()
    return redirect('view_note', note_id=note.id)

# Profile page view
@login_required
def profile_view(request):
    user = request.user

    # Ensure the user has a profile
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Handle form submission to update user and profile details
        full_name = request.POST.get('full_name')
        
        # Default full name to username if empty
        user.full_name = full_name if full_name else user.username

        # Handle date of birth parsing to ensure correct format
        dob_str = request.POST.get('dob')
        if dob_str:
            try:
                user.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                # Handle invalid date format
                return render(request, 'profile.html', {
                    'error': 'Invalid date format. Please use YYYY-MM-DD.',
                    'full_name': user.full_name,
                    'dob': dob_str,
                    'semester': request.POST.get('semester'),
                    'year': request.POST.get('year'),
                    'branch': request.POST.get('branch'),
                    'email': request.POST.get('email'),
                    'bio': request.POST.get('bio'),
                    'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                })

        user.semester = request.POST.get('semester')
        user.year = request.POST.get('year')
        user.branch = request.POST.get('branch')
        user.email = request.POST.get('email')
        user.save()

        # Update profile-specific information
        profile.bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            profile.profile_picture = profile_picture
        profile.save()

        return redirect('profile')

    # Pre-fill form with user information and use username if full_name is missing
    context = {
        'full_name': user.full_name if user.full_name else user.username,
        'dob': user.dob.strftime('%Y-%m-%d') if user.dob else '',
        'semester': user.semester,
        'year': user.year,
        'branch': user.branch,
        'email': user.email,
        'bio': profile.bio,
        'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
    }

    return render(request, 'profile.html', context)