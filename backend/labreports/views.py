from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services.ollama_service import generate_lab_record


class GenerateLabRecordView(APIView):
    def post(self, request):
        experiment_name = request.data.get("experiment_name", "")
        subject = request.data.get("subject", "")
        language = request.data.get("language", "")
        output_text = request.data.get("output_text", "")
        code_text = request.data.get("code_text", "")

        if not experiment_name or not subject:
            return Response(
                {"error": "experiment_name and subject are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lab_record = generate_lab_record(
                experiment_name=experiment_name,
                subject=subject,
                language=language,
                output_text=output_text,
                code_text=code_text
            )

            return Response(
                {
                    "message": "Lab record generated successfully",
                    "experiment_name": experiment_name,
                    "subject": subject,
                    "language": language,
                    "lab_record": lab_record
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
