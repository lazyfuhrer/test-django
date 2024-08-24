from django.urls import path, include

from .views import AppointmentsReportView, RevenueReportView, BillingReportView, \
    PaymentReportView, PaymentModeReportView, IncomeReportExport, PaymentReportExport, \
        EarningsPerProcedureReportView, AppointmentsPerDoctorReportView, \
          InvoiceIncomePerDoctorReportView, PaymentPerDayReportView

report_urls = [
    path('report/', include([
        path('export/', include([
            path('income/', IncomeReportExport.as_view(), name="income_export"),
            path('payment/', PaymentReportExport.as_view(), name="payment_export")
        ])),
        path('summery/', include([
            path('appointment/', AppointmentsReportView.as_view(),
                 name="appintment_summery"),
            path('revenue/', RevenueReportView.as_view(),
                 name="revenue_summery"),
            path('billing/', BillingReportView.as_view(),
                 name="billing_summery"),
            path('procedure/', EarningsPerProcedureReportView.as_view(),
                 name="procedure"),
            path('appointmentsperdoctor/', AppointmentsPerDoctorReportView.as_view(),
                 name="appointment_per_doctor"),
            path('invoicedincome/', InvoiceIncomePerDoctorReportView.as_view(),
                 name="invoiced_income"),
            path('payment-report/', PaymentPerDayReportView.as_view(), name='payment-report'),
            path('payment/', include([
                path('mode/', PaymentModeReportView.as_view(),
                     name="paymentmode_summery"),
                path('', PaymentReportView.as_view(),
                     name="payment_summery"),
            ]))
        ])),

    ]))
]
