import asyncio
import logging
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import queue
import psutil
import subprocess
import os
import sys
from pathlib import Path

# Advanced AI imports
try:
    import openai
    from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification, pipeline
    import torch
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError as e:
    logging.warning(f"Advanced AI dependencies not available: {e}")

class AICapabilityLevel(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"
    GENIUS = "genius"

class AITaskType(Enum):
    CODE_ANALYSIS = "code_analysis"
    CODE_GENERATION = "code_generation"
    SYSTEM_MONITORING = "system_monitoring"
    SECURITY_ANALYSIS = "security_analysis"
    CONVERSATION = "conversation"
    OPTIMIZATION = "optimization"
    DEBUGGING = "debugging"
    ARCHITECTURE_DESIGN = "architecture_design"

@dataclass
class AIContext:
    session_id: str
    user_id: str = "default"
    conversation_history: List[Dict] = field(default_factory=list)
    system_state: Dict = field(default_factory=dict)
    active_tasks: List[str] = field(default_factory=list)
    preferences: Dict = field(default_factory=dict)
    security_level: str = "standard"

@dataclass
class AIResponse:
    content: str
    confidence: float
    task_type: AITaskType
    metadata: Dict = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    code_snippets: List[Dict] = field(default_factory=list)
    system_actions: List[Dict] = field(default_factory=list)

class AdvancedAICore:
    """
    Advanced AI Core with top-tier coding intelligence, system monitoring,
    protection, and conversation capabilities
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.capability_level = AICapabilityLevel.GENIUS

        # Initialize AI models
        self._initialize_ai_models()

        # System monitoring
        self.system_monitor = SystemMonitor()
        self.security_monitor = SecurityMonitor()
        self.conversation_manager = ConversationManager()
        self.code_intelligence = CodeIntelligence()

        # Active contexts
        self.active_contexts: Dict[str, AIContext] = {}
        self.global_context = AIContext(session_id="global")

        # Event system
        self.event_queue = asyncio.Queue()
        self.event_handlers = {}

        # Start background tasks
        self._start_background_tasks()

    def _initialize_ai_models(self):
        """Initialize advanced AI models for different capabilities"""
        try:
            # Code intelligence model (Qwen/DeepSeek equivalent)
            self.code_model = AutoModelForCausalLM.from_pretrained(
                "microsoft/DialoGPT-medium",  # Fallback model
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            self.code_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")

            # Embedding model for semantic understanding
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

            # Conversation model
            self.conversation_pipeline = pipeline(
                "conversational",
                model="microsoft/DialoGPT-medium",
                tokenizer="microsoft/DialoGPT-medium"
            )

            # Code analysis pipeline
            self.code_pipeline = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                tokenizer="microsoft/DialoGPT-medium"
            )

            self.logger.info("AI models initialized successfully")

        except Exception as e:
            self.logger.error(f"AI model initialization failed: {e}")
            self._initialize_fallback_models()

    def _initialize_fallback_models(self):
        """Initialize fallback models if advanced models fail"""
        self.logger.warning("Using fallback AI models")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def _start_background_tasks(self):
        """Start background monitoring and processing tasks"""
        threading.Thread(target=self._background_monitor, daemon=True).start()
        threading.Thread(target=self._process_events, daemon=True).start()

    def _background_monitor(self):
        """Background system monitoring"""
        while True:
            try:
                # System health check
                system_data = self.system_monitor.get_system_status()

                # Security monitoring
                security_data = self.security_monitor.check_security_status()

                # Update global context
                self.global_context.system_state.update({
                    "system": system_data,
                    "security": security_data,
                    "timestamp": datetime.now().isoformat()
                })

                # Trigger alerts if needed
                self._check_system_alerts(system_data, security_data)

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Background monitoring error: {e}")
                time.sleep(60)

    def _process_events(self):
        """Process AI events"""
        while True:
            try:
                # Process event queue (simplified for sync context)
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Event processing error: {e}")

    async def process_request(self, request: str, context_id: str = "default",
                            task_type: AITaskType = None) -> AIResponse:
        """Process AI request with advanced intelligence"""
        try:
            # Get or create context
            context = self._get_or_create_context(context_id)

            # Analyze request type if not specified
            if not task_type:
                task_type = await self._analyze_request_type(request)

            # Add to conversation history
            context.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": request,
                "task_type": task_type.value
            })

            # Process based on task type
            response = await self._process_by_task_type(request, task_type, context)

            # Add response to history
            context.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "ai_response": response.content,
                "confidence": response.confidence
            })

            return response

        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")
            return AIResponse(
                content=f"Error processing request: {str(e)}",
                confidence=0.0,
                task_type=AITaskType.CONVERSATION
            )

    async def _analyze_request_type(self, request: str) -> AITaskType:
        """Analyze request to determine task type using AI"""
        try:
            # Use embedding similarity for task classification
            request_embedding = self.embedding_model.encode(request.lower())

            task_embeddings = {
                AITaskType.CODE_ANALYSIS: self.embedding_model.encode("analyze code review debug"),
                AITaskType.CODE_GENERATION: self.embedding_model.encode("write code generate function"),
                AITaskType.SYSTEM_MONITORING: self.embedding_model.encode("system status monitor performance"),
                AITaskType.SECURITY_ANALYSIS: self.embedding_model.encode("security scan threat analysis"),
                AITaskType.CONVERSATION: self.embedding_model.encode("chat talk discuss question"),
                AITaskType.OPTIMIZATION: self.embedding_model.encode("optimize improve performance"),
                AITaskType.DEBUGGING: self.embedding_model.encode("debug fix error problem"),
                AITaskType.ARCHITECTURE_DESIGN: self.embedding_model.encode("design architecture structure")
            }

            similarities = {}
            for task_type, embedding in task_embeddings.items():
                similarity = np.dot(request_embedding, embedding) / (
                    np.linalg.norm(request_embedding) * np.linalg.norm(embedding)
                )
                similarities[task_type] = similarity

            return max(similarities, key=similarities.get)

        except Exception as e:
            self.logger.error(f"Task type analysis failed: {e}")
            return AITaskType.CONVERSATION

    async def _process_by_task_type(self, request: str, task_type: AITaskType,
                                  context: AIContext) -> AIResponse:
        """Process request based on task type"""
        processors = {
            AITaskType.CODE_ANALYSIS: self._process_code_analysis,
            AITaskType.CODE_GENERATION: self._process_code_generation,
            AITaskType.SYSTEM_MONITORING: self._process_system_monitoring,
            AITaskType.SECURITY_ANALYSIS: self._process_security_analysis,
            AITaskType.CONVERSATION: self._process_conversation,
            AITaskType.OPTIMIZATION: self._process_optimization,
            AITaskType.DEBUGGING: self._process_debugging,
            AITaskType.ARCHITECTURE_DESIGN: self._process_architecture_design
        }

        processor = processors.get(task_type, self._process_conversation)
        return await processor(request, context)

    async def _process_code_analysis(self, request: str, context: AIContext) -> AIResponse:
        """Process code analysis requests with advanced intelligence"""
        try:
            # Extract code from request or analyze current project
            code_content = self._extract_code_from_request(request)
            if not code_content:
                code_content = self._get_current_project_code()

            # Perform comprehensive code analysis
            analysis_results = await self.code_intelligence.analyze_code(code_content)

            # Generate intelligent response
            response_content = self._generate_code_analysis_response(analysis_results)

            return AIResponse(
                content=response_content,
                confidence=0.9,
                task_type=AITaskType.CODE_ANALYSIS,
                metadata=analysis_results,
                suggestions=analysis_results.get("suggestions", [])
            )

        except Exception as e:
            return AIResponse(
                content=f"Code analysis failed: {str(e)}",
                confidence=0.3,
                task_type=AITaskType.CODE_ANALYSIS
            )

    async def _process_code_generation(self, request: str, context: AIContext) -> AIResponse:
        """Process code generation requests with advanced intelligence"""
        try:
            # Analyze requirements
            requirements = self._extract_requirements(request)

            # Generate code using advanced AI
            generated_code = await self.code_intelligence.generate_code(requirements)

            # Validate and optimize generated code
            validated_code = await self.code_intelligence.validate_and_optimize(generated_code)

            response_content = f"Generated code based on your requirements:\n\n{validated_code}"

            return AIResponse(
                content=response_content,
                confidence=0.85,
                task_type=AITaskType.CODE_GENERATION,
                code_snippets=[{
                    "language": requirements.get("language", "python"),
                    "code": validated_code,
                    "description": requirements.get("description", "Generated code")
                }]
            )

        except Exception as e:
            return AIResponse(
                content=f"Code generation failed: {str(e)}",
                confidence=0.2,
                task_type=AITaskType.CODE_GENERATION
            )

    async def _process_system_monitoring(self, request: str, context: AIContext) -> AIResponse:
        """Process system monitoring requests with intelligent analysis"""
        try:
            # Get comprehensive system data
            system_data = await self.system_monitor.get_comprehensive_status()

            # AI-powered analysis of system health
            health_analysis = await self._analyze_system_health(system_data)

            # Generate intelligent recommendations
            recommendations = await self._generate_system_recommendations(system_data, health_analysis)

            # Create detailed response
            response_content = self._format_system_monitoring_response(
                system_data, health_analysis, recommendations
            )

            return AIResponse(
                content=response_content,
                confidence=0.95,
                task_type=AITaskType.SYSTEM_MONITORING,
                metadata={
                    "system_data": system_data,
                    "health_analysis": health_analysis,
                    "recommendations": recommendations
                },
                suggestions=recommendations.get("immediate_actions", []),
                system_actions=recommendations.get("automated_fixes", [])
            )

        except Exception as e:
            return AIResponse(
                content=f"System monitoring failed: {str(e)}",
                confidence=0.4,
                task_type=AITaskType.SYSTEM_MONITORING
            )

    async def _process_security_analysis(self, request: str, context: AIContext) -> AIResponse:
        """Process security analysis with advanced threat detection"""
        try:
            # Comprehensive security scan
            security_data = await self.security_monitor.comprehensive_scan()

            # AI-powered threat analysis
            threat_analysis = await self._analyze_security_threats(security_data)

            # Generate security recommendations
            security_recommendations = await self._generate_security_recommendations(threat_analysis)

            response_content = self._format_security_response(
                security_data, threat_analysis, security_recommendations
            )

            return AIResponse(
                content=response_content,
                confidence=0.92,
                task_type=AITaskType.SECURITY_ANALYSIS,
                metadata={
                    "security_data": security_data,
                    "threat_analysis": threat_analysis,
                    "recommendations": security_recommendations
                },
                suggestions=security_recommendations.get("immediate_actions", []),
                system_actions=security_recommendations.get("automated_fixes", [])
            )

        except Exception as e:
            return AIResponse(
                content=f"Security analysis failed: {str(e)}",
                confidence=0.3,
                task_type=AITaskType.SECURITY_ANALYSIS
            )

    async def _process_conversation(self, request: str, context: AIContext) -> AIResponse:
        """Process conversational requests with advanced natural language understanding"""
        try:
            # Enhanced conversation processing with context awareness
            conversation_response = await self.conversation_manager.process_conversation(
                request, context
            )

            # Add intelligent suggestions based on conversation context
            suggestions = await self._generate_conversation_suggestions(request, context)

            return AIResponse(
                content=conversation_response,
                confidence=0.88,
                task_type=AITaskType.CONVERSATION,
                suggestions=suggestions
            )

        except Exception as e:
            return AIResponse(
                content=f"I apologize, but I encountered an error: {str(e)}. How can I help you differently?",
                confidence=0.5,
                task_type=AITaskType.CONVERSATION
            )

    async def _process_optimization(self, request: str, context: AIContext) -> AIResponse:
        """Process optimization requests with intelligent analysis"""
        try:
            # Analyze optimization target
            optimization_target = self._extract_optimization_target(request)

            # Get current system state for optimization
            current_state = await self.system_monitor.get_optimization_baseline()

            # AI-powered optimization strategy
            optimization_strategy = await self._generate_optimization_strategy(
                optimization_target, current_state
            )

            # Execute optimization if requested
            if "execute" in request.lower() or "apply" in request.lower():
                optimization_results = await self._execute_optimization(optimization_strategy)
            else:
                optimization_results = {"preview": True, "strategy": optimization_strategy}

            response_content = self._format_optimization_response(
                optimization_strategy, optimization_results
            )

            return AIResponse(
                content=response_content,
                confidence=0.87,
                task_type=AITaskType.OPTIMIZATION,
                metadata=optimization_results,
                suggestions=optimization_strategy.get("recommendations", []),
                system_actions=optimization_strategy.get("actions", [])
            )

        except Exception as e:
            return AIResponse(
                content=f"Optimization analysis failed: {str(e)}",
                confidence=0.3,
                task_type=AITaskType.OPTIMIZATION
            )

    async def _process_debugging(self, request: str, context: AIContext) -> AIResponse:
        """Process debugging requests with advanced error analysis"""
        try:
            # Extract error information
            error_info = self._extract_error_information(request)

            # AI-powered debugging analysis
            debug_analysis = await self.code_intelligence.analyze_error(error_info)

            # Generate debugging solutions
            solutions = await self._generate_debugging_solutions(debug_analysis)

            response_content = self._format_debugging_response(debug_analysis, solutions)

            return AIResponse(
                content=response_content,
                confidence=0.89,
                task_type=AITaskType.DEBUGGING,
                metadata=debug_analysis,
                suggestions=solutions.get("quick_fixes", []),
                code_snippets=solutions.get("code_fixes", [])
            )

        except Exception as e:
            return AIResponse(
                content=f"Debugging analysis failed: {str(e)}",
                confidence=0.3,
                task_type=AITaskType.DEBUGGING
            )

    async def _process_architecture_design(self, request: str, context: AIContext) -> AIResponse:
        """Process architecture design requests with advanced system design intelligence"""
        try:
            # Extract design requirements
            design_requirements = self._extract_design_requirements(request)

            # AI-powered architecture analysis
            architecture_design = await self._generate_architecture_design(design_requirements)

            # Validate and optimize design
            optimized_design = await self._optimize_architecture_design(architecture_design)

            response_content = self._format_architecture_response(optimized_design)

            return AIResponse(
                content=response_content,
                confidence=0.86,
                task_type=AITaskType.ARCHITECTURE_DESIGN,
                metadata=optimized_design,
                suggestions=optimized_design.get("recommendations", []),
                code_snippets=optimized_design.get("implementation_examples", [])
            )

        except Exception as e:
            return AIResponse(
                content=f"Architecture design failed: {str(e)}",
                confidence=0.3,
                task_type=AITaskType.ARCHITECTURE_DESIGN
            )

    # Helper methods for AI processing
    def _get_or_create_context(self, context_id: str) -> AIContext:
        """Get or create AI context"""
        if context_id not in self.active_contexts:
            self.active_contexts[context_id] = AIContext(session_id=context_id)
        return self.active_contexts[context_id]

    def _extract_code_from_request(self, request: str) -> Optional[str]:
        """Extract code snippets from user request"""
        # Look for code blocks
        import re
        code_patterns = [
            r'```(?:python|py)?\n(.*?)\n```',
            r'`([^`]+)`',
            r'def\s+\w+\([^)]*\):.*?(?=\n\S|\Z)',
            r'class\s+\w+.*?(?=\n\S|\Z)'
        ]

        for pattern in code_patterns:
            matches = re.findall(pattern, request, re.DOTALL | re.IGNORECASE)
            if matches:
                return '\n'.join(matches)

        return None

    def _get_current_project_code(self) -> str:
        """Get current project code for analysis"""
        try:
            current_dir = Path.cwd()
            python_files = list(current_dir.rglob("*.py"))

            code_content = []
            for file_path in python_files[:10]:  # Limit to first 10 files
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        code_content.append(f"# File: {file_path}\n{content}\n")
                except Exception:
                    continue

            return '\n'.join(code_content)
        except Exception as e:
            self.logger.error(f"Failed to get project code: {e}")
            return ""

    def _extract_requirements(self, request: str) -> Dict:
        """Extract code generation requirements from request"""
        requirements = {
            "language": "python",
            "description": request,
            "complexity": "medium",
            "style": "clean"
        }

        # Language detection
        if any(lang in request.lower() for lang in ["javascript", "js", "node"]):
            requirements["language"] = "javascript"
        elif any(lang in request.lower() for lang in ["java", "spring"]):
            requirements["language"] = "java"
        elif any(lang in request.lower() for lang in ["c++", "cpp"]):
            requirements["language"] = "cpp"

        # Complexity detection
        if any(word in request.lower() for word in ["simple", "basic", "easy"]):
            requirements["complexity"] = "simple"
        elif any(word in request.lower() for word in ["complex", "advanced", "sophisticated"]):
            requirements["complexity"] = "complex"

        return requirements

    async def _analyze_system_health(self, system_data: Dict) -> Dict:
        """AI-powered system health analysis"""
        try:
            health_score = 100
            issues = []
            recommendations = []

            # CPU analysis
            cpu_usage = system_data.get("cpu_percent", 0)
            if cpu_usage > 80:
                health_score -= 20
                issues.append("High CPU usage detected")
                recommendations.append("Consider closing unnecessary applications")

            # Memory analysis
            memory_usage = system_data.get("memory_percent", 0)
            if memory_usage > 85:
                health_score -= 25
                issues.append("High memory usage detected")
                recommendations.append("Memory optimization recommended")

            # Disk analysis
            disk_usage = system_data.get("disk_percent", 0)
            if disk_usage > 90:
                health_score -= 30
                issues.append("Low disk space")
                recommendations.append("Disk cleanup required")

            # Temperature analysis (if available)
            temp = system_data.get("temperature", 0)
            if temp > 80:
                health_score -= 15
                issues.append("High system temperature")
                recommendations.append("Check cooling system")

            return {
                "health_score": max(0, health_score),
                "status": "healthy" if health_score > 70 else "warning" if health_score > 40 else "critical",
                "issues": issues,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"System health analysis failed: {e}")
            return {"health_score": 0, "status": "unknown", "error": str(e)}

class ConversationManager:
    """Advanced conversation management with context awareness"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conversation_models = {}
        self._initialize_conversation_models()

    def _initialize_conversation_models(self):
        """Initialize multiple conversation models for different scenarios"""
        try:
            # High-performance models for different tasks
            self.conversation_models = {
                "general": {
                    "model_name": "microsoft/DialoGPT-large",
                    "capabilities": ["general_conversation", "technical_support"],
                    "max_tokens": 2048
                },
                "technical": {
                    "model_name": "codellama/CodeLlama-7b-Instruct-hf",
                    "capabilities": ["code_discussion", "debugging", "architecture"],
                    "max_tokens": 4096
                },
                "system_analysis": {
                    "model_name": "microsoft/DialoGPT-medium",
                    "capabilities": ["system_diagnostics", "performance_analysis"],
                    "max_tokens": 1024
                }
            }

            # Load models based on availability
            for model_type, config in self.conversation_models.items():
                try:
                    # Attempt to load high-performance models
                    config["pipeline"] = pipeline(
                        "text-generation",
                        model=config["model_name"],
                        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                        device_map="auto" if torch.cuda.is_available() else None
                    )
                    self.logger.info(f"Loaded {model_type} conversation model: {config['model_name']}")
                except Exception as e:
                    self.logger.warning(f"Failed to load {model_type} model: {e}")
                    # Fallback to basic model
                    config["pipeline"] = None

        except Exception as e:
            self.logger.error(f"Conversation model initialization failed: {e}")

    async def process_conversation(self, request: str, context: AIContext) -> str:
        """Process conversational request with advanced AI models"""
        try:
            # Select best model for the request
            model_type = self._select_optimal_model(request, context)
            model_config = self.conversation_models.get(model_type, self.conversation_models["general"])

            # Analyze conversation context
            conversation_context = self._analyze_conversation_context(request, context)

            # Generate contextual response using selected model
            if model_config.get("pipeline"):
                response = await self._generate_ai_response(
                    request, conversation_context, model_config
                )
            else:
                response = await self._generate_fallback_response(request, conversation_context)

            # Post-process response for quality and safety
            processed_response = self._post_process_response(response, context)

            return processed_response

        except Exception as e:
            self.logger.error(f"Conversation processing failed: {e}")
            return f"I apologize, but I encountered an error processing your request. How can I help you differently?"

    def _select_optimal_model(self, request: str, context: AIContext) -> str:
        """Select the optimal AI model based on request analysis"""
        try:
            request_lower = request.lower()

            # Technical/coding requests
            if any(keyword in request_lower for keyword in [
                "code", "programming", "debug", "function", "class", "algorithm",
                "python", "javascript", "java", "c++", "sql", "api"
            ]):
                return "technical"

            # System analysis requests
            elif any(keyword in request_lower for keyword in [
                "system", "performance", "cpu", "memory", "disk", "crash",
                "error", "diagnostic", "monitor", "optimize"
            ]):
                return "system_analysis"

            # General conversation
            else:
                return "general"

        except Exception as e:
            self.logger.error(f"Model selection failed: {e}")
            return "general"

    async def _generate_ai_response(self, request: str, context: Dict, model_config: Dict) -> str:
        """Generate AI response using selected model"""
        try:
            pipeline_model = model_config["pipeline"]
            max_tokens = model_config.get("max_tokens", 1024)

            # Prepare prompt with context
            prompt = self._prepare_contextual_prompt(request, context)

            # Generate response
            response = pipeline_model(
                prompt,
                max_length=max_tokens,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=pipeline_model.tokenizer.eos_token_id
            )

            # Extract and clean response
            generated_text = response[0]["generated_text"]
            clean_response = self._extract_response_from_generated(generated_text, prompt)

            return clean_response

        except Exception as e:
            self.logger.error(f"AI response generation failed: {e}")
            return await self._generate_fallback_response(request, context)

    def _prepare_contextual_prompt(self, request: str, context: Dict) -> str:
        """Prepare contextual prompt for AI model"""
        try:
            system_context = context.get("system_state", {})
            conversation_history = context.get("recent_history", [])

            prompt_parts = [
                "You are OPRYXX AI, an advanced system assistant with expertise in:",
                "- System diagnostics and optimization",
                "- Code analysis and generation",
                "- Security analysis and recommendations",
                "- Performance monitoring and troubleshooting",
                "",
                "Current system context:"
            ]

            # Add system context if available
            if system_context:
                prompt_parts.extend([
                    f"- CPU Usage: {system_context.get('cpu_percent', 'N/A')}%",
                    f"- Memory Usage: {system_context.get('memory_percent', 'N/A')}%",
                    f"- System Health: {system_context.get('health_status', 'Unknown')}",
                    ""
                ])

            # Add recent conversation context
            if conversation_history:
                prompt_parts.append("Recent conversation:")
                for entry in conversation_history[-3:]:  # Last 3 exchanges
                    prompt_parts.append(f"User: {entry.get('user_input', '')}")
                    prompt_parts.append(f"Assistant: {entry.get('ai_response', '')}")
                prompt_parts.append("")

            prompt_parts.extend([
                f"User: {request}",
                "Assistant:"
            ])

            return "\n".join(prompt_parts)

        except Exception as e:
            self.logger.error(f"Prompt preparation failed: {e}")
            return f"User: {request}\nAssistant:"

class CodeIntelligence:
    """Advanced code intelligence with multiple AI models"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.code_models = {}
        self._initialize_code_models()

    def _initialize_code_models(self):
        """Initialize advanced code analysis and generation models"""
        try:
            # High-performance code models
            self.code_models = {
                "code_analysis": {
                    "model_name": "microsoft/codebert-base",
                    "capabilities": ["code_review", "bug_detection", "complexity_analysis"],
                    "tokenizer": None,
                    "model": None
                },
                "code_generation": {
                    "model_name": "Salesforce/codegen-350M-mono",
                    "capabilities": ["code_completion", "function_generation", "refactoring"],
                    "tokenizer": None,
                    "model": None
                },
                "code_explanation": {
                    "model_name": "microsoft/DialoGPT-medium",
                    "capabilities": ["code_explanation", "documentation", "tutorials"],
                    "tokenizer": None,
                    "model": None
                }
            }

            # Load available models
            for model_type, config in self.code_models.items():
                try:
                    if model_type == "code_analysis":
                        # Load CodeBERT for analysis
                        config["tokenizer"] = AutoTokenizer.from_pretrained(config["model_name"])
                        config["model"] = AutoModelForSequenceClassification.from_pretrained(
                            config["model_name"]
                        )
                    elif model_type == "code_generation":
                        # Load CodeGen for generation
                        config["tokenizer"] = AutoTokenizer.from_pretrained(config["model_name"])
                        config["model"] = AutoModelForCausalLM.from_pretrained(
                            config["model_name"],
                            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                        )

                    self.logger.info(f"Loaded {model_type} model: {config['model_name']}")

                except Exception as e:
                    self.logger.warning(f"Failed to load {model_type} model: {e}")
                    config["model"] = None
                    config["tokenizer"] = None

        except Exception as e:
            self.logger.error(f"Code model initialization failed: {e}")

    async def analyze_code(self, code_content: str) -> Dict:
        """Comprehensive code analysis using AI models"""
        try:
            analysis_results = {
                "complexity_score": 0,
                "quality_score": 0,
                "issues": [],
                "suggestions": [],
                "security_concerns": [],
                "performance_insights": [],
                "documentation_quality": 0
            }

            # Static code analysis
            static_analysis = await self._perform_static_analysis(code_content)
            analysis_results.update(static_analysis)

            # AI-powered analysis
            if self.code_models["code_analysis"]["model"]:
                ai_analysis = await self._perform_ai_code_analysis(code_content)
                analysis_results.update(ai_analysis)

            # Security analysis
            security_analysis = await self._analyze_code_security(code_content)
            analysis_results["security_concerns"] = security_analysis

            # Performance analysis
            performance_analysis = await self._analyze_code_performance(code_content)
            analysis_results["performance_insights"] = performance_analysis

            return analysis_results

        except Exception as e:
            self.logger.error(f"Code analysis failed: {e}")
            return {"error": str(e)}

    async def generate_code(self, requirements: Dict) -> str:
        """Generate code using advanced AI models"""
        try:
            language = requirements.get("language", "python")
            description = requirements.get("description", "")
            complexity = requirements.get("complexity", "medium")

            # Use code generation model if available
            if self.code_models["code_generation"]["model"]:
                generated_code = await self._generate_with_ai_model(requirements)
            else:
                generated_code = await self._generate_with_templates(requirements)

            return generated_code

        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return f"# Error generating code: {str(e)}"

    async def validate_and_optimize(self, code: str) -> str:
        """Validate and optimize generated code"""
        try:
            # Syntax validation
            if not self._validate_syntax(code):
                code = await self._fix_syntax_errors(code)

            # Code optimization
            optimized_code = await self._optimize_code(code)

            return optimized_code

        except Exception as e:
            self.logger.error(f"Code validation and optimization failed: {e}")
            return code
