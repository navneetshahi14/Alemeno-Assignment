from rest_framework import serializers
from .models import Customers, Loan

class CustomerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'monthly_salary','age']

    def create(self, validated_data):
        monthly_salary = validated_data.get('monthly_salary')
        approved_limit = round(36 * monthly_salary, -5)

        customer = Customers.objects.create(
            approved_limit=approved_limit,
            current_debt=0,
            **validated_data
        )
        return customer

class CreateLoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'