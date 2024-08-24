import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from base.utils import generate_pdf_file, custom_strftime
from clinic.models import Clinic
from payment.models import Payment, Invoice
from payment.serializers import PaymentSerializer, InvoiceSerializer
from report.utils import AppointmentReport


# Create your views here.


class AppointmentsReportView(APIView):
    def get(self, request):
        query = request.query_params
        from_date = query.get('from_date', None)
        to_date = query.get('to_date', None)
        clinic_id = query.get('clinic_id', query.get('clinic'))
        app = AppointmentReport(from_date=from_date, to_date=to_date,
                                clinic_id=clinic_id)
        summery = app.appointment_summary()
        return Response(summery, status=status.HTTP_200_OK)


class RevenueReportView(APIView):
    def get(self, request):
        query = request.query_params
        from_date = query.get('from_date', None)
        to_date = query.get('to_date', None)
        clinic_id = query.get('clinic_id', query.get('clinic'))
        app = AppointmentReport(from_date=from_date, to_date=to_date,
                                clinic_id=clinic_id)
        summery = app.revenue_summary()
        return Response(summery, status=status.HTTP_200_OK)


class BillingReportView(APIView):
    def get(self, request):
        query = request.query_params
        from_date = query.get('from_date', None)
        to_date = query.get('to_date', None)
        clinic_id = query.get('clinic_id', query.get('clinic'))
        app = AppointmentReport(from_date=from_date, to_date=to_date,
                                clinic_id=clinic_id)
        summery = app.billing_summary()
        return Response(summery, status=status.HTTP_200_OK)


class PaymentReportView(APIView):
    def get(self, request):
        query = request.query_params
        from_date = query.get('from_date', None)
        to_date = query.get('to_date', None)
        clinic_id = query.get('clinic_id', query.get('clinic'))
        app = AppointmentReport(from_date=from_date, to_date=to_date,
                                clinic_id=clinic_id)
        summery = app.payment_summary()
        return Response(summery, status=status.HTTP_200_OK)


class PaymentModeReportView(APIView):
    def get(self, request):
        query = request.query_params
        from_date = query.get('from_date')
        to_date = query.get('to_date')
        clinic_id = query.get('clinic_id', query.get('clinic'))

        if not from_date or not to_date or not clinic_id:
            return Response({'error': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            app = AppointmentReport(from_date=from_date, to_date=to_date, clinic_id=clinic_id)
            summery = app.payment_mode_summary()
            return Response({"results": summery}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EarningsPerProcedureReportView(APIView):
    def get(self, request):
        query = request.query_params
        from_date = query.get('from_date', None)
        to_date = query.get('to_date', None)
        clinic_id = query.get('clinic_id', query.get('clinic'))
        app = AppointmentReport(from_date=from_date, to_date=to_date,
                                clinic_id=clinic_id)
        summery = app.earnings_per_procedure()
        return Response(summery, status=status.HTTP_200_OK)


class AppointmentsPerDoctorReportView(APIView):
    def get(self, request):
        query = request.query_params
        from_date = query.get('from_date', None)
        to_date = query.get('to_date', None)
        clinic_id = query.get('clinic_id', query.get('clinic'))
        app = AppointmentReport(from_date=from_date, to_date=to_date,
                                clinic_id=clinic_id)
        summery = app.appointments_per_doctor()
        return Response({"results": summery}, status=status.HTTP_200_OK)


class InvoiceIncomePerDoctorReportView(APIView):
    def get(self, request):
        query = request.query_params
        from_date = query.get('from_date', None)
        to_date = query.get('to_date', None)
        clinic_id = query.get('clinic_id', query.get('clinic'))
        app = AppointmentReport(from_date=from_date, to_date=to_date,
                                clinic_id=clinic_id)
        summery = app.invoiced_income_per_doctor()
        return Response({"results": summery}, status=status.HTTP_200_OK)


class ReportBaseView(APIView):
    type_name = None
    csv_column_names = None
    template = None
    prefix_valus = {
        'payment_report_id': "RCPT",
        'payment_report_invoice_number': "INV",
        'income_report_invoice_number': "INV"
    }
    sufix_valus = {

    }

    def prefix_sufix(self, key, val):
        if not key or not val:
            return val
        key_name = self.type_name + '_' + key
        if key_name in self.prefix_valus.keys():
            val = self.prefix_valus[key_name] + str(val)
        if key_name in self.sufix_valus.keys():
            val = str(val) + self.sufix_valus[key_name]
        return val

    def export_csv(self, data):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.type_name}.csv"'

        writer = csv.writer(response)
        writer.writerow(self.csv_column_names.values())
        head_keys = self.csv_column_names.keys()
        for row in data:
            new_row = {k: v for k, v in row.items() if k in head_keys}
            writer.writerow([self.prefix_sufix(column, new_row[column]) if column in new_row else '-' for column in
                             head_keys])

        return response

    def export_pdf(self, data):
        pdf_file = generate_pdf_file(f'pdf/{self.template}', data)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{self.type_name}.pdf"'

        return response


class IncomeReportExport(ReportBaseView):
    csv_column_names = {
        "invoice_number": "Invoice", "date": "Date", "clinic_name": "Clinic", "patient_name": "Patient",
        "patient_atlas_id": "Patient ID", "procedure_names": "Procedures", "cost": "Cost", "discount": "Discount",
        "tax": "Tax", "grand_total": "Invoice Amount", "paid_amount": "Paid Amount"
    }
    type_name = "income_report"
    template = "income.html"

    def get(self, request):
        query = request.query_params
        user = request.user
        from_date = query.get('from_date', None)
        to_date = query.get('to_date', None)
        clinic_id = query.get('clinic_id', query.get('clinic'))
        export_format = query.get('filetype', 'csv')
        if export_format not in ['csv', 'pdf']:
            return Response({'error': 'Invalid export format'}, status=status.HTTP_400_BAD_REQUEST)
        if not from_date or not to_date:
            return Response({'error': 'Invalid date range'}, status=status.HTTP_400_BAD_REQUEST)
        if not clinic_id:
            return Response({'error': 'Invalid clinic ID'}, status=status.HTTP_400_BAD_REQUEST)
        clinic = get_object_or_404(Clinic, id=clinic_id)
        clinic_location = clinic.name
        today = custom_strftime('%Y-%m-%d')
        app = AppointmentReport(from_date=from_date, to_date=to_date,
                                clinic_id=clinic_id)
        summery = app.income_summary()
        income = Invoice.objects.filter(clinic=clinic_id, date__range=(app.fdate, app.tdate))

        details = InvoiceSerializer(income, many=True).data
        data = {"user": user, "summery": summery, "details": details, "clinic_location": clinic_location,
                "from_date": app.fdate, "to_date": app.tdate, "today": today}

        if export_format == 'csv':
            return self.export_csv(details)
        elif export_format == 'pdf':
            return self.export_pdf(data)


class PaymentReportExport(ReportBaseView):
    csv_column_names = {
        "receipt_id": "Receipt ID", "collected_on": "Date", "clinic_name": "Clinic", "patient_name": "Patient",
        "patient_atlas_id": "Patient ID", "invoice_number": "Invoice", 'invoice_date': "Invoice Date",
        "procedure_names": "Procedures", "price": "Amount Paid (INR)", "type": "Payment Type", "mode": "Payment Mode",
        "transaction_id": "Transaction ID", "payment_status": "Status", "advance": "Advance"
    }
    balance_keys = ["receipt_id", "collected_on", "clinic_name", "patient_name", "patient_atlas_id",
                    "procedure_names", "price", "balance", "type", "mode", "transaction_id", "payment_status"]
    type_name = "payment_report"
    template = "payment.html"

    def balance_fix(self, row):
        row['advance'] = "Yes"
        row['price'] = row['balance']
        return row

    def details_fix(self, row):
        row.pop('balance')
        return row

    def get(self, request):
        query = request.query_params
        user = request.user
        from_date = query.get('from_date', None)
        to_date = query.get('to_date', None)
        clinic_id = query.get('clinic_id', query.get('clinic'))
        export_format = query.get('filetype', 'csv')
        if export_format not in ['csv', 'pdf']:
            return Response({'error': 'Invalid export format'}, status=status.HTTP_400_BAD_REQUEST)
        if not from_date or not to_date:
            return Response({'error': 'Invalid date range'}, status=status.HTTP_400_BAD_REQUEST)
        if not clinic_id:
            return Response({'error': 'Invalid clinic ID'}, status=status.HTTP_400_BAD_REQUEST)
        clinic = get_object_or_404(Clinic, id=clinic_id)
        clinic_location = clinic.name
        today = custom_strftime('%Y-%m-%d')
        app = AppointmentReport(from_date=from_date, to_date=to_date,
                                clinic_id=clinic_id)
        summery = app.payment_summary()
        payments = Payment.objects.filter(clinic=clinic_id, collected_on__range=(app.fdate, app.tdate),
                                          transaction_type='collected')
        receipt_records = Payment.objects.filter(receipt_id__in=payments.values_list('receipt_id', flat=True))
        balance_records = payments.filter(balance__gt=0)
        details = PaymentSerializer(receipt_records, many=True).data
        balance_data = PaymentSerializer(balance_records, many=True).data
        balance_rows = [
            {k: x[k] if k in self.balance_keys else '' for k in list(self.csv_column_names.keys()) + ['balance']}
            for x in balance_data]
        balance_rows = [self.balance_fix(x) for x in balance_rows]
        details.extend(balance_rows)
        details = [self.details_fix(x) for x in details]
        data = {"user": user, "summery": summery, "details": details, "clinic_location": clinic_location,
                "from_date": app.fdate, "to_date": app.tdate, "today": today}

        # return Response(summery, status=status.HTTP_200_OK)

        if export_format == 'csv':
            response = self.export_csv(details)
            return response
        elif export_format == 'pdf':
            response = self.export_pdf(data)
            return response


class PaymentPerDayReportView(APIView):
    def get(self, request):
        query = request.query_params
        from_date = query.get('from_date', None)
        to_date = query.get('to_date', None)
        clinic_id = query.get('clinic_id', query.get('clinic'))
        app = AppointmentReport(from_date=from_date, to_date=to_date,
                                clinic_id=clinic_id)
        summery = app.payments_per_day()
        return Response({"results": summery}, status=status.HTTP_200_OK)
