import pytest
import jarvis.memory as mem

def test_init_db():
    mem.init_db()

def test_add_and_retrieve_episode():
    mem.init_db()
    mem.add_episode("user", "test message for episode recall")
    eps = mem.get_recent_episodes(5)
    assert any("test message for episode recall" in e["content"] for e in eps)

def test_store_and_recall_memory():
    mem.init_db()
    mem.store_memory("Jarvis workspace is at ~/dev/jarvis")
    results = mem.recall_memories("where is jarvis")
    assert len(results) > 0
