from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom user manager
    """
    def create_user(
            self,
            first_name,
            last_name,
            email,
            password,
            **extra_fields):
        if not email or not first_name or not last_name:
            raise ValueError("This field must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
            self,
            first_name,
            last_name,
            email,
            password,
            **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            first_name,
            last_name,
            email,
            password,
            **extra_fields
        )
