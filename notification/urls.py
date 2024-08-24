from django.urls import path

from .views import NotificationLogList, NotificationLogView, \
    NotificationConfigList, \
    NotificationConfigView, ReminderList, ReminderView, LetterRequestList, \
    LetterRequestView

notification_urls = [
    path('notificationlog/', NotificationLogList.as_view(),
         name='notificationlogList'),
    path('notificationlog/<int:pk>', NotificationLogView.as_view(),
         name='notificationlogView'),
    path('notificationconfig/', NotificationConfigList.as_view(),
         name='notificationconfigList'),
    path('notificationconfig/<int:pk>', NotificationConfigView.as_view(),
         name='notificationconfigView'),
    path('reminder/', ReminderList.as_view(), name='reminderList'),
    path('reminder/<int:pk>', ReminderView.as_view(), name='reminderView'),
    path('letterrequest/', LetterRequestList.as_view(),
         name='letterrequestList'),
    path('letterrequest/<int:pk>', LetterRequestView.as_view(),
         name='letterrequestView'),
]
