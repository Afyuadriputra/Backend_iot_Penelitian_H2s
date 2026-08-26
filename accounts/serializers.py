from django.contrib.auth import (
    authenticate,
    get_user_model,
)

from django.db import transaction

from exposure.services.inhalation import (
    UnsupportedInhalationMethodologyError,
    resolve_inhalation_methodology,
    sync_worker_exposure_inhalation_rate,
)

from devices.serializers import (
    DeviceSerializer,
    H2SReadingSerializer,
)

from django.contrib.auth.password_validation import (
    validate_password,
)
from rest_framework import serializers

from accounts.models import AccountProfile
from accounts.services import create_account
from exposure.models import (
    ExposureProfile,
    Worker,
)
from exposure.services.validation import (
    ExposureValidationError,
    validate_exposure_data,
)


User = get_user_model()


class AccountProfileSerializer(
    serializers.ModelSerializer
):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    worker_code = serializers.CharField(
        source="worker.code",
        read_only=True,
        allow_null=True,
    )

    worker_name = serializers.CharField(
        source="worker.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = AccountProfile

        fields = [
            "id",
            "username",
            "email",
            "role",
            "worker",
            "worker_code",
            "worker_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


class AccountCreateSerializer(
    serializers.Serializer
):
    username = serializers.CharField(
        max_length=150,
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        default="",
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    role = serializers.ChoiceField(
        choices=AccountProfile.Role.choices,
    )

    worker_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    def validate_username(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Username cannot be blank."
            )

        if User.objects.filter(
            username=value
        ).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        role = attrs["role"]
        worker_id = attrs.get(
            "worker_id"
        )

        if (
            role
            == AccountProfile.Role.WORKER
            and worker_id is None
        ):
            raise serializers.ValidationError(
                {
                    "worker_id": (
                        "WORKER role requires "
                        "worker_id."
                    )
                }
            )

        if (
            role
            != AccountProfile.Role.WORKER
            and worker_id is not None
        ):
            raise serializers.ValidationError(
                {
                    "worker_id": (
                        "worker_id is only valid "
                        "for WORKER role."
                    )
                }
            )

        if worker_id is not None:
            try:
                worker = Worker.objects.get(
                    pk=worker_id,
                    is_active=True,
                )
            except Worker.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {
                        "worker_id": (
                            "Active Worker not found."
                        )
                    }
                ) from exc

            if AccountProfile.objects.filter(
                worker=worker
            ).exists():
                raise serializers.ValidationError(
                    {
                        "worker_id": (
                            "Worker is already linked "
                            "to an account."
                        )
                    }
                )

            attrs["worker"] = worker

        return attrs

    def create(self, validated_data):
        validated_data.pop(
            "worker_id",
            None,
        )

        result = create_account(
            username=validated_data[
                "username"
            ],
            password=validated_data[
                "password"
            ],
            email=validated_data.get(
                "email",
                "",
            ),
            role=validated_data[
                "role"
            ],
            worker=validated_data.get(
                "worker"
            ),
        )

        return result.profile


class LoginSerializer(
    serializers.Serializer
):
    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get(
                "request"
            ),
            username=attrs["username"],
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "User account is inactive."
            )

        attrs["user"] = user

        return attrs


class CurrentUserSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()

    username = serializers.CharField()

    email = serializers.EmailField(
        allow_blank=True,
    )

    role = serializers.CharField()

    worker_id = serializers.IntegerField(
        allow_null=True,
    )

    worker_code = serializers.CharField(
        allow_null=True,
    )

    worker_name = serializers.CharField(
        allow_null=True,
    )


class LoginResponseSerializer(
    serializers.Serializer
):
    token = serializers.CharField()

    user = CurrentUserSerializer()

class MyWorkerProfileSerializer(
    serializers.ModelSerializer
):
    name = serializers.CharField(
        required=False,
        allow_blank=False,
        allow_null=False,
        max_length=150,
    )

    age = serializers.IntegerField(
        required=False,
        allow_null=False,
        min_value=1,
        max_value=120,
    )

    monitoring_device_code = (
        serializers.CharField(
            source=(
                "monitoring_device.device_code"
            ),
            read_only=True,
            allow_null=True,
        )
    )

    monitoring_device_name = (
        serializers.CharField(
            source="monitoring_device.name",
            read_only=True,
            allow_null=True,
        )
    )

    monitoring_device_location = (
        serializers.CharField(
            source="monitoring_device.location",
            read_only=True,
            allow_null=True,
        )
    )

    class Meta:
        model = Worker

        fields = [
            "id",
            "code",
            "name",
            "age",
            "is_active",
            "monitoring_device_code",
            "monitoring_device_name",
            "monitoring_device_location",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "code",
            "is_active",
            "monitoring_device_code",
            "monitoring_device_name",
            "monitoring_device_location",
            "created_at",
            "updated_at",
        ]

    def validate_name(
        self,
        value,
    ):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Name cannot be blank."
            )

        return value

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        previous_age = (
            instance.age
        )

        worker = super().update(
            instance,
            validated_data,
        )

        age_changed = (
            "age" in validated_data
            and worker.age != previous_age
        )

        if age_changed:
            try:
                sync_worker_exposure_inhalation_rate(
                    worker
                )

            except (
                UnsupportedInhalationMethodologyError
            ) as exc:
                raise serializers.ValidationError(
                    {
                        "age": str(exc),
                    }
                ) from exc

        return worker

class MyExposureProfileSerializer(
    serializers.ModelSerializer
):
    worker_code = serializers.CharField(
        source="worker.code",
        read_only=True,
    )

    worker_name = serializers.CharField(
        source="worker.name",
        read_only=True,
        allow_null=True,
    )

    inhalation_rate = (
        serializers.FloatField(
            read_only=True,
        )
    )

    inhalation_category = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = ExposureProfile

        fields = [
            "id",
            "worker_code",
            "worker_name",
            "body_weight",
            "exposure_time",
            "exposure_frequency",
            "exposure_duration",
            "inhalation_rate",
            "inhalation_category",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "worker_code",
            "worker_name",
            "inhalation_rate",
            "inhalation_category",
            "created_at",
            "updated_at",
        ]

    def get_inhalation_category(
        self,
        obj,
    ):
        if obj.worker.age is None:
            return None

        try:
            methodology = (
                resolve_inhalation_methodology(
                    obj.worker.age
                )
            )

        except (
            UnsupportedInhalationMethodologyError
        ):
            return None

        return methodology.category

    def validate(
        self,
        attrs,
    ):
        instance = self.instance

        if instance is None:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Personal exposure profile "
                        "must already exist."
                    )
                }
            )

        values = {
            "body_weight": attrs.get(
                "body_weight",
                instance.body_weight,
            ),

            "exposure_time": attrs.get(
                "exposure_time",
                instance.exposure_time,
            ),

            "exposure_frequency": attrs.get(
                "exposure_frequency",
                instance.exposure_frequency,
            ),

            "exposure_duration": attrs.get(
                "exposure_duration",
                instance.exposure_duration,
            ),

            "inhalation_rate": (
                instance.inhalation_rate
            ),
        }

        try:
            validate_exposure_data(
                **values
            )

        except ExposureValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": str(exc),
                }
            ) from exc

        return attrs

    
class MyMonitoringSerializer(
    serializers.Serializer
):
    device = DeviceSerializer(
        read_only=True,
    )

    reading = H2SReadingSerializer(
        read_only=True,
        allow_null=True,
    )