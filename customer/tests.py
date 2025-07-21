from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Customers
from .models import Loan

class CreditSystemAPITests(APITestCase):

    def setUp(self):
        self.customer_data = {
            "first_name": "Navneet",
            "last_name": "Shahi",
            "age": 22,
            "monthly_salary": 78000,
            "phone_number": 9999999999
        }
        url = reverse('register')
        response = self.client.post(url, self.customer_data, format='json')
        
        self.id = response.data['customer_id']
        self.approved_limit = response.data['approved_limit']

    def test_register_customer(self):
        self.assertEqual(Customers.objects.count(), 1)
        customer = Customers.objects.first()
        self.assertEqual(customer.first_name, "Navneet")
        self.assertEqual(customer.approved_limit, 2800000)

    def test_check_eligibility_pass(self):
        payload = {
            "customer_id": self.id,
            "loan_amount": 50000,
            "interest_rate": 18,
            "tenure": 12
        }
        url = reverse("check_eligibility")
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approved', response.data)
        self.assertIn('monthly_installment', response.data)

    def test_check_eligibility_fail_due_to_emis(self):
        customer = Customers.objects.get(id=self.id)
        customer.current_debt = 2000000
        customer.save()

        payload = {
            "customer_id": self.id,
            "loan_amount": 1000000,
            "interest_rate": 10,
            "tenure": 12
        }
        url = reverse('check_eligibility')
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['approved'])

    def test_create_loan_success(self):
        payload = {
            "customer_id": self.id,
            "loan_amount": 50000,
            "interest_rate": 18,
            "tenure": 12
        }
        url = reverse('create_loan')
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['loan_amount'])
        self.assertEqual(Loan.objects.count(), 1)

    def test_create_loan_failure(self):
        payload = {
            "customer_id": self.id,
            "loan_amount": 50000000, 
            "interest_rate": 5,     
            "tenure": 24
        }
        url = reverse('create_loan')
        response = self.client.post(url, payload, format='json')
        print(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['message'],'Loan rejected: EMI exceeds 50% of monthly salary')

    def test_view_loan_detail(self):
        create_payload = {
            "customer_id": self.id,
            "loan_amount": 50000,
            "interest_rate": 18,
            "tenure": 12
        }
        url = reverse('create_loan')
        create_res = self.client.post(url, create_payload, format='json')
        loan_id = create_res.data['loan_id']
        url1 = reverse('view_loan', kwargs={'loan_id': loan_id})
        res = self.client.get(url1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['id'], loan_id)
        self.assertEqual(res.data['customer_id'],self.id)

    def test_view_all_loans_by_customer(self):
        url = reverse('create_loan')
        for _ in range(2):
            self.client.post(url, {
                "customer_id": self.id,
                "loan_amount": 30000,
                "interest_rate": 16,
                "tenure": 6
            }, format='json')

        url1 = reverse('view_loans', kwargs={'customer_id': self.id})
        response = self.client.get(url1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) >= 2)
        self.assertIn('monthly_installment', response.data[0])
