import logging
from copy import deepcopy

from django.contrib.auth import get_user_model
from django.db.models import Sum, Q, F

from appointment.models import Appointment
from .models import Payment, Invoice, Wallet
from .serializers import WalletSerializer, WalletPaymentSerializer, PaymentSerializer

logger = logging.getLogger('fuelapp')


def get_user_payments(user_id, exclude_invoice=None):
    received_payments = Payment.objects.filter(
        Q(patient=user_id),
        Q(invoice__isnull=True) | Q(invoice=None),
        transaction_type='collected',
    )

    if exclude_invoice:
        received_payments = received_payments.exclude(
            invoice__id=exclude_invoice
        )

    free_income = received_payments.aggregate(received=Sum('price', default=0))['received']

    refund_payments = Payment.objects.filter(
        Q(invoice__appointment__patient=user_id) | Q(patient=user_id),
        transaction_type='paid'
    )
    if exclude_invoice:
        refund_payments = refund_payments.exclude(
            invoice__id=exclude_invoice
        )
    refund = refund_payments.aggregate(paid=Sum('price', default=0))['paid']

    return free_income, refund, free_income - refund


def get_user_collected_invoice(user_id, exclude_invoice=None):
    invoices = Invoice.objects.filter(
        Q(patient=user_id)
    )

    if exclude_invoice:
        invoices = invoices.exclude(id=exclude_invoice)

    grand_total = invoices.aggregate(
        grand_total=Sum('grand_total', default=0)
    )['grand_total']

    payments = invoices.filter(payment__type='payment').aggregate(
        payments=Sum('payment__price', default=0)
    )['payments']

    wallet = invoices.aggregate(
        wallet=Sum('payment__excess_amount', default=0)
    )['wallet']

    return {'grand_total': grand_total, 'payments': payments, 'wallet': wallet, }


def get_user_due_invoices(user_id, exclude_invoice=None):
    due_invoices = Invoice.objects.select_related('payment', 'appointment').exclude(
        Q(appointment__payment_status='collected')
    ).filter(
        patient=user_id,
        appointment__appointment_status='checked_out'
    )

    if exclude_invoice:
        due_invoices = due_invoices.exclude(id=exclude_invoice)

    grand_total = due_invoices.aggregate(
        grand_total=Sum('grand_total', default=0))['grand_total']

    payments = due_invoices.filter(payment__type='payment').aggregate(
        payments=Sum('payment__price', default=0))['payments']

    wallet = due_invoices.filter(payment__type='wallet').aggregate(
        wallet=Sum('payment__price', default=0))['wallet']

    return grand_total, payments, wallet


def _get_user_wallet_balance(user_id):
    free_income, refund, balance = get_user_payments(user_id)
    invoices = get_user_collected_invoice(user_id)
    # due_total, due_payments, due_wallet = get_user_due_invoices(user_id)
    # invoice_received = invoices['payments'] + invoices['wallet']
    # extra_paid = invoices['payments'] - invoices['grand_total']
    cash_in = balance + invoices['payments']  # + due_payments
    invoices_total = invoices['grand_total']  # + due_total

    # due_received = due_invoices['payments'] + due_invoices['wallet']
    # due = due_invoices['grand_total'] - ()
    # due = - due_total

    # new_balance = balance + extra_paid - due
    # after_wallet_deduct = new_balance + invoices['wallet']

    # print(balance, extra_paid, new_balance, after_wallet_deduct, due_invoices)

    # Less if any values deducted from wallet on previous pending invoices
    # return new_balance - due_invoices['wallet']
    return cash_in - invoices_total


def get_user_wallet_balance(user_id):
    excess_amount = Payment.objects.filter(
        patient=user_id
    ).aggregate(
        excess_amount=Sum('excess_amount', default=0)
    )['excess_amount']
    unpaid_invoices = Invoice.objects.filter(is_paid=False, patient=user_id)
    unpaid_amount = unpaid_invoices.annotate(
        payments=Sum('payment__price', default=0),
        total=Sum('grand_total', default=0)
    )
    due = [invoice.total - invoice.payments for invoice in unpaid_amount if invoice.total - invoice.payments > 0]
    return excess_amount - sum(due)


def get_user_wallet_balance_exclude_pending_invoices(user_id, invoice_id):
    wallet_balace = _get_user_wallet_balance(user_id)
    invoice_payments = Payment.objects.filter(
        patient=user_id, invoice=invoice_id
    ).aggregate(
        balance=Sum('price', default=0)
    )['balance']
    wallet_deduct = Wallet.objects.filter(
        user=user_id, invoice=invoice_id
    ).aggregate(
        balance=Sum('amount', default=0)
    )['balance']

    new_balance = wallet_balace - invoice_payments - wallet_deduct
    return new_balance


def add_user_wallet_balance(amount, wallet_pay, patient_id):
    balance_payments = Payment.objects.filter(
        patient=patient_id, balance__gt=0
    ).order_by('id')
    amount_to_add = abs(amount)
    for payment in balance_payments:
        balance = payment.balance
        new_balance = balance - amount_to_add if balance > amount_to_add else 0
        contribution_amount = amount_to_add if balance > amount_to_add else balance
        amount_to_add = amount_to_add - contribution_amount
        wallet_payment_data = deepcopy(wallet_pay)
        wallet_payment_data.update({
            'price': contribution_amount,
            'excess_amount': -abs(contribution_amount),
            'receipt_id': payment.id,
        })
        wallet_payment_serializer = PaymentSerializer(data=wallet_payment_data)
        if wallet_payment_serializer.is_valid():
            wallet_payment_serializer.save()
            payment.balance = new_balance
            payment.save()
        else:
            logger.error(wallet_payment_serializer.errors)
        if contribution_amount == 0:
            break


def _add_user_wallet_balance(amount, patient_id, invoice_id, userid, desc=""):
    if amount > 0:
        desc = desc if desc else 'added balance after payment for invoice'
        type = 'dr'
    else:
        desc = desc if desc else 'balance due after payment for invoice'
        type = 'cr'

    wallet_data = {'user': patient_id, 'amount': abs(amount),
                   'type': type, 'invoice': invoice_id,
                   'desc': desc, 'created_by': userid,
                   'updated_by': userid}
    wallet_serializer = WalletSerializer(data=wallet_data)
    if wallet_serializer.is_valid():
        wallet_serializer.save()
        if type == 'dr':
            balance_payments = Payment.objects.filter(
                patient=patient_id, balance__gt=0
            ).order_by('id')
            amount_to_add = abs(amount)
            for payment in balance_payments:
                balance = payment.balance
                new_balance = balance - amount_to_add if balance > amount_to_add else 0
                contribution_amount = amount_to_add if balance > amount_to_add else balance
                amount_to_add = amount_to_add - contribution_amount
                wallet_payment_data = {'wallet': wallet_serializer.data.get('id'),
                                       'payment': payment.id,
                                       'contribution_amount': contribution_amount,
                                       'created_by': userid,
                                       'updated_by': userid}
                wallet_payment_serializer = WalletPaymentSerializer(data=wallet_payment_data)
                wallet_payment_serializer.is_valid()
                wallet_payment_serializer.save()
                payment.balance = new_balance
                payment.save()
                if contribution_amount == 0:
                    break

    else:
        logger.error(f"collect_payment"
                     f"{wallet_serializer.errors} - "
                     f"wallet transaction failed")


def _get_user_advance_balance(user_id, exclude_invoice_id):
    _, _, balance = get_user_payments(user_id, exclude_invoice_id)
    invoices = get_user_collected_invoice(user_id, exclude_invoice_id)
    due_total, due_payments, due_wallet = get_user_due_invoices(user_id, exclude_invoice_id)
    invoice_balance = invoices['payments'] - invoices['grand_total']
    actual_balance = invoice_balance > 0 and invoice_balance or 0  # this is hack
    balance_invoice_free = balance + invoice_balance
    # balance_after_wallet_pay = balance_invoice_free - invoices['wallet']
    balance_after_wallet_pay = balance_invoice_free - due_wallet
    return balance_after_wallet_pay


def get_user_advance_balance(user_id, exclude_invoice_id):
    payments = Payment.objects.filter(
        Q(patient=user_id)
    )
    grand_total, due, wallet, received = 0,0,0,0
    if exclude_invoice_id:
        payments = payments.exclude(
            invoice__id=exclude_invoice_id
        )
        invoice = Invoice.objects.get(id=exclude_invoice_id)
        grand_total = invoice.grand_total
        payments = Payment.objects.filter(invoice=exclude_invoice_id)
        # received = payments.filter(transaction_type='collected').aggregate(amount=Sum('price', default=0))['amount']
        wallet = payments.filter(transaction_type='wallet_payment').aggregate(amount=Sum('price', default=0))['amount']


    advance = payments.aggregate(amount=Sum('excess_amount', default=0))['amount']
    # excluded_advance = grand_total - (advance - (wallet))
    # return advance if not exclude_invoice_id else excluded_advance
    return advance

def temp(user_id):
    _, _, balance = get_user_payments(user_id)
    invoices = get_user_collected_invoice(user_id)
    due_total, due_payments, due_wallet = get_user_due_invoices(user_id)
    final_income = invoices['payments'] + due_payments + balance
    invoice_sum = invoices['grand_total'] - invoices['wallet']

    wallet_payments = invoices['wallet'] + due_wallet
    after_final_income = final_income - wallet_payments
    sum = after_final_income - invoice_sum

    # invoice_balance = final_income - invoices['grand_total']
    # actual_balance = invoice_balance > 0 and invoice_balance or 0
    # actual_balance = balance + invoice_balance - invoices['wallet']
    # actual_balance = invoice_balance > 0 and invoice_balance or 0
    # balance_invoice_free = balance + actual_balance + due_invoices['payments']
    # balance_after_wallet_pay = balance_invoice_free - invoices['wallet']
    # balance_after_wallet_pay = balance_invoice_free - due_invoices['wallet']
    return sum


def due_invoices_by_user(user_id):
    due_invoices = Invoice.objects.filter(
        Q(patient=user_id)
    ).annotate(
        payments=Sum('payment__price', default=0),
    ).annotate(
        wallet_payments=Sum('wallet__amount', default=0),
    ).annotate(
        due=F('grand_total') - F('payments') - F('wallet_payments')
    ).filter(due__gt=0)

    return due_invoices


def get_all_details_by_user(user_id):
    appointments = Appointment.objects.filter(patient=user_id)
    invoices = Invoice.objects.filter(patient=user_id)
    invoices_without_appointment = Invoice.objects.filter(patient=user_id, appointment__isnull=True)
    payments = Payment.objects.filter(patient=user_id)
    free_payments = Payment.objects.filter(patient=user_id, invoice__isnull=True)
    invoice_payments = Payment.objects.filter(invoice__patient=user_id, invoice__isnull=False)
    wallet = Wallet.objects.filter(user=user_id)
    invoices_sum = invoices.values('grand_total').aggregate(invoice_total=Sum('grand_total', default=0))[
        'invoice_total']
    payments_sum = payments.values('price').aggregate(payment_price=Sum('price', default=0))['payment_price']
    due_amount = payments_sum - invoices_sum
    return appointments, invoices, payments, wallet, invoices_without_appointment, free_payments, invoice_payments, \
        invoices_sum, payments_sum, due_amount


def patient_migrate(fromid, toid, dry=True):
    usermodel = get_user_model()
    from_user = usermodel.objects.get(id=fromid)
    to_user = usermodel.objects.get(id=toid)
    print(f"Migrate {from_user} => {to_user}")
    appointments, invoices, payments, wallet, _, _, _, _, _, _ = get_all_details_by_user(fromid)
    print(f"Appointments {len(appointments)}")
    print(f"Invoices {len(invoices)}")
    print(f"Payments {len(payments)}")
    print(f"wallet {len(wallet)}")
    if not dry:
        for appointment in appointments:
            appointment.patient = to_user
            appointment.save()

        for invoice in invoices:
            invoice.patient = to_user
            invoice.save()

        for payment in payments:
            payment.patient = to_user
            payment.save()

        for wall in wallet:
            wall.user = to_user
            wall.save()

        from_user.delete()
    return "Migrated"
