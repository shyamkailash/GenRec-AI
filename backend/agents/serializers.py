"""API serializers for agent orchestration requests."""

from rest_framework import serializers


class PlannerRequestSerializer(serializers.Serializer):
    """Validate requests to generate an experiment workflow plan."""

    experiment_id = serializers.IntegerField(min_value=1)
