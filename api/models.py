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

    class Meta:
        db_table = 'clubs'
        managed = False

    def __str__(self):
        return self.name


class UserClubs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_clubs')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='userclubs')

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