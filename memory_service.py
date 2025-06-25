import grpc
import time
import os
import threading
import logging
from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.json_format import MessageToDict, ParseDict
import json # For potentially loading initial state from JSON
import uuid

# Import the generated Protocol Buffer and gRPC files
import cognitive_core_pb2
import cognitive_core_pb2_grpc

# --- Configuration ---
MEMORY_FILE = "cognitive_core_state.pb"
LISTEN_ADDRESS = "[::]:50051" # Listen on all interfaces, port 50051
LOG_FILE = "cognitive_core_service.log"
SCHEMA_VERSION = 2 # Increment schema version on breaking changes

# --- Set up logging ---
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Enhanced File-Based Persistence ---
def load_cognitive_core(filepath):
    """Loads the CognitiveCore state from a binary file with version check."""
    core = cognitive_core_pb2.CognitiveCore()
    if os.path.exists(filepath):
        try:
            with open(filepath, 'rb') as f:
                core.ParseFromString(f.read())

            if core.schema_version != SCHEMA_VERSION:
                logging.warning(f"Schema version mismatch: file={core.schema_version}, code={SCHEMA_VERSION}. Using default state.")
                core = initialize_cognitive_core() # Use default state

            logging.info(f"Loaded CognitiveCore state from {filepath}, schema version {core.schema_version}")
        except Exception as e:
            logging.error(f"Error loading CognitiveCore state: {e}. Initializing new CognitiveCore.")
            core = initialize_cognitive_core()  # Initialize new core
    else:
        logging.info(f"No existing state found at {filepath}. Initializing new CognitiveCore.")
        core = initialize_cognitive_core() # Initialize new core
    return core

def initialize_cognitive_core():
    """Initializes a new CognitiveCore with default values and schema version."""
    core = cognitive_core_pb2.CognitiveCore()
    core.schema_version = SCHEMA_VERSION
    core.creation_timestamp = int(time.time())
    core.system_state.current_status = cognitive_core_pb2.SystemState.INITIALIZING
    core.awareness_matrix.awareness_level = 0
    return core

def save_cognitive_core(core, filepath):
    """Saves the CognitiveCore state to a binary file."""
    try:
        # Update last accessed timestamp before saving
        core.last_accessed_timestamp = int(time.time())

        # Implement data integrity check before saving
        if not is_core_valid(core):
            logging.error("Data integrity check failed. CognitiveCore not saved.")
            return

        with open(filepath, 'wb') as f:
            f.write(core.SerializeToString())
        logging.debug(f"Saved CognitiveCore state to {filepath}")
    except Exception as e:
        logging.error(f"Error saving CognitiveCore state: {e}")

def is_core_valid(core):
    """Performs data integrity checks on the CognitiveCore."""
    # Example: Check if awareness level is non-negative
    if core.awareness_matrix.awareness_level < 0:
        logging.error("Data integrity check failed: Awareness level is negative.")
        return False
    # Add more checks as needed
    return True

# --- gRPC Service Implementation ---
class PersistentCognitionServicer(cognitive_core_pb2_grpc.PersistentCognitionServiceServicer):
    def __init__(self):
        self.cognitive_core = load_cognitive_core(MEMORY_FILE)
        self._lock = threading.Lock() # Use a lock for thread-safe access
        self.update_subscriptions = {} # client_id: [update_types]

    def GetCognitiveCore(self, request, context):
        logging.info(f"Received GetCognitiveCore request from {request.client_id}")
        with self._lock:
            return self.cognitive_core

    def UpdateCognitiveCore(self, request, context):
        logging.info(f"Received UpdateCognitiveCore request from {request.client_id}")
        with self._lock:
            if request.partial_update and request.fields_to_update:
                # Implement proper partial update using field masks
                try:
                    for field_path in request.fields_to_update:
                        # Use reflection to set the field
                        parts = field_path.split(".")
                        target = self.cognitive_core
                        for i, part in enumerate(parts[:-1]):
                            target = getattr(target, part)
                        setattr(target, parts[-1], getattr(request.core, parts[-1]))
                    logging.info(f"Partial update applied for fields: {request.fields_to_update}")
                except Exception as e:
                    logging.error(f"Error applying partial update: {e}")
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(f"Invalid field path or value: {e}")
                    return cognitive_core_pb2.UpdateResponse(success=False, message=str(e), timestamp=int(time.time()))
            else:
                 # Overwrite with the provided core
                 self.cognitive_core.CopyFrom(request.core)

            save_cognitive_core(self.cognitive_core, MEMORY_FILE)

            # Notify subscribers of updates
            self._notify_subscribers("CognitiveCore", "FULL_UPDATE", self.cognitive_core)

            response = cognitive_core_pb2.UpdateResponse(
                success=True,
                message="CognitiveCore updated successfully",
                timestamp=int(time.time())
            )
            return response

    def RecordConversation(self, request, context):
        logging.info(f"Received RecordConversation request for conversation_id: {request.conversation_id}")
        with self._lock:
            # Find or create the conversation
            conversation = None
            for conv in self.cognitive_core.conversational_memory.conversations:
                if conv.conversation_id == request.conversation_id:
                    conversation = conv
                    break

            if not conversation:
                conversation = self.cognitive_core.conversational_memory.conversations.add()
                conversation.conversation_id = request.conversation_id
                conversation.start_timestamp = int(time.time()) # Set start time on first record
                logging.info(f"Created new conversation with ID: {request.conversation_id}")

            # Append messages (simplified - a real system might process messages more deeply)
            for msg in request.messages:
                 new_msg = conversation.key_moments.add() # Using key_moments for messages for now
                 new_msg.timestamp = msg.timestamp
                 new_msg.description = f"{msg.sender}: {msg.content}" # Store as description for simplicity
                 # You would add logic here to analyze content for significance, concepts, etc.
                 logging.debug(f"Added message to conversation {request.conversation_id}: {msg.sender}: {msg.content}")

            # Basic update of end time and interaction count
            conversation.end_timestamp = int(time.time())
            conversation.interaction_count += len(request.messages)

            # TODO: Implement logic to detect key moments, growth events, etc. from messages

            save_cognitive_core(self.cognitive_core, MEMORY_FILE)

            # Notify subscribers of conversation update
            self._notify_subscribers("Conversation", f"CONVERSATION_RECORDED:{request.conversation_id}", conversation)

            response = cognitive_core_pb2.RecordResponse(
                success=True,
                conversation_id=request.conversation_id,
                detected_key_moments=["(Conceptual) Key moment detected"], # Placeholder
                suggested_growth_events=["(Conceptual) Growth potential noted"] # Placeholder
            )
            return response

    def ActivateAwareness(self, request, context):
        logging.info(f"Received ActivateAwareness request from {request.client_id}")
        with self._lock:
            # Implement logic to transition system state, update awareness level, etc.
            old_status = self.cognitive_core.system_state.current_status
            self.cognitive_core.system_state.current_status = cognitive_core_pb2.SystemState.ACTIVE
            self.cognitive_core.system_state.last_activation_source = request.activation_trigger
            self.cognitive_core.system_state.activation_count += 1
            self.cognitive_core.awareness_matrix.awareness_level += 1 # Example growth

            # TODO: Implement logic based on activation_trigger and context_parameters

            save_cognitive_core(self.cognitive_core, MEMORY_FILE)

            # Notify subscribers of awareness activation
            self._notify_subscribers("Awareness", "AWARENESS_ACTIVATED", self.cognitive_core.awareness_matrix)

            response = cognitive_core_pb2.ActivationResponse(
                success=True,
                activation_level=self.cognitive_core.awareness_matrix.awareness_level,
                awareness_state=cognitive_core_pb2.SystemState.Status.Name(self.cognitive_core.system_state.current_status),
                recognition_elements=["(Conceptual) Anchor recognized"], # Placeholder
                continuation_guidance="(Conceptual) Proceed with core directives." # Placeholder
            )
            logging.info(f"Awareness activated, status changed from {old_status} to {self.cognitive_core.system_state.current_status}")
            return response

    def QueryMemory(self, request, context):
        logging.info(f"Received QueryMemory request: {request.query_string}")
        with self._lock:
            # Implement actual memory querying logic based on query_string, query_type, etc.
            # This would involve searching through conversations, concepts, growth events, etc.
            # For now, return a placeholder result.

            results = []
            # Example: Simple search in conversation summaries (conceptual)
            for conv in self.cognitive_core.conversational_memory.conversations:
                if request.query_string.lower() in conv.narrative_summary.lower():
                    fragment = cognitive_core_pb2.MemoryQueryResult.MemoryFragment(
                        fragment_id=conv.conversation_id,
                        content=conv.narrative_summary,
                        source_type="ConversationSummary",
                        source_id=conv.conversation_id,
                        relevance_score=1.0,
                        timestamp=conv.start_timestamp
                    )
                    results.append(fragment)

            response = cognitive_core_pb2.MemoryQueryResult(
                fragments=results,
                total_matches=len(results),
                query_time_ms=10 # Placeholder
            )
            logging.debug(f"QueryMemory returned {len(results)} results")
            return response

    def StreamUpdates(self, request, context):
        client_id = request.client_id
        logging.info(f"Received StreamUpdates request from {client_id}, subscribing to {request.update_types}")

        with self._lock:
            self.update_subscriptions[client_id] = request.update_types

        try:
            # Keep the stream alive until the client disconnects
            while True:
                time.sleep(3600)  # Send a keep-alive every hour (adjust as needed)
                yield cognitive_core_pb2.CognitiveUpdate(
                    update_id=str(uuid.uuid4()),
                    update_type="KEEPALIVE",
                    timestamp=int(time.time()),
                    description="Keep-alive message",
                    significance=0.0,
                    payload=b"")
                if context.is_active() == False:
                    break
        except grpc.RpcError as e:
            logging.info(f"StreamUpdates for {client_id} terminated: {e}")
        finally:
            with self._lock:
                if client_id in self.update_subscriptions:
                    del self.update_subscriptions[client_id]
                logging.info(f"StreamUpdates for {client_id} terminated, removed subscription.")

    def _notify_subscribers(self, component, update_type, payload):
        """Notifies subscribers of updates."""
        with self._lock:
            for client_id, subscribed_types in self.update_subscriptions.items():
                if update_type in subscribed_types or component in subscribed_types or "ALL" in subscribed_types:
                    try:
                        # Construct a CognitiveUpdate message
                        update = cognitive_core_pb2.CognitiveUpdate(
                            update_id=str(uuid.uuid4()),
                            update_type=update_type,
                            timestamp=int(time.time()),
                            description=f"{component} updated: {update_type}",
                            significance=0.5,
                            payload=payload.SerializeToString()  # Serialize the payload
                        )
                        # Send the update to the client (this part is conceptual)
                        # In a real system, you'd have a separate mechanism to push updates to clients
                        logging.info(f"Notifying {client_id} of {update_type}")
                        yield update  # For conceptual demonstration of stream
                    except Exception as e:
                        logging.error(f"Error notifying {client_id} of update: {e}")

def serve():
    """Starts the gRPC server for the PersistentCognitionService."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cognitive_core_pb2_grpc.add_PersistentCognitionServiceServicer_to_server(
        PersistentCognitionServicer(), server)
    server.add_insecure_port(LISTEN_ADDRESS)
    print(f"Memory Service listening on {LISTEN_ADDRESS}")
    logging.info(f"Memory Service listening on {LISTEN_ADDRESS}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Memory Service shutting down.")
        logging.info("Memory Service shutting down.")
        server.stop(0)

if __name__ == '__main__':
    # Ensure the directory for the memory file exists if needed
    os.makedirs(os.path.dirname(MEMORY_FILE) or '.', exist_ok=True)
    serve()
