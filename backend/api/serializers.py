from rest_framework import serializers

from experiments.models import Experiment


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
