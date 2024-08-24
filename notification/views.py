from rest_framework import generics

from .models import NotificationLog, NotificationConfig, Reminder, LetterRequest
from .serializers import NotificationLogSerializer, \
    NotificationConfigSerializer, \
    ReminderSerializer, LetterRequestSerializer


# Create your views here.


# Create your views here.


class NotificationLogList(generics.ListCreateAPIView):
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer

    def get_queryset(self):
        queryset = NotificationLog.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class NotificationLogView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer


class NotificationConfigList(generics.ListCreateAPIView):
    queryset = NotificationConfig.objects.all()
    serializer_class = NotificationConfigSerializer

    def get_queryset(self):
        queryset = NotificationConfig.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class NotificationConfigView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NotificationConfig.objects.all()
    serializer_class = NotificationConfigSerializer


class ReminderList(generics.ListCreateAPIView):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer

    def get_queryset(self):
        queryset = Reminder.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class ReminderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer


class LetterRequestList(generics.ListCreateAPIView):
    queryset = LetterRequest.objects.all()
    serializer_class = LetterRequestSerializer

    def get_queryset(self):
        queryset = LetterRequest.objects.all()
        params = self.request.query_params
        if params and len(params) > 0:
            for param in params:
                if param not in ['page', 'search']:
                    queryset = queryset.filter(**{param: params[param]})
        return queryset


class LetterRequestView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LetterRequest.objects.all()
    serializer_class = LetterRequestSerializer
