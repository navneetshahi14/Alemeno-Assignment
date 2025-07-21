from django.db import models

# Create your models here.
class Customers(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.PositiveBigIntegerField(max_length=15, unique=True)
    monthly_salary = models.PositiveBigIntegerField()
    approved_limit = models.PositiveBigIntegerField()
    current_debt = models.PositiveBigIntegerField()
    age = models.PositiveIntegerField()

    def save(self,*args, **kwargs):
        if not self.approved_limit:
            calculate_limit = 36 * self.monthly_salary
            self.approved_limit = round(calculate_limit / 100000) * 100000
        super().save(*args,**kwargs)

    
class Loan(models.Model):
    customer_id = models.ForeignKey(Customers,on_delete=models.CASCADE,related_name="loans")
    loan_amount = models.FloatField()
    tenure = models.PositiveBigIntegerField(help_text="Tenure in month")
    interest_rate = models.FloatField(help_text="Annual interest rate (%)")
    monthly_installment = models.FloatField()
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    emis_paid_on_time = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"Loan {self.id} for {self.customer_id.first_name}"