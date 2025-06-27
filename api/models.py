from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    profile_image = models.BinaryField(null=True, blank=True)

    class Meta:
        db_table = 'users'
        managed = False  # Assume table already exists; set to True if letting Django manage.

    def __str__(self):
        return self.username


class Club(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    affiliations = models.CharField(max_length=255, null=True, blank=True)
    pres = models.IntegerField(null=True, blank=True)
    vp = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'clubs'
        managed = False

    def __str__(self):
        return self.name


# Add role choices for club membership
class ClubRole(models.TextChoices):
    MEMBER = "member", "Member"
    OFFICER = "officer", "Officer"
    ADMIN = "admin", "Admin"


class UserClubs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_clubs')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='userclubs')
    role = models.CharField(max_length=10, choices=ClubRole.choices, default=ClubRole.MEMBER)

    class Meta:
        db_table = 'user_clubs'
        managed = False
        unique_together = (('user', 'club'),)


class CollegeClubs(models.Model):
    college = models.IntegerField()
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='college_clubs')

    class Meta:
        db_table = 'college_clubs'
        managed = False


# New model to store club events
class Event(models.Model):
    id = models.AutoField(primary_key=True)
    club = models.ForeignKey('Club', on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_events')

    class Meta:
        ordering = ["starts_at"]
        db_table = 'events'
        managed = True

    def __str__(self):
        return f"{self.title} ({self.club.name})" 