import os
import logging
import requests

from dotenv import load_dotenv

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.core.files.storage import default_storage
from django.contrib.auth.models import User

from langchain_core.embeddings import Embeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

logger = logging.getLogger(__name__)

# API configuration
JINA_API_KEY = os.environ.get("JINA_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

JINA_API_URL = "https://api.jina.ai/v1/embeddings"
JINA_MODEL = "jina-embeddings-v3"

# Temporary document memory
VECTOR_STORE = None


# Custom Jina Embeddings implementation
class JinaEmbeddings(Embeddings):

    def __init__(self):
        if not JINA_API_KEY:
            raise ValueError("JINA_API_KEY is missing")

        self.api_key = JINA_API_KEY

    def _get_embeddings(self, texts, task):

        all_embeddings = []
        batch_size = 16

        for start in range(0, len(texts), batch_size):

            batch = texts[start:start + batch_size]

            payload = {
                "model": JINA_MODEL,
                "task": task,
                "input": batch,
                "normalized": True
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                JINA_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()

            result = response.json()

            data = sorted(
                result["data"],
                key=lambda item: item["index"]
            )

            all_embeddings.extend(
                item["embedding"] for item in data
            )

        if len(all_embeddings) != len(texts):
            raise ValueError("Jina returned an unexpected number of embeddings")

        return all_embeddings

    def embed_documents(self, texts):
        return self._get_embeddings(
            texts,
            "retrieval.passage"
        )

    def embed_query(self, text):
        result = self._get_embeddings(
            [text],
            "retrieval.query"
        )
        return result[0]


# User registration
class RegisterView(APIView):

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Please provide both username and password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        User.objects.create_user(
            username=username,
            password=password
        )

        return Response(
            {"message": "User created successfully"},
            status=status.HTTP_201_CREATED
        )


# PDF upload
class UploadPDFView(APIView):

    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.warning("UPLOAD POST REQUEST RECEIVED")

        global VECTOR_STORE

        file_obj = request.FILES.get("file")

        if not file_obj:
            return Response(
                {"error": "No file uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not file_obj.name.lower().endswith(".pdf"):
            return Response(
                {"error": "Please upload a PDF file"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if file_obj.size > 10 * 1024 * 1024:
            return Response(
                {"error": "PDF size must be 10 MB or less"},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_path = None

        try:

            file_path = default_storage.save(
                "pdfs/" + file_obj.name,
                file_obj
            )

            full_path = default_storage.path(file_path)

            loader = PyPDFLoader(full_path)
            documents = loader.load()

            if not documents:
                return Response(
                    {"error": "No readable pages found in PDF"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )

            chunks = text_splitter.split_documents(documents)

            if not chunks:
                return Response(
                    {"error": "No extractable text found in PDF"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            embeddings = JinaEmbeddings()

            VECTOR_STORE = FAISS.from_documents(
                chunks,
                embeddings
            )

            return Response({
                "message": "File processed successfully!",
                "chunks": len(chunks)
            })

        except Exception as e:

            logger.exception("PDF upload failed")

            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:

            if file_path:
                try:
                    default_storage.delete(file_path)
                except Exception:
                    logger.warning("Could not delete temporary PDF file")


# Ask questions
class AskQuestionView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        global VECTOR_STORE

        question = request.data.get("question")

        if not question:
            return Response(
                {"error": "Please enter a question"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if VECTOR_STORE is None:
            return Response(
                {"error": "Please upload a document first"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not GROQ_API_KEY:
            return Response(
                {"error": "GROQ_API_KEY is missing"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:

            docs = VECTOR_STORE.similarity_search(
                question,
                k=2
            )

            context = "\n\n".join(
                doc.page_content for doc in docs
            )

            llm = ChatGroq(
                temperature=0,
                model_name="openai/gpt-oss-20b",
                max_tokens=300,
                api_key=GROQ_API_KEY
            )

            prompt = ChatPromptTemplate.from_template("""
            Answer the question based only on the following context.

            If the answer is not available in the context,
            clearly say that you cannot find the answer in the document.

            Context:
            {context}

            Question:
            {question}
            """)

            chain = prompt | llm | StrOutputParser()

            answer = chain.invoke({
                "context": context,
                "question": question
            })

            return Response({
                "answer": answer
            })

        except Exception as e:

            logger.exception("Question answering failed")

            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Clear document memory
class ClearMemoryView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        global VECTOR_STORE

        VECTOR_STORE = None

        return Response({
            "message": "Memory cleared successfully"
        })

