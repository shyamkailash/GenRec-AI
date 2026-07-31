"""REST endpoints for agent workflow orchestration."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from experiments.models import Experiment

from .serializers import PlannerRequestSerializer
from .services import PlannerAgent, PlannerError


class PlannerAPIView(APIView):
    """Return the ordered agent workflow for an existing experiment."""

    planner_class = PlannerAgent

    def post(self, request):
        serializer = PlannerRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        experiment = get_object_or_404(
            Experiment.objects.prefetch_related("documents"),
            pk=serializer.validated_data["experiment_id"],
        )

        try:
            plan = self.planner_class().plan(experiment)
        except PlannerError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(plan.to_dict(), status=status.HTTP_200_OK)
