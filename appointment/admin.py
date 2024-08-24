from django.contrib import admin

from .models import Appointment, Procedure, Tax, Category, PatientDirectory, \
    Files, Exercise, PatientDirectoryExercises, NoteCategory


# Register your models here.

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'scheduled_from', 'doctor', 'clinic', 'patient',
                    'scheduled_to', 'appointment_status', 'payment_status',)
    search_fields = (
        'scheduled_from', 'scheduled_to', 'doctor__first_name',
        'doctor__last_name', 'id', 'category__name',
        'patient__first_name', 'patient__last_name', 'patient__atlas_id', 'procedure__name',
    )
    autocomplete_fields = ('doctor', 'patient', 'procedure', 'created_by', 'updated_by')
    list_filter = (
        'clinic',
        'category',
        'scheduled_from',
        'scheduled_to',
        'payment_status',
        'appointment_status'
    )


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'clinic', 'cost')
    search_fields = ('name', 'description')
    list_filter = ('clinic', 'tax')
    autocomplete_fields = ('created_by', 'updated_by')


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'percentage')
    search_fields = ('name',)
    autocomplete_fields = ('created_by', 'updated_by')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', 'description')
    list_filter = ('clinic',)
    autocomplete_fields = ('created_by', 'updated_by')


@admin.register(NoteCategory)
class NoteCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    autocomplete_fields = ('created_by', 'updated_by')
    # list_filter = ('clinic',)


@admin.register(PatientDirectory)
class PatientDirectoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'clinical_note_type')
    search_fields = ('notes', 'clinical_note_type')
    list_filter = ('clinical_note_type', 'category', 'appointment__clinic')
    autocomplete_fields = ('created_by', 'updated_by', 'appointment')


@admin.register(Files)
class FilesAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_name')
    search_fields = ('file_name', 'file_url')
    list_filter = ('patient_directory__appointment__clinic',)
    autocomplete_fields = ('created_by', 'updated_by', 'patient_directory')


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title', 'video_link')
    autocomplete_fields = ('created_by', 'updated_by')


@admin.register(PatientDirectoryExercises)
class PatientDirectoryExercisesAdmin(admin.ModelAdmin):
    list_display = ('id', 'exercise')
    search_fields = ('exercise', 'patient_directory')
    list_filter = ('patient_directory', 'exercise')
    autocomplete_fields = (
        'created_by', 'updated_by', 'patient_directory', 'exercise')
