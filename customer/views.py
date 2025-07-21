from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import CustomerRegisterSerializer,CreateLoanSerializer ,LoanSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Customers,Loan
import math
from .task import calculate_credit_score_task
from .utils import calculate_emi
from datetime import date , timedelta
from django.http import Http404

class RegisterCustomerView(APIView):
    def post(self,request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response({
                "customer_id": customer.id,
                "name": f"{customer.first_name} {customer.last_name}",
                "age": customer.age,
                "monthly_income": customer.monthly_salary,
                "approved_limit": customer.approved_limit,
                "phone_number": customer.phone_number
            },status=status.HTTP_201_CREATED)
        return Response (serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class CheckEligibiltyView(APIView):
    def post(self,request):
        try:
            print(request.data)
            customer = Customers.objects.get(id=request.data['customer_id'])
            print({customer.id})
        except Customers.DoesNotExist:
            return Response({"error":"Customer not found"},status=status.HTTP_404_NOT_FOUND)


        loan_amount = float(request.data['loan_amount'])
        interest_rate = float(request.data['interest_rate'])
        tenure = int(request.data['tenure'])

        r = interest_rate / (12 * 100)
        emi = calculate_emi(loan_amount,interest_rate,tenure)

        existing_loans = Loan.objects.filter(customer_id=customer)
        total_existing_emi = sum(
            loan.loan_amount * (loan.interest_rate / (12 * 100)) * math.pow(1 + loan.interest_rate / (12 * 100), loan.tenure) /
            (math.pow(1 + loan.interest_rate / (12 * 100), loan.tenure) - 1)
            for loan in existing_loans
        )
        if total_existing_emi + emi > 0.5 * customer.monthly_salary:
            return Response({
                "customer_id": customer.id,
                "approved": False,
                "message": "Loan rejected: EMI exceeds 50% of monthly salary"
            })
        credit_score = calculate_credit_score_task(customer.id, customer.approved_limit)

        approved = False
        corrected_interest_rate = None

        if credit_score > 50:
            approved = True
        elif 30 < credit_score <= 50:
            if interest_rate > 12:
                approved = True
            else:
                corrected_interest_rate = 13
        elif 10 < credit_score <= 30:
            if interest_rate > 16:
                approved = True
            else:
                corrected_interest_rate = 17
        elif credit_score <= 10:
            approved = False

        response = {
            "customer_id": customer.id,
            "approved": approved,
            "credit_score": credit_score,
            "monthly_installment": emi,
            "tenure": tenure,
            "interest_rate": interest_rate,
            "message": "Loan approved" if approved else "Loan not approved"
        }

        if corrected_interest_rate:
            response["corrected_interest_rate"] = corrected_interest_rate

        return Response(response)

class CreateLoanView(APIView):
    def post(self, request):
        serializer = CreateLoanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            customer = Customers.objects.get(id=data['customer_id'])
        except Customers.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']

        r = interest_rate / (12 * 100)
        emi = loan_amount * r * math.pow(1 + r, tenure) / (math.pow(1 + r, tenure) - 1)
        emi = round(emi, 2)

        total_existing_emi = sum(
            loan.loan_amount * (loan.interest_rate / (12 * 100)) * math.pow(1 + loan.interest_rate / (12 * 100), loan.tenure) /
            (math.pow(1 + loan.interest_rate / (12 * 100), loan.tenure) - 1)
            for loan in Loan.objects.filter(customer_id=customer)
        )

        if total_existing_emi + emi > 0.5 * customer.monthly_salary:
            return Response({
                "message": "Loan rejected: EMI exceeds 50% of monthly salary"
            }, status=403)

        credit_score = calculate_credit_score_task(customer.id, customer.approved_limit)

        approved = False
        corrected_interest_rate = None

        if credit_score > 50:
            approved = True
        elif 30 < credit_score <= 50:
            if interest_rate > 12:
                approved = True
            else:
                corrected_interest_rate = 13
        elif 10 < credit_score <= 30:
            if interest_rate > 16:
                approved = True
            else:
                corrected_interest_rate = 17
        elif credit_score <= 10:
            approved = False

        if not approved:
            return Response({
                "message": "Loan not approved",
                "credit_score": credit_score
            }, status=403)

        if corrected_interest_rate:
            interest_rate = corrected_interest_rate
            r = interest_rate / (12 * 100)
            emi = loan_amount * r * math.pow(1 + r, tenure) / (math.pow(1 + r, tenure) - 1)
            emi = round(emi, 2)

        end_date = date.today() + timedelta(days=30 * tenure)

        loan = Loan.objects.create(
            customer_id=customer,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure,
            monthly_installment=emi,
            end_date=end_date
        )

        return Response({
            "loan_id": loan.id,
            "customer_id": customer.id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "tenure": loan.tenure,
            "monthly_installment": loan.monthly_installment,
            "start_date": loan.start_date,
            "end_date": loan.end_date,
            "message": "Loan created successfully",
            "credit_score": credit_score
        }, status=201)

class ViewLoanDetails(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            raise Http404("Loan Not Found")
        
        serializer = LoanSerializer(loan)
        return Response(serializer.data)
    
class ViewCustomerLoans(APIView):
    def get(self,request, customer_id):
        try:
            customer = Customers.objects.get(id=customer_id)
        except Customers.DoesNotExist:
            raise Http404("Customer does not exist")
        
        loans = Loan.objects.filter(customer_id=customer)
        serializer = LoanSerializer(loans,many=True)
        return Response(serializer.data)