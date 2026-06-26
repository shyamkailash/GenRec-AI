from django.urls import path
from .views import GenerateLabRecordView

urlpatterns = [
    path("generate/", GenerateLabRecordView.as_view(), name="generate-lab-record"),
]
