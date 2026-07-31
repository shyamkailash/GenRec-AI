"""Unit tests for the ChromaDB vector-store adapter."""

from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from .services.vector_store import RAGServiceError, semantic_search


class SemanticSearchTests(SimpleTestCase):
    def test_rejects_empty_query(self):
        with self.assertRaisesMessage(RAGServiceError, "cannot be empty"):
            semantic_search("  ")

    def test_rejects_invalid_limit(self):
        for invalid_limit in (0, 21):
            with self.subTest(limit=invalid_limit):
                with self.assertRaisesMessage(RAGServiceError, "between 1 and 20"):
                    semantic_search("sorting", limit=invalid_limit)

    @patch("rag.services.vector_store.get_embedding_model")
    @patch("rag.services.vector_store.get_collection")
    def test_transforms_chroma_results(self, get_collection, get_model):
        collection = Mock()
        collection.count.return_value = 1
        collection.query.return_value = {
            "documents": [["Bubble sort compares adjacent values."]],
            "metadatas": [[{"document_id": 1, "filename": "manual.pdf"}]],
            "distances": [[0.1]],
        }
        get_collection.return_value = collection
        get_model.return_value.encode.return_value = [[0.2, 0.3]]

        results = semantic_search("bubble sort")

        self.assertEqual(results[0]["text"], "Bubble sort compares adjacent values.")
        self.assertEqual(results[0]["metadata"]["document_id"], 1)
        self.assertEqual(results[0]["distance"], 0.1)
        self.assertAlmostEqual(results[0]["similarity"], 0.9)

    @patch("rag.services.vector_store.get_embedding_model")
    @patch("rag.services.vector_store.get_collection")
    def test_filters_by_experiment(self, get_collection, get_model):
        collection = Mock()
        collection.count.return_value = 2
        collection.query.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }
        get_collection.return_value = collection
        get_model.return_value.encode.return_value = [[0.2, 0.3]]

        semantic_search("stack", experiment_id=7)

        self.assertEqual(collection.query.call_args.kwargs["where"], {"experiment_id": 7})

    @patch("rag.services.vector_store.get_collection")
    def test_empty_collection_returns_empty_list(self, get_collection):
        get_collection.return_value.count.return_value = 0

        self.assertEqual(semantic_search("queue"), [])
