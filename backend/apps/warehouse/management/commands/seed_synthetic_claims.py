"""
Generates synthetic healthcare claims data only. No real PHI is used in
this portfolio project. All identifiers are fabricated
(MBR-10039281, CLM-2026-000938, PRV-20381, PAY-2026-005921, ...).
"""

import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from apps.warehouse.models import (
    RawAdjustment,
    RawClaim,
    RawClaimServiceLine,
    RawDenialCode,
    RawDiagnosisCategory,
    RawEligibility,
    RawMember,
    RawPayer,
    RawPayment,
    RawProcedureCategory,
    RawProvider,
)

fake = Faker()
Faker.seed(42)
random.seed(42)

DIAGNOSIS_CATEGORIES = [
    ("E11", "Type 2 Diabetes Mellitus"),
    ("I10", "Essential Hypertension"),
    ("J45", "Asthma"),
    ("M54", "Back Pain"),
    ("F41", "Anxiety Disorder"),
    ("K21", "Gastroesophageal Reflux"),
    ("Z00", "General Health Exam"),
    ("S93", "Ankle Sprain"),
    ("N39", "Urinary Tract Infection"),
    ("R51", "Headache"),
]

PROCEDURE_CATEGORIES = [
    ("99213", "Office Visit - Established Patient"),
    ("99214", "Office Visit - Detailed"),
    ("80053", "Comprehensive Metabolic Panel"),
    ("71046", "Chest X-Ray"),
    ("93000", "Electrocardiogram"),
    ("36415", "Blood Draw"),
    ("90834", "Psychotherapy Session"),
    ("97110", "Therapeutic Exercise"),
    ("12001", "Simple Wound Repair"),
    ("99283", "Emergency Department Visit"),
]

DENIAL_CODES = [
    ("CO-16", "Claim lacks information needed for adjudication", "Documentation"),
    ("CO-45", "Charge exceeds fee schedule/maximum allowable", "Pricing"),
    ("CO-50", "Non-covered service - not medically necessary", "Medical Necessity"),
    ("CO-97", "Benefit included in another payment/allowance", "Bundling"),
    ("PR-1", "Deductible amount", "Patient Responsibility"),
    ("CO-29", "Time limit for filing has expired", "Timely Filing"),
]

SPECIALTIES = ["Family Medicine", "Internal Medicine", "Cardiology", "Orthopedics", "Behavioral Health", "Urgent Care"]
PAYER_TYPES = ["Commercial", "Medicare", "Medicaid"]
PLAN_TYPES = ["PPO", "HMO", "EPO", "HDHP"]
CLAIM_TYPES = ["Professional", "Institutional", "Pharmacy"]


class Command(BaseCommand):
    help = "Seeds synthetic healthcare claims data (members, providers, payers, claims, payments, etc.)"

    def add_arguments(self, parser):
        parser.add_argument("--members", type=int, default=250)
        parser.add_argument("--providers", type=int, default=40)
        parser.add_argument("--payers", type=int, default=8)
        parser.add_argument("--claims", type=int, default=2000)

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding synthetic reference data...")
        diagnosis_categories = [
            RawDiagnosisCategory.objects.update_or_create(
                diagnosis_category_code=code, defaults={"diagnosis_category_name": name}
            )[0]
            for code, name in DIAGNOSIS_CATEGORIES
        ]
        procedure_categories = [
            RawProcedureCategory.objects.update_or_create(
                procedure_category_code=code, defaults={"procedure_category_name": name}
            )[0]
            for code, name in PROCEDURE_CATEGORIES
        ]
        denial_codes = [
            RawDenialCode.objects.update_or_create(
                denial_code=code, defaults={"denial_reason": reason, "denial_category": category}
            )[0]
            for code, reason, category in DENIAL_CODES
        ]

        self.stdout.write(f"Seeding {options['payers']} payers...")
        payers = []
        for i in range(options["payers"]):
            payer_id = f"PAY-{100 + i}"
            payer, _ = RawPayer.objects.update_or_create(
                payer_id=payer_id,
                defaults={
                    "payer_name": f"{fake.company()} Health Plan",
                    "payer_type": random.choice(PAYER_TYPES),
                },
            )
            payers.append(payer)

        self.stdout.write(f"Seeding {options['providers']} providers...")
        providers = []
        for i in range(options["providers"]):
            provider_id = f"PRV-{20000 + i}"
            provider, _ = RawProvider.objects.update_or_create(
                provider_id=provider_id,
                defaults={
                    "provider_name": f"Dr. {fake.last_name()} {random.choice(['Clinic', 'Medical Group', 'Associates'])}",
                    "specialty": random.choice(SPECIALTIES),
                    "npi": fake.numerify("##########"),
                    "network_status": random.choices(["In-Network", "Out-of-Network"], weights=[85, 15])[0],
                    "address": f"{fake.street_address()}, {fake.city()}, {fake.state_abbr()}",
                    "phone": fake.numerify("###-###-####"),
                },
            )
            providers.append(provider)

        self.stdout.write(f"Seeding {options['members']} members...")
        members = []
        for i in range(options["members"]):
            member_id = f"MBR-{10000000 + i}"
            effective_date = date(2023, 1, 1) + timedelta(days=random.randint(0, 365))
            member, _ = RawMember.objects.update_or_create(
                member_id=member_id,
                defaults={
                    "subscriber_id": f"SUB-{10000000 + i}",
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "date_of_birth": fake.date_of_birth(minimum_age=1, maximum_age=90),
                    "gender": random.choice(["Female", "Male", "Other"]),
                    "address": f"{fake.street_address()}, {fake.city()}, {fake.state_abbr()}",
                    "phone": fake.numerify("###-###-####"),
                    "email": fake.free_email(),
                    "plan_type": random.choice(PLAN_TYPES),
                    "effective_date": effective_date,
                    "term_date": None,
                },
            )
            members.append(member)

            # Eligibility history: one or two coverage periods, sometimes
            # with an intentional gap for the data quality / gap check demo.
            coverage_start = effective_date
            coverage_end = coverage_start + timedelta(days=random.randint(150, 400))
            RawEligibility.objects.update_or_create(
                eligibility_id=f"ELG-{member_id}-1",
                defaults={
                    "member": member,
                    "coverage_start": coverage_start,
                    "coverage_end": coverage_end,
                    "plan_type": member.plan_type,
                    "status": "Active",
                },
            )
            if random.random() < 0.2:
                gap_days = random.randint(10, 60)
                next_start = coverage_end + timedelta(days=gap_days)
                RawEligibility.objects.update_or_create(
                    eligibility_id=f"ELG-{member_id}-2",
                    defaults={
                        "member": member,
                        "coverage_start": next_start,
                        "coverage_end": None,
                        "plan_type": member.plan_type,
                        "status": "Active",
                    },
                )

        self.stdout.write(f"Seeding {options['claims']} claims with service lines, payments, adjustments...")
        for i in range(options["claims"]):
            member = random.choice(members)
            provider = random.choice(providers)
            payer = random.choice(payers)
            diagnosis = random.choice(diagnosis_categories)

            service_start = date(2024, 1, 1) + timedelta(days=random.randint(0, 730))
            service_end = service_start + timedelta(days=random.randint(0, 2))
            submitted_date = service_end + timedelta(days=random.randint(1, 14))

            claim_status = random.choices(
                ["Paid", "Denied", "Pending", "Partially Paid"], weights=[60, 15, 10, 15]
            )[0]
            billed_amount = round(random.uniform(75, 4500), 2)
            is_denied = claim_status == "Denied"
            if is_denied:
                paid_amount = 0
            elif claim_status == "Pending":
                paid_amount = 0
            elif claim_status == "Partially Paid":
                paid_amount = round(billed_amount * random.uniform(0.3, 0.7), 2)
            else:
                paid_amount = round(billed_amount * random.uniform(0.7, 0.98), 2)

            claim_id = f"CLM-{service_start.year}-{100000 + i:06d}"
            claim = RawClaim.objects.create(
                claim_id=claim_id,
                member=member,
                provider=provider,
                payer=payer,
                claim_type=random.choice(CLAIM_TYPES),
                claim_status=claim_status,
                diagnosis_category=diagnosis,
                denial_code=random.choice(denial_codes) if is_denied else None,
                service_date_start=service_start,
                service_date_end=service_end,
                submitted_date=submitted_date,
                billed_amount=billed_amount,
                paid_amount=paid_amount,
            )

            num_lines = random.randint(1, 3)
            remaining_billed = billed_amount
            for line_no in range(1, num_lines + 1):
                procedure = random.choice(procedure_categories)
                line_billed = round(remaining_billed / (num_lines - line_no + 1), 2)
                remaining_billed -= line_billed
                line_allowed = round(line_billed * random.uniform(0.6, 0.95), 2)
                line_paid = round(line_billed * (float(paid_amount) / float(billed_amount)), 2) if billed_amount else 0
                RawClaimServiceLine.objects.create(
                    service_line_id=f"{claim_id}-L{line_no}",
                    claim=claim,
                    line_number=line_no,
                    procedure_category=procedure,
                    service_date=service_start,
                    units=random.randint(1, 3),
                    billed_amount=line_billed,
                    allowed_amount=line_allowed,
                    paid_amount=line_paid,
                )

            if paid_amount and float(paid_amount) > 0:
                RawPayment.objects.create(
                    payment_id=f"PAY-{service_start.year}-{100000 + i:06d}",
                    claim=claim,
                    payment_date=submitted_date + timedelta(days=random.randint(5, 45)),
                    payment_amount=paid_amount,
                    payment_method=random.choice(["EFT", "Check", "Virtual Card"]),
                )

            if claim_status in ("Paid", "Partially Paid") and random.random() < 0.4:
                adjustment_amount = round(float(billed_amount) - float(paid_amount), 2)
                if adjustment_amount > 0:
                    RawAdjustment.objects.create(
                        adjustment_id=f"ADJ-{claim_id}",
                        claim=claim,
                        adjustment_type=random.choice(["Contractual", "Write-off", "Coordination of Benefits"]),
                        adjustment_amount=adjustment_amount,
                        adjustment_date=submitted_date + timedelta(days=random.randint(5, 40)),
                        reason_code=random.choice(["CO-45", "CO-97", None]),
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(members)} members, {len(providers)} providers, {len(payers)} payers, "
            f"{options['claims']} claims. Synthetic data only -- no real PHI."
        ))
