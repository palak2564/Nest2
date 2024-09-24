from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin




# BADGE_OPTION 
# class Badge(models.Model):
#     BADGE_TYPE_CHOICES = [
#         ('upvoter', 'Upvote Master'),
#         # Add more badges if needed
#     ]
#     user = models.ForeignKey(NestUser, on_delete=models.CASCADE, related_name="badges")
#     badge_type = models.CharField(max_length=50, choices=BADGE_TYPE_CHOICES)
#     awarded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.user.username} - {self.badge_type}'


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  # Ensure the superuser is active
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)


class NestUser(AbstractBaseUser, PermissionsMixin):
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('ME', 'Mechanical Engineering'),
        # Add other branches here
    ]

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES)
    notes = models.ManyToManyField('Note', related_name='added_by_users')

    
    is_active = models.BooleanField(default=True)  # Needed for login
    is_staff = models.BooleanField(default=False)  # Needed for admin access
    is_superuser = models.BooleanField(default=False)  # Superuser status
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return self.username



class Note(models.Model):

    BRANCH_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('ME', 'Mechanical Engineering'),
        # Add other branches here
    ]
    SEMESTER_CHOICES = [(i, f'Semester {i}') for i in range(1, 9)]

    subject = models.CharField(max_length=255)
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES)
    description = models.TextField(blank=True, null=True)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    file = models.FileField(upload_to='notes/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    upload_date = models.DateTimeField(auto_now_add=True)

    def check_and_award_badge(self):
        """Check if this note has reached 1 upvotes and award a badge."""
        upvote_count = self.upvote_set.count()
        if upvote_count >= 0 and not Badge.objects.filter(user=self.uploaded_by, badge_type='upvoter').exists():
            Badge.objects.create(user=self.uploaded_by, badge_type='upvoter')

    def __str__(self):
        return self.subject


class MyNotes(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)  # Use ForeignKey to relate to the Note model
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.note.subject}'  # Access the subject of the related Note


class Upvote(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # note = models.ForeignKey(Note, on_delete=models.CASCADE)

       user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
       note = models.ForeignKey(Note, on_delete=models.CASCADE)

       class Meta:
        unique_together = ('user', 'note') 


        # BADGE_OPTION 
class Badge(models.Model):
    BADGE_TYPE_CHOICES = [
        ('upvoter', 'Upvote Master'),
        # Add more badges if needed
    ]
    user = models.ForeignKey(NestUser, on_delete=models.CASCADE, related_name="badges")
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPE_CHOICES)
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.badge_type}'