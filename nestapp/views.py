# myapp/views.py
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import SignupForm, NoteUploadForm
from django.contrib.auth.decorators import login_required
from .models import Note

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
            return redirect('landingpage')
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

    notes = Note.objects.all()

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
