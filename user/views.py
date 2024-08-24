# Create your views here.
import logging
import traceback

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q
from django.db.models.functions import Lower
from knox.models import AuthToken
from rest_framework import permissions, generics, filters, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from clinic.serializers import ClinicPeopleSerializer
from fuelapp.pagination import CustomPagination
from .models import User, Address, DoctorTiming, Leaves
from .serializers import LoginUserSerializer, AddressSerializer, \
    ForgetPasswordSerializer, CreateUserSerializer, UserSerializer, \
    DoctorTimingSerializer, LeaveSerializer, DoctorSerializer, \
    StaffSerializer
from .utils import send_verify_code, gen_rand_code

logger = logging.getLogger('fuelapp')


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user,
                                   context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        user.auth_token_set.all().delete()
        return Response({
            "user": UserSerializer(user,
                                   context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class ForgetPasswordAPI(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ForgetPasswordSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        user.auth_token_set.all().delete()
        return Response({
            "Your password has changed"
        })


class ResendCode(APIView):
    def post(self, request, format=None):
        try:
            email = request.data.get('email', '')
            user = User.objects.get(email=email, email_verified=False)
            user.email_code = gen_rand_code()
            user.save()
            send_verify_code(user)
            response = {'status': 'success',
                        'message': 'Email verification code resent',
                        'code': status.HTTP_200_OK}
            return Response(response)
        except ObjectDoesNotExist:
            logger(traceback.format_exc())
            return Response({'status': 'error',
                             'message': 'user not found / already verified'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger(traceback.format_exc())
            return Response({'status': 'error'},
                            status=status.HTTP_400_BAD_REQUEST)


class Verify(APIView):
    def post(self, request, format=None):
        try:
            data = request.data
            email = data.get('email', '')
            code = data.get('code', '')
            # logger(data)
            user = User.objects.get(
                email=email, email_code=code, email_verified=0)
            if user:
                # user.email_code = ""
                user.email_verified = 1
                user.save()
                response = {'status': 'success',
                            'message': 'Email verified',
                            'code': status.HTTP_200_OK}
                return Response(response)
        except ObjectDoesNotExist:
            logger(traceback.format_exc())
            return Response({'status': 'error',
                             'message': 'user not found / already verified'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger(traceback.format_exc())
            return Response({'status': 'error'},
                            status=status.HTTP_400_BAD_REQUEST)


class TestEmail(APIView):
    def get(self, request, format=None):
        try:
            message = "Hello World"
            is_success = send_mail(
                # title:
                subject="Password Reset for {title}".format(
                    title="Atlas Chiropractic & Wellness"),
                # message:
                message=message,
                # from:
                from_email=settings.DEFAULT_FROM_EMAIL,
                # to:
                # ,'abdul.nazurudeen@gmail.com'
                recipient_list=['2minstudio.dev@gmail.com']

            )
        except Exception as ex:
            logger(f'{ex}')
            logger(traceback.format_exc())
        response = {'status': 'okay'}
        return Response(response)


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by(Lower('first_name'))
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', '^email', '^phone_number', 'atlas_id']
    ordering_fields = ['first_name']

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        # serializer.save(created_by=self.request.user,
        #               updated_by=self.request.user)
        serializer.save()

    def get_queryset(self):
        queryset = User.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})

        search_query = params.get('search','')
        search_query_values = search_query.split(" ")
        if search_query_values:
            for search_query_value in search_query_values:
                queryset = queryset.filter(
                    Q(first_name__icontains=search_query_value) |
                    Q(last_name__icontains=search_query_value) |
                    Q(email__icontains=search_query_value) |
                    Q(phone_number__icontains=search_query_value) |
                    Q(atlas_id__icontains=search_query_value)
                )
        # if search_query:
        #     queryset = queryset.filter(
        #         Q(first_name__icontains=search_query) |
        #         Q(last_name__icontains=search_query) |
        #         Q(email__icontains=search_query) |
        #         Q(phone_number__icontains=search_query) |
        #         Q(atlas_id__icontains=search_query)
        #     )
        return queryset.order_by(Lower('first_name'))


class UserView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_update(self, serializer):
        # Set updated_by field
        instance = serializer.save(updated_by=self.request.user)
        photo_file = self.request.data.get('photo')
        if photo_file:
            instance.photo = photo_file
            instance.save()


class AddressList(generics.ListCreateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def get_queryset(self):
        queryset = Address.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class AddressView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def perform_update(self, serializer):
        # Set updated_by field
        serializer.save(updated_by=self.request.user)


class DoctorTimingList(generics.ListCreateAPIView):
    queryset = DoctorTiming.objects.all()
    serializer_class = DoctorTimingSerializer

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def get_queryset(self):
        queryset = DoctorTiming.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class DoctorTimingView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DoctorTiming.objects.all()
    serializer_class = DoctorTimingSerializer

    def perform_update(self, serializer):
        # Set updated_by field
        serializer.save(updated_by=self.request.user)


class LeavesList(generics.ListCreateAPIView):
    queryset = Leaves.objects.all()
    serializer_class = LeaveSerializer

    def perform_create(self, serializer):
        # Set created_by and updated_by fields
        serializer.save(created_by=self.request.user,
                        updated_by=self.request.user)

    def get_queryset(self):
        queryset = Leaves.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class LeavesView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Leaves.objects.all()
    serializer_class = LeaveSerializer


class DoctorList(generics.ListCreateAPIView):
    group_id = 2
    queryset = User.objects.filter(groups=group_id)
    pagination_class = CustomPagination
    serializer_class = DoctorSerializer

    # parser_classes = (MultiPartParser, FormParser)
    def get_queryset(self):
        queryset = self.queryset
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param == 'clinic':
                    queryset = queryset.filter(
                        clinicpeople__clinic__in=[params[param]])
                elif param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})

        return queryset

    def create(self, request, *args, **kwargs):
        # doctor_serializer = DoctorSerializer(data=request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.save()
        try:
            doctor.groups.add(self.group_id)
            clinic_id = request.data.get('clinic')
            clinic_people_data = {"user": doctor.id, "clinic": clinic_id,
                                  "created_by": request.user.id,
                                  "updated_by": request.user.id}

            clinic_people_serializer = ClinicPeopleSerializer(
                data=clinic_people_data)
            clinic_people_serializer.is_valid(raise_exception=True)
            clinic_people_serializer.save()

        except Exception as e:
            print(e)
            return Response(
                {'error': 'An error occurred during user creation.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DoctorView(generics.RetrieveUpdateDestroyAPIView):
    group_id = 2
    queryset = User.objects.filter(groups=group_id)
    serializer_class = DoctorSerializer
    parser_classes = (MultiPartParser, FormParser)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)

        # Check if 'file_field' exists in the request data
        if 'signature' in request.data:
            # A file is provided in the request, update it
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        else:
            # No file provided in the request, don't update the file field
            serializer.is_valid(raise_exception=True)
            serializer.save(signature=instance.signature)
            return Response(serializer.data)

    # def perform_update(self, serializer):
    #     # Set updated_by field
    #     instance = serializer.save(updated_by=self.request.user)
    #     signature_file = self.request.data.get('signature')
    #     if signature_file:
    #         instance.signature = signature_file
    #         instance.save()


class StaffList(generics.ListCreateAPIView):
    group_id = 3
    queryset = User.objects.filter(groups=group_id)
    pagination_class = CustomPagination
    serializer_class = StaffSerializer

    def create(self, request, *args, **kwargs):
        # doctor_serializer = DoctorSerializer(data=request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
        try:
            staff.groups.add(self.group_id)
            clinic_id = request.data.get('clinic')
            clinic_people_data = {"user": staff.id, "clinic": clinic_id,
                                  "created_by": request.user.id,
                                  "updated_by": request.user.id}

            clinic_people_serializer = ClinicPeopleSerializer(
                data=clinic_people_data)
            clinic_people_serializer.is_valid(raise_exception=True)
            clinic_people_serializer.save()

        except Exception as e:
            return Response(
                {'error': 'An error occurred during user creation.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StaffView(generics.RetrieveUpdateDestroyAPIView):
    group_id = 3
    queryset = User.objects.filter(groups=group_id)
    serializer_class = StaffSerializer
