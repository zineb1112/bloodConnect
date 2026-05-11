import random
from datetime import timedelta, date

from django.core.management.base import BaseCommand
from django.utils import timezone

from hospital_app.models import (
    HospitalUser, Hospital,
    BloodRequest, Donation, Campaign
)

BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# Relative demand weights (realistic)
BLOOD_WEIGHTS = {
    "O+": 0.35,
    "A+": 0.25,
    "B+": 0.15,
    "O-": 0.10,
    "A-": 0.07,
    "B-": 0.04,
    "AB+": 0.03,
    "AB-": 0.01,
}


class Command(BaseCommand):
    help = "Seed realistic hospital, blood request, donation, and campaign data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding hospital data...")

        hospitals = self.create_hospitals()
        self.create_campaigns(hospitals)
        total_requests = self.create_blood_requests(hospitals)

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Database successfully seeded!"
        ))
        self.stdout.write(f"   - Hospitals: {len(hospitals)}")
        self.stdout.write(f"   - Blood Requests: {total_requests}")
        self.stdout.write(f"   - Fulfilled requests: ~{int(total_requests * 0.85)} (for forecasting)")
        self.stdout.write(f"\n💡 Test forecast at: http://localhost:8000/forcast/")

    # ---------------------------
    def create_hospitals(self):
        locations = [
            ("Rabat Central Hospital", "Rabat", "Rabat-Salé"),
            ("Casablanca Health Center", "Casablanca", "Casablanca-Settat"),
            ("Marrakech Medical Hub", "Marrakech", "Marrakech-Safi"),
            ("Agadir Regional Hospital", "Agadir", "Souss-Massa"),
        ]

        hospitals = []

        for i, (name, city, region) in enumerate(locations):
            # Check if hospital already exists to avoid duplicates
            existing_hospital = Hospital.objects.filter(city=city, region=region).first()
            if existing_hospital:
                self.stdout.write(f"Using existing hospital: {existing_hospital.name}")
                hospitals.append(existing_hospital)
                continue
                
            user = HospitalUser.objects.create_user(
                username=f"hospital{i}",
                email=f"hospital{i}@test.com",
                password="test1234"
            )

            hospital = Hospital.objects.create(
                user=user,
                name=name,
                city=city,
                region=region,
                phone="0522000000",
                address=f"{city} Main Street"
            )

            hospitals.append(hospital)

        return hospitals

    # ---------------------------
    def create_campaigns(self, hospitals):
        for hospital in hospitals:
            for i in range(random.randint(1, 3)):
                Campaign.objects.create(
                    hospital=hospital,
                    title=f"Blood Donation Campaign {i+1}",
                    description="Urgent blood donation campaign",
                    starting_date=date.today() - timedelta(days=60),
                    ending_date=date.today() - timedelta(days=30),
                    address=hospital.address,
                    duration="2 weeks"
                )

    # ---------------------------
    def create_blood_requests(self, hospitals):
        start_date = date.today() - timedelta(days=720)  # ~24 months
        total_requests = 0

        for hospital in hospitals:
            current = start_date

            while current <= date.today():
                monthly_volume = random.randint(15, 35)

                # Seasonal effect (summer ↑)
                if current.month in [6, 7, 8]:
                    monthly_volume += 8

                    # Agadir has stronger summer pressure
                    if hospital.city == "Agadir":
                        monthly_volume += 6
                elif current.month in [1, 2]:
                    monthly_volume -= 5

                for _ in range(monthly_volume):
                    blood_type = random.choices(
                        list(BLOOD_WEIGHTS.keys()),
                        weights=BLOOD_WEIGHTS.values(),
                        k=1
                    )[0]

                    # Set status: 85% fulfilled (for forecasting), 10% open, 5% expired
                    status_choice = random.choices(
                        ['fulfilled', 'open', 'expired'],
                        weights=[85, 10, 5]
                    )[0]
                    
                    request = BloodRequest.objects.create(
                        hospital=hospital,
                        blood_type=blood_type,
                        request_date=timezone.make_aware(
                            timezone.datetime(
                                current.year,
                                current.month,
                                random.randint(1, 28)
                            )
                        ),
                        deadline=current + timedelta(days=7),
                        quantity_needed=random.randint(1, 3),
                        status=status_choice,  # CRITICAL: Set status for forecasting
                        description="Routine hospital blood demand"
                    )

                    total_requests += 1

                    # Some donations (more likely for fulfilled requests)
                    if request.status == 'fulfilled' and random.random() < 0.7:
                        Donation.objects.create(
                            request=request,
                            donor_id=random.randint(1, 500),
                            status=random.choice(
                                ["approved", "completed"]
                            )
                        )
                    elif request.status == 'open' and random.random() < 0.3:
                        Donation.objects.create(
                            request=request,
                            donor_id=random.randint(1, 500),
                            status="pending"
                        )

                # Next month
                if current.month == 12:
                    current = date(current.year + 1, 1, 1)
                else:
                    current = date(current.year, current.month + 1, 1)
        
        return total_requests
