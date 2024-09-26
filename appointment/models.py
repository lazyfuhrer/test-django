from django.db import models

from clinic.models import Clinic
# Create your models here.
from user.models import User


class Tax(models.Model):
    name = models.CharField(null=True, max_length=30)
    percentage = models.FloatField(null=True, blank=True)
    status = models.BooleanField(default=1)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='tax_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='tax_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} {self.percentage}'


class Procedure(models.Model):
    name = models.CharField(max_length=100)
    clinic = models.ForeignKey(Clinic, on_delete=models.DO_NOTHING, blank=True,
                               null=True)
    description = models.TextField(null=True, blank=True)
    cost = models.FloatField(null=True, blank=True)
    # tax = models.ForeignKey(Tax, on_delete=models.DO_NOTHING)
    tax = models.ManyToManyField(Tax,
                                 related_name='taxs',
                                 blank=True)
    status = models.BooleanField(default=1)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='procedure_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='procedure_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} - {} - {}".format(self.name, self.cost, self.clinic)


class Category(models.Model):
    name = models.CharField(max_length=100)
    clinic = models.ForeignKey(Clinic, on_delete=models.DO_NOTHING, blank=True,
                               null=True)

    status = models.BooleanField(default=1)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='category_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='category_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} - {}".format(self.name, self.clinic)


class Appointment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('partial_paid', 'Partial Paid'),
        ('collected', 'Collected')
    )
    APPOINTMENT_STAUTS = (
        ('booked', 'Booked'),
        ('checked_in', 'Checked In'),  # visited to clinic
        ('engaged', 'Engaged'),  # met doctor
        ('checked_out', 'Checked Out'),  # checkout out from hospital
        ('cancelled', 'Cancelled'),
        ('not_visited', 'Not Visited')
    )
    is_new = models.BooleanField(null=True, blank=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.DO_NOTHING)
    doctor = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                               related_name='appointment_doctor')
    patient = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                                related_name='appointment_patient')
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING,
                                 blank=True, null=True)
    scheduled_from = models.DateTimeField(null=True, blank=True)
    scheduled_to = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    procedure = models.ForeignKey(Procedure, on_delete=models.DO_NOTHING,
                                  blank=True, null=True)
    # today_schedule = models.TextField(null=True, blank=True)
    # previous_appointments = models.TextField(null=True, blank=True)
    payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=20,
                                      default='pending')
    checked_in = models.DateTimeField(null=True, blank=True)
    engaged_at = models.DateTimeField(null=True, blank=True)
    checked_out = models.DateTimeField(null=True, blank=True)
    appointment_status = models.CharField(choices=APPOINTMENT_STAUTS,
                                          max_length=20,
                                          default='booked')
    status = models.BooleanField(default=1)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name='appointment_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name='appointment_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "#{} {} {}".format(self.id, self.patient, self.scheduled_from)


CLINICAL_NOTE_TYPE = (
    ('complaints', "Chief Complaint"),
    ('subjective', "Subjective"),
    ('objective', "Objective"),
    ('assessment', "Assessment"),
    ('plan', "Plan"),
    ('procedure', "Procedure"),
    ('exercises', "Exercises"),
)


# SOAP_TYPE = (
#     ('subjective', 'Subjective'),
#     ('objective', 'Objective'),
#     ('assessment', 'Assessment'),
#     ('procedure', 'Procedure'),
# )


class NoteCategory(models.Model):
    name = models.TextField()
    status = models.BooleanField(default=1)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name='notecategory_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name='notecategory_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.name)


class PatientDirectory(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    notes = models.TextField(null=True, blank=True)
    category = models.ForeignKey(NoteCategory, on_delete=models.SET_NULL,
                                 null=True)
    # soap_type = models.CharField(choices=SOAP_TYPE, max_length=20, null=True,
    #                              blank=True)
    clinical_note_type = models.CharField(choices=CLINICAL_NOTE_TYPE,
                                          max_length=30)
    status = models.BooleanField(default=1)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name='patientdirectory_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name='patientdirectory_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.clinical_note_type)


class Files(models.Model):
    patient_directory = models.ForeignKey(PatientDirectory,
                                          on_delete=models.CASCADE)
    file_url = models.TextField(null=True, blank=True)
    file_name = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=1)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='files_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='files_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name


class Exercise(models.Model):
    title = models.CharField(max_length=100)
    video_clips = models.FileField(null=True, blank=True)
    video_link = models.URLField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=1)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='exercise_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='exercise_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PatientDirectoryExercises(models.Model):
    patient_directory = models.ForeignKey(PatientDirectory,
                                          on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    status = models.BooleanField(default=1)
    created_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name='patientdirectoryexercises_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name='patientdirectoryexercises_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient_directory} - {self.exercise}"
