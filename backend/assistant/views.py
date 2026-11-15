import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from rest_framework.permissions import IsAuthenticated
from dotenv import load_dotenv
from groq import Groq # <--- Use direct Groq client
from django.contrib.auth.models import User
from rest_framework import status

# LangChain for Upload only
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

VECTOR_STORE = None
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

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
            
            # Split text into manageable chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200) 
            chunks = text_splitter.split_documents(documents)

            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            VECTOR_STORE = FAISS.from_documents(chunks, embeddings)

            return Response({"message": "File processed successfully!"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)



import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)




class AskQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        global VECTOR_STORE
        question = request.data.get('question')

        if not VECTOR_STORE:
            return Response({"error": "Please upload a document first"}, status=400)

        try:
            # 1. Retrieve the most relevant chunks (we keep k=1 to save tokens)
            docs = VECTOR_STORE.similarity_search(question, k=1)
            raw_context = "\n\n".join([doc.page_content for doc in docs])
            
            # 2. Hard limit the context to 1500 characters (approx 350 tokens)
            context = raw_context[:1500] 

            # 3. Initialize ChatGroq but DO NOT use a chain (to avoid hidden streaming limits)
            llm = ChatGroq(
                temperature=0, 
                model_name="openai/gpt-oss-20b",
                max_tokens=500,
                streaming=False # 🔥 THIS IS THE CRUCIAL FIX
            )

            # 4. Construct the prompt manually
            prompt_text = f"""
            Answer the question based only on the following context:
            
            Context:
            {context}

            Question: {question}
            """

            # 5. Directly invoke the LLM (No chains, no hidden streaming)
            response = llm.invoke(prompt_text)
            
            return Response({"answer": response.content})
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)

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



class ClearMemoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        global VECTOR_STORE
        VECTOR_STORE = None # Reset the memory
        return Response({"message": "Memory cleared successfully"})
