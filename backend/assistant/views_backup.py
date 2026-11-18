import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import HttpResponse
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Simplified memory for Render Free Tier
VECTOR_STORE = None

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Please provide both username and password"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(username=username, password=password)
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)


class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "https://frontend-six-omega-ig9gta7f.vercel.app"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return response

    def post(self, request, *args, **kwargs):
        global VECTOR_STORE
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=400)

        file_path = default_storage.save('pdfs/' + file_obj.name, file_obj)
        full_path = default_storage.path(file_path)

        try:
            loader = PyPDFLoader(full_path)
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50) 
            chunks = text_splitter.split_documents(documents)

            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            VECTOR_STORE = FAISS.from_documents(chunks, embeddings)

            return Response({"message": "File processed successfully!"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class AskQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "https://frontend-six-omega-ig9gta7f.vercel.app"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return response

    def post(self, request, *args, **kwargs):
        global VECTOR_STORE
        question = request.data.get('question')

        if not VECTOR_STORE:
            return Response({"error": "Please upload a document first"}, status=400)

        try:
            docs = VECTOR_STORE.similarity_search(question, k=1)
            raw_context = "\n\n".join([doc.page_content for doc in docs])
            context = raw_context[:800] 

            llm = ChatGroq(
                temperature=0, 
                model_name="openai/gpt-oss-20b",
                max_tokens=300 
            )

            prompt = ChatPromptTemplate.from_template("""
            Answer the question based only on this context:
            {context}

            Question: {question}
            """)

            chain = prompt | llm | StrOutputParser()
            answer = chain.invoke({"context": context, "question": question})
            
            return Response({"answer": answer})
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class ClearMemoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        global VECTOR_STORE
        VECTOR_STORE = None
        return Response({"message": "Memory cleared successfully"})
