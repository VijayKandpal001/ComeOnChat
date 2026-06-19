from pydantic import BaseModel, Field
from backend.rag import _THREAD_RETRIEVERS, _THREAD_METADATA
from backend.graph import checkpointer

def retrieve_threads():
    memory_threads= set()
    for chkpt in checkpointer.list(None):
        memory_threads.add(chkpt.config['configurable']['thread_id'])
    return list(memory_threads)

def thread_has_document(thread_id: str) -> bool:
    return str(thread_id) in _THREAD_RETRIEVERS

def thread_document_metadata(thread_id: str) -> dict:
    return _THREAD_METADATA.get(str(thread_id), {})
