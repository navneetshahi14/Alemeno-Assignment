from django.urls import path
from .views import RegisterCustomerView, CheckEligibiltyView, CreateLoanView, ViewLoanDetails, ViewCustomerLoans

urlpatterns = [
    path('register/',RegisterCustomerView.as_view(),name="register"),
    path('check-eligibility/', CheckEligibiltyView.as_view(),name="check-eligibility"),
    path('create-loan/', CreateLoanView.as_view() , name="create loan"),
    path('view-loan/<int:loan_id>/',ViewLoanDetails.as_view(), name="view loan"),
    path('view-loans/<int:customer_id>/',ViewCustomerLoans.as_view(),name="view loans")
]
