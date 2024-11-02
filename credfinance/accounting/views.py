from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from utils.utils import Utils, IsFinanceManager  

class ExpenseRequestAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceManager]

    def get(self, request):
        expense_requests = ExpenseRequest.objects.all()
        serializer = ExpenseRequestSerializer(expense_requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExpenseRequestSerializer(data=request.data)
        if serializer.is_valid():
            expense_request = serializer.save(requested_by=request.user)

            Utils.log_audit_trail(
                user=request.user,
                action="Created Expense Request",
                model_name="ExpenseRequest",
                model_id=expense_request.id,
                new_value=str(expense_request.amount),
                ip_address=request.META.get("REMOTE_ADDR")
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            expense_request = ExpenseRequest.objects.get(pk=pk)
            previous_approved_status = expense_request.approved

            expense_request.approved = True  
            expense_request.approved_by = request.user
            expense_request.save()

            Utils.log_audit_trail(
                user=request.user,
                action="Approved Expense Request",
                model_name="ExpenseRequest",
                model_id=expense_request.id,
                previous_value=str(previous_approved_status),
                new_value=str(expense_request.approved),
                ip_address=request.META.get("REMOTE_ADDR")
            )
            return Response({'message': 'Expense request approved successfully.'}, status=status.HTTP_200_OK)

        except ExpenseRequest.DoesNotExist:
            return Response({'error': 'Expense request not found.'}, status=status.HTTP_404_NOT_FOUND)


class IncomeAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceManager]

    def get(self, request):
        income_entries = Income.objects.all()
        serializer = IncomeSerializer(income_entries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = IncomeSerializer(data=request.data)
        if serializer.is_valid():
            income = serializer.save(added_by=request.user)

            if income.income_type == 'cash':
                debit_account = "Cash"  
                credit_account = "Cash Income"  
            elif income.income_type == 'bank':
                debit_account = "Bank" 
                credit_account = "Bank Income"
            else:
                return Response({"error": "Invalid income type."}, status=status.HTTP_400_BAD_REQUEST)

            amount = income.amount
            description = f"Income received from {income.source}"

            Utils.record_income_transaction(income, debit_account, credit_account, amount, description)

            Utils.log_audit_trail(
                user=request.user,
                action="Added Income",
                model_name="Income",
                model_id=income.id,
                new_value=str(income.amount),
                ip_address=request.META.get("REMOTE_ADDR")
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuotationAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceManager]

    def get(self, request):
        expense_request_id = request.query_params.get('expense_request')
        if expense_request_id:
            quotations = Quotation.objects.filter(expense_request_id=expense_request_id)
        else:
            quotations = Quotation.objects.all()
        
        serializer = QuotationSerializer(quotations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        expense_request_id = request.data.get('expense_request')
        try:
            expense_request = ExpenseRequest.objects.get(id=expense_request_id)
        except ExpenseRequest.DoesNotExist:
            return Response({"error": "Expense Request not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuotationSerializer(data=request.data)
        if serializer.is_valid():
            quotation = serializer.save(added_by=request.user, expense_request=expense_request)

            Utils.log_audit_trail(
                user=request.user,
                action="Added Quotation",
                model_name="Quotation",
                model_id=quotation.id,
                new_value=str(serializer.validated_data['amount']),
                ip_address=request.META.get("REMOTE_ADDR")
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            quotation = Quotation.objects.get(id=pk)
        except Quotation.DoesNotExist:
            return Response({"error": "Quotation not found."}, status=status.HTTP_404_NOT_FOUND)

        selected_status = request.data.get('selected')
        if selected_status is not None:
            quotation.selected = selected_status
            quotation.save()

            Utils.log_audit_trail(
                user=request.user,
                action="Updated Quotation Selected Status",
                model_name="Quotation",
                model_id=quotation.id,
                previous_value=str(not quotation.selected), 
                new_value=str(quotation.selected),          
                ip_address=request.META.get("REMOTE_ADDR")
            )
            return Response({"message": "Quotation updated successfully."}, status=status.HTTP_200_OK)

        return Response({"error": "Selected status not provided."}, status=status.HTTP_400_BAD_REQUEST)


class InvoiceAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceManager]

    def get(self, request):
        expense_request_id = request.query_params.get('expense_request')
        if expense_request_id:
            invoices = Invoice.objects.filter(expense_request_id=expense_request_id)
        else:
            invoices = Invoice.objects.all()

        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        expense_request_id = request.data.get('expense_request')
        try:
            expense_request = ExpenseRequest.objects.get(id=expense_request_id)
        except ExpenseRequest.DoesNotExist:
            return Response({"error": "Expense Request not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice = serializer.save(added_by=request.user, expense_request=expense_request)

            Utils.log_audit_trail(
                user=request.user,
                action="Added Invoice",
                model_name="Invoice",
                model_id=invoice.id,
                new_value=str(serializer.validated_data['amount']),
                ip_address=request.META.get("REMOTE_ADDR")
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            invoice = Invoice.objects.get(id=pk)
        except Invoice.DoesNotExist:
            return Response({"error": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvoiceSerializer(invoice, data=request.data, partial=True)  
        if serializer.is_valid():
            previous_value = str(invoice.amount)  
            invoice = serializer.save()

            Utils.log_audit_trail(
                user=request.user,
                action="Updated Invoice",
                model_name="Invoice",
                model_id=invoice.id,
                previous_value=previous_value,
                new_value=str(invoice.amount),  
                ip_address=request.META.get("REMOTE_ADDR")
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProofOfPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsFinanceManager]

    def get(self, request):
        expense_request_id = request.query_params.get('expense_request')
        if expense_request_id:
            proof_of_payments = ProofOfPayment.objects.filter(expense_request_id=expense_request_id)
        else:
            proof_of_payments = ProofOfPayment.objects.all()

        serializer = ProofOfPaymentSerializer(proof_of_payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        expense_request_id = request.data.get('expense_request')
        try:
            expense_request = ExpenseRequest.objects.get(id=expense_request_id)
        except ExpenseRequest.DoesNotExist:
            return Response({"error": "Expense Request not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProofOfPaymentSerializer(data=request.data)
        if serializer.is_valid():
            proof_of_payment = serializer.save(added_by=request.user, expense_request=expense_request)

            Utils.log_audit_trail(
                user=request.user,
                action="Added Proof of Payment",
                model_name="ProofOfPayment",
                model_id=proof_of_payment.id,
                new_value=serializer.validated_data['transaction_id'],
                ip_address=request.META.get("REMOTE_ADDR")
            )

            debit_account, credit_account = self.get_accounts_based_on_payment_method(serializer.validated_data['payment_method'], proof_of_payment.amount)

            if debit_account and credit_account:
                Utils.record_expense_transaction(proof_of_payment, debit_account, credit_account, proof_of_payment.amount, "Payment received for Expense Request ID: {}".format(expense_request_id))

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_accounts_based_on_payment_method(self, payment_method, amount):
        """ Logic to determine the debit and credit accounts based on the payment method """
        if payment_method == 'cash':
            return 'cash_account_id', 'income_account_id'  
        elif payment_method == 'bank':
            return 'bank_account_id', 'income_account_id' 
        return None, None

    def put(self, request, pk):
        try:
            proof_of_payment = ProofOfPayment.objects.get(id=pk)
        except ProofOfPayment.DoesNotExist:
            return Response({"error": "Proof of Payment not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProofOfPaymentSerializer(proof_of_payment, data=request.data, partial=True)  
        if serializer.is_valid():
            previous_value = str(proof_of_payment.transaction_id)  
            proof_of_payment = serializer.save()

            Utils.log_audit_trail(
                user=request.user,
                action="Updated Proof of Payment",
                model_name="ProofOfPayment",
                model_id=proof_of_payment.id,
                previous_value=previous_value,
                new_value=str(proof_of_payment.transaction_id),  
                ip_address=request.META.get("REMOTE_ADDR")
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
