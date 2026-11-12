
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions
)
from core.rag_engine import build_rag_chain, ask_question


load_dotenv()


def run_pipeline(source: str, language: str = "english", progress_callback=None) -> dict:

    def update_progress(percent, message):
        print(message)
        if progress_callback:
            progress_callback(percent, message)

    update_progress(5, "Preparing your source...")

    # Step 1: Process video/audio
    chunks = process_input(source)
    update_progress(22, "Audio extracted and ready.")

    # Step 2: Generate transcript
    transcript = transcribe_all(chunks, language)
    update_progress(48, "Transcription completed.")

    if not transcript.strip():
        raise ValueError("Transcription is empty. Cannot continue.")

    print(f"Raw transcription (first 300 characters): {transcript[:300]}")

    # Step 3: Generate meeting title
    title = generate_title(transcript)
    update_progress(56, "Generated session title.")

    # Step 4: Generate meeting summary
    summary = summarize(transcript)
    update_progress(66, "Created the executive summary.")

    # Step 5: Extract action items
    action_items = extract_action_items(transcript)
    update_progress(74, "Extracted action items.")

    # Step 6: Extract key decisions
    decisions = extract_key_decisions(transcript)
    update_progress(81, "Identified key decisions.")

    # Step 7: Extract open questions
    questions = extract_questions(transcript)
    update_progress(87, "Collected open questions.")

    # Step 8: Build RAG pipeline
    rag_chain = build_rag_chain(transcript)
    update_progress(97, "Built the searchable RAG knowledge base.")

    update_progress(100, "Your analysis is ready!")

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


# CLI Entry Point
if __name__ == "__main__":

    source = input("Enter YouTube URL or local file path: ").strip()

    language = input("Language (english/hinglish): ").strip().lower() or "english"

    result = run_pipeline(source, language)

    print("\n" + "=" * 60)
    print(f"Title: {result['title']}")
    print(f"\nSUMMARY:\n{result['summary']}")
    print(f"\nACTION ITEMS:\n{result['action_items']}")
    print(f"\nKEY DECISIONS:\n{result['key_decisions']}")
    print(f"\nOPEN QUESTIONS:\n{result['open_questions']}")
    print("=" * 60)

    # Phase 2: Chat with meeting using RAG
    print("\nChat with your meeting (type 'exit' to quit)\n")

    rag_chain = result["rag_chain"]

    while True:

        question = input("You: ").strip()

        if question.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        if not question:
            continue

        answer = ask_question(rag_chain, question)

        print(f"\nAssistant: {answer}\n")
