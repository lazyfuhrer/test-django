# Create your views here.
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.db.models import Count
from django.utils import timezone
from rest_framework import generics, status, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from base.utils import send_appointment_followup_email, \
    appointment_booked_notification
from user.serializers import UserSerializer
from .models import Appointment, Procedure, Tax, Category, PatientDirectory, \
    Files, Exercise, PatientDirectoryExercises, NoteCategory
from .serializers import AppointmentSerializer, ProcedureSerializer, \
    TaxSerializer, NoteCategorySerializer, CategorySerializer, PatientDirectorySerializer, \
    FilesSerializer, ExerciseSerializer, \
    PatientDirectoryExercisesSerializer

# Create your views here.
User = get_user_model()


class AppointmentList(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)
        # place send email logic here on schedule followup
        if self.request.query_params.get('schedule') == 'true':
            send_appointment_followup_email({"appointment": serializer.data})

    def get_queryset(self):
        queryset = Appointment.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class AppointmentAll(generics.ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Appointment.objects.all().order_by('-scheduled_from')
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class AppointmentView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def perform_update(self, serializer):
        # Set updated_by field
        serializer.save(updated_by=self.request.user)


class ProcedureList(generics.ListCreateAPIView):
    queryset = Procedure.objects.all()
    model = Procedure
    serializer_class = ProcedureSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def get_queryset(self):
        queryset = Procedure.objects.all().order_by('-created_at')
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search', 'page_size']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class ProcedureView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Procedure.objects.all()
    serializer_class = ProcedureSerializer

    def perform_update(self, serializer):
        # Set updated_by field
        serializer.save(updated_by=self.request.user)


class TaxList(generics.ListCreateAPIView):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def get_queryset(self):
        queryset = Tax.objects.all().order_by('-created_at')
        params = self.request.query_params
        if len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class TaxView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer

    def perform_update(self, serializer):
        # Set updated_by field
        serializer.save(updated_by=self.request.user)


class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def get_queryset(self):
        queryset = Category.objects.all().order_by('-created_at')
        params = self.request.query_params
        if len(params) > 0:
            for param in params:
                if param not in ['page', 'search', 'page_size']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class CategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def perform_update(self, serializer):
        # Set updated_by field
        serializer.save(updated_by=self.request.user)


class NoteCategoryList(generics.ListCreateAPIView):
    queryset = NoteCategory.objects.all()
    serializer_class = NoteCategorySerializer
    search_fields = ['name']

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def get_queryset(self):
        queryset = NoteCategory.objects.all().order_by('-created_at')
        params = self.request.query_params
        if len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class NoteCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NoteCategory.objects.all()
    serializer_class = NoteCategorySerializer

    def perform_update(self, serializer):
        # Set updated_by field
        serializer.save(updated_by=self.request.user)


class PatientDirectoryList(generics.ListCreateAPIView):
    queryset = PatientDirectory.objects.all()
    serializer_class = PatientDirectorySerializer

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def get_queryset(self):
        queryset = PatientDirectory.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class PatientDirectoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PatientDirectory.objects.all()
    serializer_class = PatientDirectorySerializer

    def perform_update(self, serializer):
        # Set updated_by field
        serializer.save(updated_by=self.request.user)


class FilesList(generics.ListCreateAPIView):
    queryset = Files.objects.all()
    serializer_class = FilesSerializer

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def get_queryset(self):
        queryset = Files.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class FilesView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Files.objects.all()
    serializer_class = FilesSerializer

    def perform_update(self, serializer):
        # Set updated_by field
        serializer.save(updated_by=self.request.user)


class ExerciseList(generics.ListCreateAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def get_queryset(self):
        queryset = Exercise.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class ExerciseView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    def perform_update(self, serializer):
        # Set updated_by field
        serializer.save(updated_by=self.request.user)


class PatientDirectoryExercisesList(generics.ListCreateAPIView):
    queryset = PatientDirectoryExercises.objects.all()
    serializer_class = PatientDirectoryExercisesSerializer

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def get_queryset(self):
        queryset = PatientDirectoryExercises.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class PatientDirectoryExercisesView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PatientDirectoryExercises.objects.all()
    serializer_class = PatientDirectoryExercisesSerializer

    def perform_update(self, serializer):
        # Set updated_by field
        serializer.save(updated_by=self.request.user)


# this view allows create or update note form frontend
class CreateNotesView(APIView):
    def post(self, request):
        data = request.data
        clinical_note_type = data.get('clinical_note_type')
        exercise = data.get('exercise')
        appointment = data.get('appointment')
        category = data.get('category')
        notes = data.get('notes')
        note_id = data.get('id', '')
        session = {'created_by': self.request.user.id, 'updated_by': self.request.user.id}
        note = {
            'appointment': appointment,
            'category': category,
            'notes': notes,
            'clinical_note_type': clinical_note_type,
        }
        note.update(session)

        if note_id:
            success_status = status.HTTP_200_OK
            instance = PatientDirectory.objects.filter(id=note_id).first()
        else:
            success_status = status.HTTP_201_CREATED
            instance = None

        serializer = PatientDirectorySerializer(data=note, instance=instance, partial=True)

        if serializer.is_valid():
            pd = serializer.save()
            note_id = pd.id  # Ensure we have the saved instance ID for file associations
            files = request.FILES.getlist('file')  # Get the list of uploaded files
            if files:
                path = f'/files/appointment_{appointment}/note_{note_id}'
                upload_location = f'{settings.UPLOADS_ROOT}{path}'
                fs = FileSystemStorage(location=upload_location)
                for file in files:
                    # Create a new instance of the FilesSerializer
                    file_data = {
                        'patient_directory': note_id,
                        'file_name': file.name,
                        'created_by': request.user.id,
                        'updated_by': request.user.id,
                    }
                    file_serializer = FilesSerializer(data=file_data, context={'request': request})
                    if file_serializer.is_valid(raise_exception=True):
                        filename = fs.save(file.name, file)
                        file_url = fs.url(filename)
                        # Update file_url in serializer data
                        file_serializer.save(file_url=path + file_url)

            if clinical_note_type == 'exercise':
                ex_data = {'patient_directory': pd, 'exercise': exercise}
                ex_data.update(session)
                pde_serializer = PatientDirectoryExercisesSerializer(data=ex_data)
                if pde_serializer.is_valid():
                    pde_serializer.save()
                else:
                    return Response(pde_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=success_status)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateAppointment(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        photo = request.FILES.get('photo')
        data = request.POST.get('data')
        data_object = json.loads(data)
        patient = data_object.pop('patient')
        email = patient.get('email')
        phone_number = patient.get('phone_number')
        first_name = patient.get('first_name')
        try:
            user = User.objects.filter(email=email, phone_number=phone_number,
                                       first_name=first_name).first()
            if not user:
                raise ObjectDoesNotExist
            data_object.update({'patient': user.id, 'is_new': False})
        except ObjectDoesNotExist:
            patient.update({'photo': photo})
            user_serializer = UserSerializer(data=patient)
            if user_serializer.is_valid():
                user_data = user_serializer.save()
                user = User.objects.get(pk=user_data.id)
                group = Group.objects.get(pk=settings.PATIENT_GROUP_ID)
                user.groups.add(group)
                user.atlas_id = f"{settings.PREFIX_ATLAS_ID}{user.id}"
                group.user_set.add(user)
                user.save()
                data_object.update({'patient': user_serializer.data['id'],
                                    'is_new': True})
            else:
                return Response(user_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

        # if user:
        #     data.update({'patient': user.__dict__})
        # else:
        data_object.update({'created_by': self.request.user.id,
                            'updated_by': self.request.user.id})
        serializer = AppointmentSerializer(data=data_object,
                                           context={'request': request})

        if serializer.is_valid():
            serializer.save()
            appointment_booked_notification({"appointment": data_object})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    # serializer_class = CreateAppointmentSerializer
    # queryset = Appointment.objects.all()
    #
    # def perform_create(self, serializer):
    #     # Set created_by and updated_by fields
    #     serializer.save(created_by=self.request.user,
    #                     updated_by=self.request.user)


class UpComingsListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        # Get the current date and time
        now = timezone.now()
        queryset = Appointment.objects.filter(
            scheduled_from__gte=now.date()).order_by('scheduled_from')
        # Get the query parameters
        clinic = self.request.query_params.get('clinic')
        date = self.request.query_params.get('scheduled_from')

        if clinic:
            queryset = queryset.filter(clinic=clinic)
        if date:
            queryset = queryset.filter(scheduled_from__gte=date)

        return queryset


class DoctorsAppointmentsListView(APIView):
    def get(self, request):
        scheduled_from = request.query_params.get('scheduled_from')
        scheduled_to = request.query_params.get('scheduled_to')
        clinic = request.query_params.get('clinic')

        # Filter appointments based on the specified fields
        queryset = Appointment.objects.all()
        if scheduled_from:
            queryset = queryset.filter(scheduled_from__gte=scheduled_from)
        if scheduled_to:
            queryset = queryset.filter(scheduled_to__lte=scheduled_to)
        if clinic:
            queryset = queryset.filter(clinic_id=clinic)

        # Filter appointments based on the query parameters
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search', 'scheduled_from', 'scheduled_to', 'clinic']:
                    queryset = queryset.filter(**{param: params[param]})
        # Count the filtered appointments
        appointments_count = queryset.count()
        # Get count of individual doctors' appointments with their names
        queryset = queryset.values('doctor').annotate(count=Count('doctor'))

        # Prepare data for response

        doctors_data = []
        for doctor_count in queryset:
            doctor_id = doctor_count['doctor']
            doctor = User.objects.get(id=doctor_id)
            doctor_first_name = doctor.first_name
            doctor_last_name = doctor.last_name
            full_name = doctor_first_name + " " + doctor_last_name
            doctor_color = doctor.doctor_calender_color
            doctors_data.append({
                'doctor_id': doctor_id,
                'full_name': full_name,
                'doctor_color': doctor_color,
                'count': doctor_count['count']
            })

        return Response({
            'all': appointments_count,
            'doctors_appointments_count': doctors_data
        })
