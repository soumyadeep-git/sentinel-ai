from .celery_app import celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import weaviate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from .database_models import Investigation, TaskStatus

# --- Database Setup for Worker ---
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Weaviate Client Setup ---
weaviate_client = weaviate.Client(
    url=f"http://{os.getenv('WEAVIATE_HOST')}:{os.getenv('WEAVIATE_PORT')}",
    additional_headers={"X-Google-Api-Key": os.getenv("GOOGLE_API_KEY")},
)

# --- LangChain Setup with Gemini ---
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0, convert_system_message_to_human=True)

def perform_rag_search(query: str) -> str:
    """Performs a vector search in Weaviate to find relevant log entries."""
    print(f"Performing RAG search for query: '{query}'")
    
    response = (
        weaviate_client.query
        .get("LogEntry", ["content", "ip_address", "timestamp"])
        .with_near_text({"concepts": [query]})
        .with_limit(15)
        .do()
    )
    
    results = response.get('data', {}).get('Get', {}).get('LogEntry', [])
    if not results:
        return "No relevant log entries found."
        
    formatted_results = "\n".join([f"- {res['content']} (IP: {res['ip_address']})" for res in results])
    print(f"Found {len(results)} relevant logs.")
    return formatted_results

@celery.task(name="app.tasks.run_investigation")
def run_investigation(investigation_id: int):
    """The main Celery task orchestrating the RAG and synthesis steps."""
    db = SessionLocal()
    investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not investigation:
        print(f"FATAL: Investigation {investigation_id} not found.")
        return

    try:
        print(f"Starting investigation {investigation_id} for query: '{investigation.query}'")
        investigation.status = TaskStatus.IN_PROGRESS
        db.commit()

        log_context = perform_rag_search(investigation.query)

        prompt_template = ChatPromptTemplate.from_template(
            """You are a senior SOC analyst. Your task is to analyze the following log entries and provide a concise summary for a security incident report.
            Based on the user's query and the retrieved logs, answer the query and summarize the key findings. Be direct and factual.

            USER QUERY: "{query}"

            RETRIEVED LOGS:
            {log_context}

            SUMMARY:
            """
        )
        chain = prompt_template | llm | StrOutputParser()
        
        print("Synthesizing results with Gemini...")
        summary = chain.invoke({
            "query": investigation.query,
            "log_context": log_context
        })
        print(f"Generated summary: {summary}")

        investigation.summary = summary
        investigation.status = TaskStatus.COMPLETED
        db.commit()
        print(f"Investigation {investigation_id} completed successfully.")

    except Exception as e:
        print(f"Investigation {investigation_id} failed. Error: {e}")
        investigation.status = TaskStatus.FAILED
        investigation.summary = f"An error occurred during analysis: {str(e)}"
        db.commit()
    finally:
        db.close()