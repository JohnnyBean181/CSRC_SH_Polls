from datetime import date, timedelta
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property

# Create your models here.
class Question(models.Model):
    def __str__(self):
        return self.question_text

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - timedelta(days=1)

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

class Choice(models.Model):
    def __str__(self):
        return self.choice_text

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

class Employees(models.Model):
    emp_no = models.AutoField(primary_key=True)
    birth_date = models.DateField(blank=True, null=True)
    first_name = models.CharField(max_length=14)
    last_name = models.CharField(max_length=16)
    gender = models.CharField(max_length=1)
    hire_date = models.DateField(blank=True, null=True)
    index_2024 = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employees'
        verbose_name = "candidate"

    def __str__(self):
        return f"{self.last_name}{self.first_name}"

class Departments(models.Model):
    dept_no = models.AutoField(primary_key=True)
    dept_name = models.CharField(unique=True, max_length=40, verbose_name="部门名称")
    location = models.CharField(max_length=40, blank=True, null=True, verbose_name="位置")
    created_date = models.DateField(verbose_name="设立日期")
    previous = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'departments'
        verbose_name = "department"

    def __str__(self):
        return self.dept_name


class Titles(models.Model):
    emp_no = models.OneToOneField('Employees', on_delete=models.CASCADE, db_column='emp_no', primary_key=True)  # The composite primary key (emp_no, title, from_date) found, that is not supported. The first column is selected.
    title = models.CharField(max_length=50)
    from_date = models.DateField(default=date(2024, 1, 1))
    to_date = models.DateField(default=date(2024, 12, 31))

    class Meta:
        managed = False
        db_table = 'titles'
        verbose_name = "candidate's title"
        unique_together = (('emp_no', 'title', 'from_date'),)

    def __str__(self):
        #return f"{self.emp_no}-{self.title}"
        return self.title

class DeptManager(models.Model):
    record_id = models.AutoField(primary_key=True)
    dept_no = models.ForeignKey('Departments', on_delete=models.CASCADE, db_column='dept_no')
    emp_no = models.ForeignKey('Employees', on_delete=models.CASCADE, db_column='emp_no')
    from_date = models.DateField(default=date(2024, 1, 1))
    to_date = models.DateField(default=date(2024, 12, 31))

    class Meta:
        managed = False
        db_table = 'dept_manager'
        unique_together = (('dept_no', 'emp_no', 'from_date'),)


class VoterTitles(models.Model):
    title_id = models.AutoField(primary_key=True)
    title_name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'voter_titles'
        verbose_name = "voter's title"

    def __str__(self):
        #return f"{self.emp_no}-{self.title}"
        return self.title_name

class Voters2024(AbstractUser):
    emp_no = models.ForeignKey('Employees', on_delete=models.CASCADE, db_column='emp_no', blank=True, null=True)
    title_id = models.ForeignKey('VoterTitles', on_delete=models.CASCADE, db_column='title_id', blank=True, null=True)
    dept_no = models.ForeignKey('Departments', on_delete=models.CASCADE, db_column='dept_no', blank=True, null=True)
    voted = models.BooleanField(default=False)
    valid_year = models.IntegerField(default=2024)

class Scales(models.Model):
    scale_id = models.AutoField(primary_key=True)
    scale_name = models.CharField(unique=True, max_length=10)
    scale_value = models.IntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'scales'
        verbose_name = "scale"

    def __str__(self):
        return f"{self.scale_name}-{self.scale_value}"

class Votes(models.Model):
    voter = models.ForeignKey('Voters2024', on_delete=models.CASCADE)
    emp_no = models.ForeignKey('Employees', on_delete=models.CASCADE, db_column='emp_no')
    scale = models.ForeignKey('Scales', on_delete=models.CASCADE, db_column='scale_id')
    comment = models.CharField(max_length=50, blank=True, null=True)
    vote_timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'votes'
        verbose_name = "vote"
        constraints = [
            models.UniqueConstraint(fields=['voter', 'emp_no'], name='unique_vote')
        ]

