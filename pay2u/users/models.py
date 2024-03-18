from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, phone, email, password):
        if not phone:
            raise ValueError("У пользователя должен быть номер телефона")
        if not email:
            raise ValueError("У пользователя должен быть email")
        user = self.model(
            phone=phone,
            email=self.normalize_email(email),
            password=password,
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, email, password=None):
        if password is None:
            raise ValueError("Пароль не может быть пустым")
        user = self.create_user(
            phone=phone,
            email=email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    phone = models.CharField("Номер телефона", max_length=20, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.phone


def increment_account_number():
    last_account = Account.objects.all().order_by('id').last()
    if not last_account:
        return 'AN000001'
    account_no = last_account.account_number
    account_int = int(account_no.split('AN')[-1])
    new_account_int = account_int + 1
    new_account_no = 'AN' + str(new_account_int).zfill(4)
    return new_account_no


class Account(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="accounts",
        null=False,
        blank=False,
        verbose_name="Пользователь",
    )
    balance = models.IntegerField(default=0, verbose_name="Баланс")
    account_number = models.CharField(
        default=increment_account_number,
        max_length=20,
        unique=True,
        verbose_name="Номер счёта",
    )

    class Meta:
        verbose_name = "Счёт"
        verbose_name_plural = "Счета"

    def __str__(self):
        return self.account_number
