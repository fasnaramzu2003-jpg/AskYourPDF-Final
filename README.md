
📄 AskYourPDF – AI-Powered PDF Question Answering

AskYourPDF is a Full-Stack Generative AI web application that allows users to upload PDF documents and ask questions about their content. It uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from documents and generate context-based answers using an LLM.

🚀 Live Demo

Live Application: https://askyourpdf-final.vercel.app/

GitHub Repository: https://github.com/fasnaramzu2003-jpg/AskYourPDF-Final

✨ Features

- User Authentication: Secure user registration and login.
- PDF Upload: Upload PDF documents through an interactive interface.
- Document Processing: Extract and split PDF content into smaller text chunks.
- Vector Embeddings: Generate document embeddings using Jina AI.
- Similarity Search: Retrieve relevant document content using FAISS.
- AI-Powered Question Answering: Ask questions and receive contextual answers using Groq LLM.
- RAG Architecture: Generate answers based on retrieved document information.

🛠️ Technology Stack

Category| Technologies
Frontend| React.js, JavaScript, HTML5, CSS3
Backend| Python, Django, Django REST Framework
AI Framework| LangChain
Embeddings| Jina AI ("jina-embeddings-v3")
Vector Database| FAISS
LLM| Groq API
Authentication| JWT
Deployment| Vercel, Render

🧠 How It Works

AskYourPDF follows a Retrieval-Augmented Generation (RAG) workflow.

1. PDF Upload: The user uploads a PDF document.
2. Text Extraction: The backend extracts text from the PDF.
3. Text Chunking: Extracted content is divided into smaller chunks.
4. Embedding Generation: Jina AI converts text chunks into vector embeddings.
5. Vector Storage: FAISS stores the embeddings for similarity search.
6. Question Processing: The user's question is converted into an embedding.
7. Context Retrieval: FAISS retrieves relevant document chunks.
8. Answer Generation: Groq LLM generates an answer using the retrieved context.

🏗️ Project Architecture

AskYourPDF/
│
├── backend/
│ ├── assistant/
│ │ ├── views.py
│ │ ├── urls.py
│ │ └── models.py
│ │
│ ├── config/
│ │ ├── settings.py
│ │ └── urls.py
│ │
│ └── requirements.txt
│
├── frontend/
│ ├── src/
│ ├── public/
│ ├── package.json
│ └── .env
│
└── README.md

⚙️ Installation and Setup

Prerequisites

- Python 3.10+
- Node.js and npm
- Git
- Jina AI API key
- Groq API key

1. Clone the Repository

git clone https://github.com/fasnaramzu2003-jpg/AskYourPDF-Final.git

cd AskYourPDF-Final

2. Backend Setup

cd backend

python -m venv venv

Activate the virtual environment.

Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Create a ".env" file inside the backend folder and configure:

SECRET_KEY=your_django_secret_key
DEBUG=True
GROQ_API_KEY=your_groq_api_key
JINA_API_KEY=your_jina_api_key

Configure your database and other Django environment settings as required.

Run migrations:

python manage.py migrate

Start the backend server:

python manage.py runserver

Backend runs at:

"http://127.0.0.1:8000/"

3. Frontend Setup

Open another terminal:

cd frontend

Install dependencies:

npm install

Create a frontend ".env" file:

VITE_API_URL=http://127.0.0.1:8000

Start the frontend:

npm run dev

Open the local URL displayed in your terminal.

🔐 Environment Variables

Variable| Purpose
SECRET_KEY| Django security key
DEBUG| Django debug setting
GROQ_API_KEY| Groq API authentication
JINA_API_KEY| Jina embeddings API authentication
DATABASE_URL| Database connection, when configured
VITE_API_URL| Backend API base URL

Important: Never upload ".env" files, passwords, secret keys, or API keys to GitHub.

☁️ Deployment

The application is deployed using:

- Frontend: Vercel
- Backend: Render

The React frontend communicates with the Django REST API hosted on Render.

📚 What I Learned

Through this project, I gained practical experience in:

- Full-Stack Web Application Development
- REST API Development and Integration
- Generative AI and Large Language Models
- Retrieval-Augmented Generation (RAG)
- Vector Embeddings and Similarity Search
- PDF Processing and Document Retrieval
- Cloud Deployment and Environment Configuration

🔮 Future Improvements

- Persistent vector storage
- Support for multiple PDF documents
- Improved handling of large documents
- Better support for scanned PDFs and document images
- Conversation history and document management

👩‍💻 Author

Fasna Fathima

Computer Science and Engineering Graduate

Interested in Full-Stack Development and Generative AI.

GitHub: https://github.com/fasnaramzu2003-jpg
                                                                                                                                
---

⭐ If you find this project interesting, feel free to explore the repository and share your feedback!
                                                                                                                                               
