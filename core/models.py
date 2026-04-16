from django.db import models
from django.contrib.auth.models import User


# 🔥 Lecturer Model
class Lecturer(models.Model):
    ROLE_CHOICES = [
        ('HOD', 'HOD'),
        ('FULL', 'Full-Time'),
        ('PART', 'Part-Time'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    max_duties = models.IntegerField(default=5)
    assigned_duties = models.IntegerField(default=0)

    def __str__(self):
        return self.name


# Exam Model
class Exam(models.Model):
    SESSION_CHOICES = [
        ('1', 'Forenoon'),   # ✅ changed
        ('2', 'Afternoon'),  # ✅ changed
    ]

    date = models.DateField()
    session = models.CharField(max_length=1, choices=SESSION_CHOICES)

    def __str__(self):
        session_display = dict(self.SESSION_CHOICES).get(self.session)
        return f"{self.date} - {session_display}"

    class Meta:
        ordering = ['date', 'session']  

# Room Model (GLOBAL ROOMS)
class Room(models.Model):
    room_number = models.CharField(max_length=10)

    def __str__(self):
        return self.room_number

    class Meta:
        ordering = ['room_number']   # ✅ sorted display


# 🔥 Allocation Model (CORE LOGIC)
class Allocation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)

    class Meta:
        pass

    def __str__(self):
        return f"{self.room} - {self.exam} - {self.lecturer}"


# 🔥 Absence Model
class Absence(models.Model):
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.lecturer.name} - {self.date}"