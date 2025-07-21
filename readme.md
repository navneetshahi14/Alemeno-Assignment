````markdown
# 💳 Credit Approval System – Alemeno Internship Assignment

This project is a Django-based **Credit Approval System** built as part of an internship assignment for Alemeno. It uses **Django REST Framework** and **PostgreSQL**, and is fully dockerized. The system handles customer onboarding, loan eligibility, and loan management.

## 🛠 Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Celery (for background data ingestion)
- Docker & Docker Compose

---

## 📦 Features

### 🔹 1. Customer Registration (`customer/register`)
- Adds a new customer with:
  - Approved limit = `36 × monthly_salary` (rounded to nearest lakh)

### 🔹 2. Loan Eligibility Check (`customer/check-eligibility`)
- Calculates credit score based on:
  - Past loan repayment history
  - No. of past loans
  - Current year activity
  - Total loan volume
  - Debt-to-limit ratio

- Applies business logic to approve/reject loans and correct interest rate if needed.

### 🔹 3. Create Loan (`customer/create-loan`)
- Creates new loans only if eligibility conditions are met.
- Responds with loan info or rejection message.

### 🔹 4. View Loan by ID (`customer/view-loan/<loan_id>`)
- Returns customer + loan details.

### 🔹 5. View All Loans by Customer (`customer/view-loans/<customer_id>`)
- Lists all active loans and EMIs left for a customer.

---

## 🐳 Dockerized Setup

### Prerequisites:
- Docker
- Docker Compose

### Run the app:

```bash
docker compose up --build
````

### Test the app:

Step1-->
```bash
docker compose up
```
Step2-->
```bash
docker compose exec web python manage.py test


> This spins up Django, PostgreSQL, and Celery in separate containers.

---

## 📂 Project Structure

```
Alemeno-Assignment/
├── credit_system/      # Django settings and URLs
├── customer/               # App handling customer models and APIs
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── manage.py
```

---

## 📈 API Overview

| Endpoint                | Method | Description                |
| ----------------------- | ------ | -------------------------- |
| `/register`             | POST   | Register a new customer    |
| `/check-eligibility`    | POST   | Check loan eligibility     |
| `/create-loan`          | POST   | Create new loan            |
| `/view-loan/<loan_id>`  | GET    | View single loan           |
| `/view-loans/<cust_id>` | GET    | View all loans by customer |

---

## ✅ Additional Notes

* Uses **Compound Interest** for EMI calculations.
* Code is modular and follows clean architecture.
* Background tasks are managed using Celery.

---

## 🙋‍♂️ Author

Made by [Navneet Shahi](https://github.com/navneetshahi14)
For: Alemeno Internship Assignment

---

## 🛡 License

This project is for educational and demo purposes only.

````

