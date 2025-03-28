from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from django.core.validators import RegexValidator
from Users.services import *

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'Admin')
        phone_number = validate_phone_number(Profile, input('Phone Number: '))
        user = self.create_user(email, password, **extra_fields)
        create_admin_profile(Profile, user, phone_number)
        return user

class User(AbstractBaseUser):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    institute = models.CharField(max_length=255, null=False, blank=False, default="S.S.V.P's B.S.Deore Polytechnic, Dhule")
    email = models.EmailField(unique=True, null=False, blank=False)
    username = models.CharField(unique=True, max_length=100, null=False, blank=False)
    password = models.CharField(max_length=100, null=False, blank=False)
    role = models.CharField(max_length=10, null=False, blank=False)
    joined_date = models.DateField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']
    objects = UserManager()

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        self.email = self.email.lower()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    class Meta:
        db_table = 'Users'
    
class Subject(models.Model):
    id = models.BigAutoField(primary_key=True)
    subject_code = models.CharField(max_length=100, unique=True, null=False, blank=False)
    subject_name = models.CharField(max_length=255, null=False, blank=False)
    semester = models.CharField(max_length=100, null=False, blank=False)
    department =models.CharField(max_length=100, null=False, blank=False)
    scheme = models.CharField(max_length=10, null=False, blank=False)

    def __str__(self):
        return f'{self.subject_code}({self.scheme}): {self.subject_name}'
    
    class Meta:
        db_table = 'Subjects'
    
class Profile(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, null=False, blank=False ,validators=[RegexValidator(regex=r'^\d{10}$')])
    designation = models.CharField(max_length=100, null=False, blank=False)
    department = models.CharField(max_length=100, null=False, blank=False)
    experience = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    subjects = models.ManyToManyField(Subject, related_name='profiles', blank=True)
    
    def __str__(self):
        return f'{self.user.role}: {self.user}'
 
    class Meta:
        db_table = 'Profiles'