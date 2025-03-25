import logging
from typing import Dict, Any, List
from unittest.mock import MagicMock

class FirebaseMock:
    def __init__(self):
        self._mock_data: Dict[str, Dict[str, Any]] = {}
        self._chat_history: Dict[str, List[Dict[str, Any]]] = {}  # Armazenamento dedicado para histórico de chat
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

            # Simulate subcollection for messages
            def mock_collection(subcollection_name: str) -> MagicMock:
                if subcollection_name == "messages":
                    subcollection_mock = MagicMock()
                    
                    def mock_add(message_data: Dict[str, Any]):
                        # Adiciona a mensagem ao histórico do chat
                        if document_id not in self._chat_history:
                            self._chat_history[document_id] = []
                        self._chat_history[document_id].append(message_data)
                        return None, f"msg-{len(self._chat_history[document_id])}"

                    def mock_order_by(field: str):
                        order_mock = MagicMock()
                        
                        def mock_get():
                            # Retorna o histórico ordenado por created_at
                            messages = self._chat_history.get(document_id, [])
                            sorted_messages = sorted(messages, key=lambda x: x.get('created_at', ''))
                            return [MagicMock(to_dict=lambda m=msg: m) for msg in sorted_messages]
                        
                        order_mock.get = mock_get
                        return order_mock

                    subcollection_mock.add = mock_add
                    subcollection_mock.order_by = mock_order_by
                    return subcollection_mock
                return MagicMock()
            
            doc_mock.get = mock_get
            doc_mock.set = mock_set
            doc_mock.update = mock_update
            doc_mock.delete = mock_delete
            doc_mock.collection = mock_collection
            
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

        def mock_where(field: str, op: str, value: Any):
            where_mock = MagicMock()
            
            def mock_limit(limit: int):
                limit_mock = MagicMock()
                
                def mock_get():
                    matching_docs = []
                    for doc_id, data in self._mock_data[collection_name].items():
                        if field in data and data[field] == value:
                            matching_docs.append(MagicMock(
                                id=doc_id,
                                to_dict=lambda d=data: d
                            ))
                            if len(matching_docs) >= limit:
                                break
                    return matching_docs
                
                limit_mock.get = mock_get
                return limit_mock
            
            where_mock.limit = mock_limit
            return where_mock
        
        collection_mock.add = mock_add
        collection_mock.get = mock_get
        collection_mock.where = mock_where
        
        return collection_mock 