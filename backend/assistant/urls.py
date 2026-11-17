from django.urls import path
from .views import (
    UploadPDFView,
    AskQuestionView,
    RegisterView,
    ClearMemoryView
)

urlpatterns = [
    path('upload/', UploadPDFView.as_view(), name='upload_pdf'),
    path('ask/', AskQuestionView.as_view(), name='ask_question'),
    path('register/', RegisterView.as_view(), name='register'),
    path('clear/', ClearMemoryView.as_view(), name='clear_memory'),
]
