from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    """
    部門
    """

    name = models.CharField("部門名稱", max_length=32)

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    職級
    """

    name = models.CharField("職級名稱", max_length=32)
    is_supervisor = models.BooleanField("是否為主管", default=False)

    def __str__(self):
        return f"{self.name}"


class User(AbstractUser):
    """
    使用者
    """

    class SexChoices(models.TextChoices):
        MALE = "M", "男"
        FEMALE = "F", "女"

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name="所屬部門",
        null=True,
        blank=True,
    )
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, verbose_name="職級", blank=True
    )
    gender = models.CharField(
        "性別", max_length=10, choices=SexChoices.choices, null=True, blank=True
    )

    def __str__(self):
        return f"{self.username} ({str(self.department)}) {str(self.role)}"
