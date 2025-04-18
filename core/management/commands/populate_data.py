import logging
import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import lorem_ipsum, timezone

from api.models import LeaveCategory, RoleLeavePolicy, UserLeaveBalance
from core.models import Department, Role, User

logger = logging.getLogger("commands_logger")

DEPARTMENTS = ["人資部", "財務部", "業務部", "技術部"]
ROLES = [
    ("員工", False),
    ("主管", True),
]
WORK_HOURS = 8


class Command(BaseCommand):
    help = "Populate the database with initial data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--empty",
            action="store_true",
            help="Empty the database before populating",
        )

    def handle(self, *args, **kwargs):
        if kwargs["empty"]:
            User.objects.all().delete()
            Department.objects.all().delete()
            Role.objects.all().delete()
            LeaveCategory.objects.all().delete()
            RoleLeavePolicy.objects.all().delete()
            UserLeaveBalance.objects.all().delete()
            logger.info("Database emptied.")
            return

        self.populate_core_app_models()
        self.populate_api_app_models()

    def populate_core_app_models(self):
        with transaction.atomic():
            # Populate Department
            for dept in DEPARTMENTS:
                department, created = Department.objects.get_or_create(name=dept)
                if created:
                    logger.info(f"Created department: {department.name}")

            # Populate Role
            for role_name, is_supervisor in ROLES:
                role, created = Role.objects.get_or_create(
                    name=role_name, is_supervisor=is_supervisor
                )
                if created:
                    logger.info(f"Created role: {str(role)}")

            # Populate User
            for is_supervisor in [False, True]:
                for dept in Department.objects.all():
                    if User.objects.filter(
                        role__is_supervisor=is_supervisor, department=dept
                    ).exists():
                        continue

                    first_name, last_name = lorem_ipsum.words(2, common=False).split()
                    username = f"{last_name}{random.randint(1, 1000):03}"

                    user_kwargs = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": f"{username}@localhost",
                        "department": dept,
                        "role": Role.objects.get(is_supervisor=is_supervisor),
                        "gender": lambda: random.choice(User.SexChoices.values),
                    }

                    user, created = User.objects.get_or_create(
                        username=username, defaults=user_kwargs
                    )
                    if created:
                        user.set_password("password")
                        user.save()
                        logger.info(f"Created user: {user.username}")

            logger.info("Using default password: 'password' to login.")

            # Populate django admin superuser
            try:
                User.objects.get(username="admin")
            except User.DoesNotExist:
                User.objects.create_superuser(
                    username="admin",
                    password="adminpassword",
                    email="admin@localhost",
                )

    def populate_api_app_models(self):
        with transaction.atomic():
            # Populate LeaveCategory
            leave_categories = [
                {
                    "name": "事假",
                    "reset_policy": LeaveCategory.ResetPolicyChoices.MONTHLY,
                },
                {
                    "name": "病假",
                    "reset_policy": LeaveCategory.ResetPolicyChoices.MONTHLY,
                },
                {
                    "name": "生理假",
                    "reset_policy": LeaveCategory.ResetPolicyChoices.MONTHLY,
                },
                {
                    "name": "特休",
                    "reset_policy": LeaveCategory.ResetPolicyChoices.YEARLY,
                },
                {
                    "name": "魔物獵人荒野假",
                    "reset_policy": LeaveCategory.ResetPolicyChoices.NONE,
                    "effective_start_date": timezone.datetime(2025, 2, 28).date(),
                    "effective_end_date": timezone.datetime(2025, 4, 30).date(),
                },
            ]

            for category in leave_categories:
                leave_category, created = LeaveCategory.objects.get_or_create(
                    name=category["name"],
                    defaults=category,
                )

                if created:
                    logger.info(f"Created leave category: {leave_category.name}")

            # Populate RoleLeavePolicy
            for role in Role.objects.all():
                for category in LeaveCategory.objects.all():
                    if RoleLeavePolicy.objects.filter(
                        role=role, category=category
                    ).exists():
                        continue

                    default_amount = random.randint(1, 10)

                    if role.is_supervisor and category.name == "特休":
                        default_amount = random.randint(5, 15)
                    elif category.name == "魔物獵人荒野假":
                        default_amount = 5
                    elif category.name == "生理假":
                        default_amount = 1

                    if role.is_supervisor:
                        default_amount += 2

                    role_leave_policy, created = RoleLeavePolicy.objects.get_or_create(
                        role=role,
                        category=category,
                        defaults={"default_amount": default_amount},
                    )

                    if created:
                        logger.info(
                            f"Created role leave policy: {role_leave_policy.role} - {role_leave_policy.category} ({role_leave_policy.default_amount})"
                        )

            # Populate UserLeaveBalance
            for user in User.objects.filter(
                department__isnull=False, role__isnull=False
            ):
                for category in LeaveCategory.objects.all():
                    if UserLeaveBalance.objects.filter(
                        user=user, category=category
                    ).exists():
                        continue

                    try:
                        role_leave_policy = RoleLeavePolicy.objects.get(
                            role=user.role, category=category
                        )
                    except RoleLeavePolicy.DoesNotExist as e:
                        logger.warning(
                            f"RoleLeavePolicy not found for role: {user.role}, category: {category}"
                        )
                        continue

                    default_amount = role_leave_policy.default_amount

                    if (
                        category.name == "生理假"
                        and user.gender == User.SexChoices.MALE
                    ):
                        default_amount = 0

                    if default_amount > 0:
                        if random.random() < 0.5:
                            default_amount //= random.randint(2, 3)

                    default_amount *= WORK_HOURS

                    user_leave_balance, created = (
                        UserLeaveBalance.objects.get_or_create(
                            user=user,
                            category=category,
                            defaults={"remaining_amount": default_amount},
                        )
                    )

                    if created:
                        logger.info(
                            f"Created user leave balance: {user_leave_balance.user} - {user_leave_balance.category} ({user_leave_balance.remaining_amount})"
                        )

            # TODO: need to implement later
            # change all is_supervisor users to is_staff in User model
            User.objects.filter(role__is_supervisor=True).update(is_staff=True)
