from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.contrib.auth.models import User
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
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True or extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_staff=True and is_superuser=True.')
        return self.create_user(username, email, password, **extra_fields)

class NestUser(AbstractBaseUser, PermissionsMixin):
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('ME', 'Mechanical Engineering'),
    ]

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    branch = models.CharField(max_length=50, choices=BRANCH_CHOICES)
    date_joined = models.DateTimeField(auto_now_add=True)
    notes = models.ManyToManyField('Note', related_name='added_by_users')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

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
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.note.subject}'


class PickupLocation(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return self.name

class PrintPricing(models.Model):
    black_and_white_price = models.DecimalField(max_digits=5, decimal_places=2, default=0.10)
    color_price = models.DecimalField(max_digits=5, decimal_places=2, default=0.25)
    fast_print_surcharge = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    delivery_surcharge = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0.05)

    def __str__(self):
        return "Current Pricing"

class Order(models.Model):
    COLOR_OPTIONS = [
        ('bw', 'Black & White'),
        ('color', 'Colored'),
    ]
    STATUS_OPTIONS = [
        ('processing', 'Processing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='orders/')
    page_count = models.IntegerField()
    color_option = models.CharField(max_length=50, choices=COLOR_OPTIONS)
    pickup_location = models.ForeignKey(PickupLocation, on_delete=models.SET_NULL, null=True)
    file_type = models.CharField(max_length=50, blank=True , default='none')
    fast_option = models.BooleanField(default=False)
    delivery_option = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_OPTIONS, default='processing')
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_price(self):
        pricing = PrintPricing.objects.last()
        if self.color_option == 'bw':
            price = pricing.black_and_white_price * self.page_count
        elif self.color_option == 'color':
            price = pricing.color_price * self.page_count
        else:
            # Handle mixed pricing separately
            price = pricing.black_and_white_price * (self.page_count // 2) + pricing.color_price * (self.page_count // 2)
        if self.fast_option:
            price += pricing.fast_print_surcharge
        if self.delivery_option:
            price += pricing.delivery_surcharge
        price += price * pricing.tax_rate
        self.price = price
        self.save()

    def __str__(self):
        return f"Order {self.order_id}"
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

#new code
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)  # To allow admins to approve/disapprove comments

    def __str__(self):
        return f"Comment by {self.user} on {self.note.subject}"