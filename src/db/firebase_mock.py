import logging
from typing import Dict, Any
from unittest.mock import MagicMock

class FirebaseMock:
    def __init__(self):
        self._mock_data: Dict[str, Dict[str, Any]] = {}
        logging.info("Firebase mock initialized with in-memory storage")

    def collection(self, collection_name: str) -> MagicMock:
        collection_mock = MagicMock()
        collection_mock.name = collection_name
        
        if collection_name not in self._mock_data:
            self._mock_data[collection_name] = {}
        
        # Simulate document references
        def mock_document(document_id: str) -> MagicMock:
            doc_mock = MagicMock()
            doc_mock.id = document_id
            
            # Simulate document operations
            def mock_get():
                doc_data = self._mock_data[collection_name].get(document_id, {})
                return MagicMock(exists=bool(doc_data), to_dict=lambda: doc_data)
            
            def mock_set(data: Dict[str, Any]):
                self._mock_data[collection_name][document_id] = data
                return None
            
            def mock_update(data: Dict[str, Any]):
                if document_id in self._mock_data[collection_name]:
                    self._mock_data[collection_name][document_id].update(data)
                return None
            
            def mock_delete():
                if document_id in self._mock_data[collection_name]:
                    del self._mock_data[collection_name][document_id]
                return None
            
            doc_mock.get = mock_get
            doc_mock.set = mock_set
            doc_mock.update = mock_update
            doc_mock.delete = mock_delete
            
            return doc_mock
        
        collection_mock.document = mock_document
        
        # Simulate collection operations
        def mock_add(data: Dict[str, Any]):
            doc_id = f"mock-id-{len(self._mock_data[collection_name])}"
            self._mock_data[collection_name][doc_id] = data
            return None, doc_id
        
        def mock_get():
            return [MagicMock(id=doc_id, to_dict=lambda: data) 
                   for doc_id, data in self._mock_data[collection_name].items()]
        
        collection_mock.add = mock_add
        collection_mock.get = mock_get
        
        return collection_mock 