"""
Workflow nodes for the Course Q&A Agent.

Adapted from caching-agent to use CourseManager for course search.
Semantic caching is commented out for now - will be added later.
"""

import logging
import time

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .state import WorkflowState
from .tools import search_courses_sync

# Suppress httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# Configure logger
logger = logging.getLogger("course-qa-workflow")

# Global cache variable - COMMENTED OUT FOR NOW
# Will be added in future stages
# semantic_cache = None

# Global LLMs
_analysis_llm = None
_research_llm = None


def initialize_nodes():
    """Initialize the nodes with required dependencies."""
    # NOTE: Semantic cache initialization commented out
    # global semantic_cache
    # semantic_cache = cache
    pass


def get_analysis_llm():
    """Get the configured analysis LLM instance."""
    global _analysis_llm
    if _analysis_llm is None:
        _analysis_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=800)
    return _analysis_llm


def get_research_llm():
    """Get the configured research LLM instance."""
    global _research_llm
    if _research_llm is None:
        _research_llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0.3, max_tokens=3000
        )
    return _research_llm


def classify_intent_node(state: WorkflowState) -> WorkflowState:
    """Classify query intent and determine appropriate detail level."""
    start_time = time.perf_counter()
    query = state["original_query"]

    logger.info(f"🎯 Classifying intent for: '{query[:50]}...'")

    try:
        intent_prompt = f"""You are a query intent classifier for a course information system.

TASK: Analyze the query and return ONLY the most appropriate intent category.

Query: {query}

INTENT CATEGORIES:

1. GREETING
   - Greetings, acknowledgments, pleasantries
   - Examples: "hello", "hi there", "thank you", "thanks"

2. GENERAL
   - Broad course information requests
   - Course descriptions and overviews
   - "What is [course]?" questions
   - Example: "What is CS002?"

3. SYLLABUS_OBJECTIVES
   - Syllabus requests
   - Course structure and topics covered
   - Learning objectives and outcomes
   - Examples: "Show me the syllabus for CS002", "What will I learn?", "What topics are covered?", "Give me details about this course"

4. ASSIGNMENTS
   - Homework, projects, exams
   - Assessment types and workload
   - Grading information
   - Examples: "What are the assignments?", "How many exams?", "What's the workload?"

5. PREREQUISITES
   - Course requirements
   - Prior knowledge needed
   - Examples: "What are the prerequisites?", "What do I need before taking this?"

CLASSIFICATION RULES:
- Choose the MOST SPECIFIC category that matches
- If multiple categories apply, prioritize based on the primary intent
- Default to GENERAL for ambiguous queries
- Ignore filler words and focus on core intent

OUTPUT FORMAT (respond with exactly this structure):
INTENT: <category_name>
"""

        response = get_analysis_llm().invoke([HumanMessage(content=intent_prompt)])

        # Track LLM usage
        llm_calls = state.get("llm_calls", {}).copy()
        llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1

        # Parse response
        response_content = response.content.strip()
        intent = "GENERAL"

        for line in response_content.split("\n"):
            if line.startswith("INTENT:"):
                intent = line.split(":", 1)[1].strip()

        logger.info(f"🎯 Intent: {intent}")

        latency = (time.perf_counter() - start_time) * 1000

        return {
            **state,
            "query_intent": intent,
            "llm_calls": llm_calls,
        }

    except Exception as e:
        logger.error(f"❌ Intent classification failed: {e}")
        # Default to safe values
        return {
            **state,
            "query_intent": "GENERAL",
        }


def decompose_query_node(state: WorkflowState) -> WorkflowState:
    """Decompose complex queries into focused, cacheable sub-questions."""
    start_time = time.perf_counter()
    query = state["original_query"]

    logger.info(f"🧠 Decomposing query: '{query[:50]}...'")

    try:
        decomposition_prompt = f"""
        Analyze this course-related query and determine if it needs to be broken down into sub-questions.

        Original query: {query}

        Rules:
        - If the query is simple and focused on ONE topic, respond with: SINGLE_QUESTION
        - If the query has multiple distinct aspects, break it into 2-4 specific sub-questions
        - Each sub-question should be self-contained and cacheable
        - Focus on course-related information (course content, prerequisites, instructors, schedules, etc.)

        If breaking down, provide ONLY the sub-questions, one per line, no numbering.
        If keeping as single question, respond with exactly: SINGLE_QUESTION
        """

        response = get_analysis_llm().invoke(
            [HumanMessage(content=decomposition_prompt)]
        )

        # Track LLM usage
        llm_calls = state.get("llm_calls", {}).copy()
        llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1

        # Process response
        response_content = response.content.strip()
        if response_content == "SINGLE_QUESTION":
            sub_questions = [query]
            logger.info("🧠 Query is simple - keeping as single question")
        else:
            sub_questions = [
                line.strip()
                for line in response_content.split("\n")
                if line.strip()
                and not line.strip().startswith(("1.", "2.", "3.", "4.", "-", "*"))
                and line.strip() != "SINGLE_QUESTION"
            ]

            if not sub_questions or len(sub_questions) == 1:
                sub_questions = [query]
            elif len(sub_questions) > 4:
                sub_questions = sub_questions[:4]

            logger.info(
                f"🧠 Decomposed into {len(sub_questions)} sub-questions in {(time.perf_counter() - start_time) * 1000:.2f}ms"
            )
            for i, q in enumerate(sub_questions, 1):
                logger.info(f"   {i}. {q}")

        # Update state
        state["sub_questions"] = sub_questions
        state["llm_calls"] = llm_calls
        state["execution_path"].append("decomposed")

        # Initialize tracking for sub-questions
        for question in sub_questions:
            state["cache_hits"][question] = False
            state["cache_confidences"][question] = 0.0
            state["research_iterations"][question] = 0
            state["current_research_strategy"][question] = "initial"

        # Update metrics
        decomposition_time = (time.perf_counter() - start_time) * 1000
        state["metrics"]["decomposition_latency"] = decomposition_time
        state["metrics"]["sub_question_count"] = len(sub_questions)

        logger.info("🧠 Query decomposition complete")
        return state

    except Exception as e:
        logger.error(f"Decomposition failed: {e}")
        # Fallback to original query
        state["sub_questions"] = [query]
        state["execution_path"].append("decomposed")
        return state


def extract_entities_node(state: WorkflowState) -> WorkflowState:
    """
    Extract named entities from query for hybrid search.

    NEW in Stage 4: Performs NER to identify:
    - Course codes (e.g., CS101, MATH202)
    - Course names (e.g., "Introduction to Python")
    - Departments (e.g., Computer Science, Mathematics)
    - Instructors
    - Other metadata for filtering
    """
    start_time = time.perf_counter()
    query = state["original_query"]
    sub_questions = state.get("sub_questions", [query])

    logger.info(f"🔍 Extracting entities from query: '{query[:50]}...'")

    try:
        ner_prompt = f"""
        Extract structured information from this course-related query for precise search.

        Query: {query}

        Extract the following entities (return empty list/dict if not found):

        1. COURSE_CODES: Exact course codes mentioned (e.g., CS101, MATH202, ENG301)
        2. COURSE_NAMES: Specific course titles mentioned (e.g., "Introduction to Python", "Data Structures")
        3. DEPARTMENTS: Department names (e.g., Computer Science, Mathematics, Engineering)
        4. INSTRUCTORS: Instructor names if mentioned
        5. TOPICS: Specific topics or subjects (e.g., machine learning, calculus, databases)
        6. METADATA_FILTERS: Other filters like:
           - difficulty_level: beginner, intermediate, advanced, graduate
           - format: online, in_person, hybrid
           - semester: fall, spring, summer
           - credits: number of credits
        7. INFORMATION_TYPE: What information is being requested:
           - syllabus, assignments, schedule, prerequisites, grading_policy, textbooks, overview

        Respond in this EXACT format:
        COURSE_CODES: [list of codes or empty]
        COURSE_NAMES: [list of names or empty]
        DEPARTMENTS: [list of departments or empty]
        INSTRUCTORS: [list of instructors or empty]
        TOPICS: [list of topics or empty]
        DIFFICULTY: [level or empty]
        FORMAT: [format or empty]
        SEMESTER: [semester or empty]
        CREDITS: [number or empty]
        INFO_TYPE: [type or empty]

        Example:
        Query: "Show me the syllabus for CS101 and assignments for Data Structures"
        COURSE_CODES: CS101
        COURSE_NAMES: Data Structures
        DEPARTMENTS:
        INSTRUCTORS:
        TOPICS:
        DIFFICULTY:
        FORMAT:
        SEMESTER:
        CREDITS:
        INFO_TYPE: syllabus, assignments
        """

        response = get_analysis_llm().invoke([HumanMessage(content=ner_prompt)])

        # Track LLM usage
        llm_calls = state.get("llm_calls", {}).copy()
        llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1

        # Parse response
        response_content = response.content.strip()
        entities = {
            "course_codes": [],
            "course_names": [],
            "departments": [],
            "instructors": [],
            "topics": [],
            "metadata_filters": {},
            "information_type": [],
        }

        for line in response_content.split("\n"):
            line = line.strip()
            if not line or ":" not in line:
                continue

            key, value = line.split(":", 1)
            value = value.strip()

            if not value or value.lower() in ["empty", "none", "[]"]:
                continue

            if key == "COURSE_CODES":
                entities["course_codes"] = [
                    c.strip() for c in value.split(",") if c.strip()
                ]
            elif key == "COURSE_NAMES":
                entities["course_names"] = [
                    n.strip() for n in value.split(",") if n.strip()
                ]
            elif key == "DEPARTMENTS":
                entities["departments"] = [
                    d.strip() for d in value.split(",") if d.strip()
                ]
            elif key == "INSTRUCTORS":
                entities["instructors"] = [
                    i.strip() for i in value.split(",") if i.strip()
                ]
            elif key == "TOPICS":
                entities["topics"] = [t.strip() for t in value.split(",") if t.strip()]
            elif key == "DIFFICULTY":
                entities["metadata_filters"]["difficulty_level"] = value.lower()
            elif key == "FORMAT":
                entities["metadata_filters"]["format"] = value.lower()
            elif key == "SEMESTER":
                entities["metadata_filters"]["semester"] = value.lower()
            elif key == "CREDITS":
                try:
                    entities["metadata_filters"]["credits"] = int(value)
                except ValueError:
                    pass
            elif key == "INFO_TYPE":
                entities["information_type"] = [
                    t.strip() for t in value.split(",") if t.strip()
                ]

        # Determine search strategy
        search_strategy = "semantic_only"  # default
        if entities["course_codes"]:
            search_strategy = "exact_match"  # Exact course codes found
        elif entities["course_names"] or entities["departments"]:
            search_strategy = "hybrid"  # Mix of exact and semantic

        logger.info(f"🔍 Extracted entities:")
        logger.info(f"   Course codes: {entities['course_codes']}")
        logger.info(f"   Course names: {entities['course_names']}")
        logger.info(f"   Departments: {entities['departments']}")
        logger.info(f"   Topics: {entities['topics']}")
        logger.info(f"   Metadata filters: {entities['metadata_filters']}")
        logger.info(f"   Information type: {entities['information_type']}")
        logger.info(f"   Search strategy: {search_strategy}")

        latency = (time.perf_counter() - start_time) * 1000
        logger.info(f"🔍 Entity extraction complete in {latency:.2f}ms")

        return {
            **state,
            "extracted_entities": entities,
            "search_strategy": search_strategy,
            "exact_matches": entities["course_codes"],
            "metadata_filters": entities["metadata_filters"],
            "llm_calls": llm_calls,
            "execution_path": state["execution_path"] + ["entities_extracted"],
        }

    except Exception as e:
        logger.error(f"❌ Entity extraction failed: {e}")
        # Fallback to semantic-only search
        return {
            **state,
            "extracted_entities": {
                "course_codes": [],
                "course_names": [],
                "departments": [],
                "instructors": [],
                "topics": [],
                "metadata_filters": {},
                "information_type": [],
            },
            "search_strategy": "semantic_only",
            "exact_matches": [],
            "metadata_filters": {},
            "execution_path": state["execution_path"] + ["entities_extracted"],
        }


def check_cache_node(state: WorkflowState) -> WorkflowState:
    """
    Check semantic cache for existing answers to sub-questions.

    NOTE: Semantic caching is COMMENTED OUT for now.
    This node currently just marks all questions as cache misses.
    Will be implemented in future stages.
    """
    start_time = time.perf_counter()
    sub_questions = state["sub_questions"]

    logger.info(
        f"🔍 Checking cache for {len(sub_questions)} sub-questions (CACHE DISABLED)"
    )

    # SEMANTIC CACHING COMMENTED OUT - Will be added later
    # Original implementation preserved below for reference

    cache_hits = 0
    for question in sub_questions:
        # For now, all questions are cache misses
        state["cache_hits"][question] = False
        state["cache_confidences"][question] = 0.0
        logger.info(f"   ❌ Cache MISS (disabled): '{question[:40]}...'")

    # Update metrics
    cache_time = (time.perf_counter() - start_time) * 1000
    hit_rate = 0.0  # Always 0 since caching is disabled

    state["metrics"]["cache_latency"] = cache_time
    state["metrics"]["cache_hit_rate"] = hit_rate
    state["metrics"]["cache_hits_count"] = cache_hits
    state["execution_path"].append("cache_checked")

    logger.info(
        f"🔍 Cache check complete: {cache_hits}/{len(sub_questions)} hits ({hit_rate:.1f}%) in {cache_time:.2f}ms"
    )

    return state


# ORIGINAL SEMANTIC CACHE IMPLEMENTATION (COMMENTED OUT):
# """
# def check_cache_node(state: WorkflowState) -> WorkflowState:
#     start_time = time.perf_counter()
#     sub_questions = state["sub_questions"]
#
#     logger.info(f"🔍 Checking cache for {len(sub_questions)} sub-questions")
#
#     cache_hits = 0
#     for question in sub_questions:
#         if state["cache_enabled"]:
#             try:
#                 cache_results = semantic_cache.check(question, num_results=1)
#
#                 if cache_results:
#                     cached_entry = cache_results[0]
#                     confidence = 1.0 - cached_entry.get("vector_distance", 1.0)
#
#                     state["cache_hits"][question] = True
#                     state["cache_confidences"][question] = confidence
#                     state["sub_answers"][question] = cached_entry["response"]
#                     cache_hits += 1
#
#                     logger.info(f"   ✅ Cache HIT: '{question[:40]}...' (confidence: {confidence:.3f})")
#                 else:
#                     state["cache_hits"][question] = False
#                     state["cache_confidences"][question] = 0.0
#                     logger.info(f"   ❌ Cache MISS: '{question[:40]}...'")
#             except Exception as e:
#                 logger.warning(f"Cache check failed for '{question[:40]}...': {e}")
#                 state["cache_hits"][question] = False
#                 state["cache_confidences"][question] = 0.0
#         else:
#             state["cache_hits"][question] = False
#             state["cache_confidences"][question] = 0.0
#
#     cache_time = (time.perf_counter() - start_time) * 1000
#     hit_rate = (cache_hits / len(sub_questions)) * 100 if sub_questions else 0
#
#     state["metrics"]["cache_latency"] = cache_time
#     state["metrics"]["cache_hit_rate"] = hit_rate
#     state["metrics"]["cache_hits_count"] = cache_hits
#     state["execution_path"].append("cache_checked")
#
#     logger.info(f"🔍 Cache check complete: {cache_hits}/{len(sub_questions)} hits ({hit_rate:.1f}%) in {cache_time:.2f}ms")
#
#     return state
# """


def research_node(state: WorkflowState) -> WorkflowState:
    """
    Research sub-questions using hybrid search.

    NEW in Stage 4: Uses extracted entities for intelligent search:
    - Exact match for course codes
    - Hybrid search for course names + semantic
    - Metadata filtering for departments, difficulty, etc.
    - Respects intent from intent classification
    """
    start_time = time.perf_counter()
    cache_hits = state.get("cache_hits", {})
    sub_answers = state.get("sub_answers", {}).copy()
    research_iterations = state.get("research_iterations", {}).copy()
    questions_researched = 0

    # Get intent and search strategy from state
    intent = state.get("query_intent", "GENERAL")
    search_strategy = state.get("search_strategy", "semantic_only")
    extracted_entities = state.get("extracted_entities", {})
    metadata_filters = state.get("metadata_filters", {})

    # Track LLM usage
    llm_calls = state.get("llm_calls", {}).copy()

    logger.info(
        f"🔬 Research: Starting hybrid search (strategy={search_strategy}, intent={intent})"
    )

    try:
        for sub_question, is_cached in cache_hits.items():
            if not is_cached:
                iteration = research_iterations.get(sub_question, 0) + 1
                current_strategy = state.get("current_research_strategy", {}).get(
                    sub_question, "initial"
                )

                logger.info(
                    f"🔍 Researching: '{sub_question[:50]}...' (iteration {iteration}, strategy: {current_strategy})"
                )

                # Use hybrid search with extracted entities
                search_results = search_courses_sync(
                    query=sub_question,
                    top_k=5,
                    intent=intent,
                    search_strategy=search_strategy,
                    extracted_entities=extracted_entities,
                    metadata_filters=metadata_filters,
                )

                # Format the answer
                if search_results and "No relevant courses found" not in search_results:
                    answer = f"Found relevant courses:\n\n{search_results}"
                else:
                    answer = "No relevant courses found for this question."

                sub_answers[sub_question] = answer
                research_iterations[sub_question] = iteration
                questions_researched += 1

                # Track LLM usage (just for embeddings)
                llm_calls["research_llm"] = llm_calls.get("research_llm", 0) + 1

                logger.info(
                    f"   ✅ Research complete (iteration {iteration}): '{answer[:50]}...'"
                )

        # Update state
        state["sub_answers"] = sub_answers
        state["research_iterations"] = research_iterations
        state["llm_calls"] = llm_calls
        state["execution_path"].append("researched")

        # Update metrics
        research_time = (time.perf_counter() - start_time) * 1000
        state["metrics"]["research_latency"] = research_time
        state["metrics"]["questions_researched"] = questions_researched

        logger.info(
            f"🔬 Research complete: {questions_researched} questions researched in {research_time:.2f}ms"
        )

        return state

    except Exception as e:
        logger.error(f"Research failed: {e}")
        import traceback

        traceback.print_exc()
        state["execution_path"].append("research_failed")
        return state


def evaluate_quality_node(state: WorkflowState) -> WorkflowState:
    """Evaluate the quality of research results."""
    start_time = time.perf_counter()
    sub_answers = state.get("sub_answers", {})
    quality_scores = {}

    logger.info(
        f"🎯 Quality Evaluation: Evaluating research quality for {len(sub_answers)} answers"
    )

    # Track LLM usage
    llm_calls = state.get("llm_calls", {}).copy()

    try:
        needs_improvement = 0

        for question, answer in sub_answers.items():
            # Skip quality evaluation for cached answers
            if state["cache_hits"].get(question, False):
                quality_scores[question] = 1.0
                continue

            # Evaluate research quality
            evaluation_prompt = f"""
            Evaluate the quality of this course search answer on a scale of 0.0 to 1.0.

            Question: {question}
            Answer: {answer}

            Criteria:
            - Completeness: Does it fully answer the question?
            - Accuracy: Is the course information correct and relevant?
            - Relevance: Does it directly address what was asked?
            - Grounding: Does it provide specific course details and stick to facts, not general knowledge?

            Respond with only a number between 0.0 and 1.0 (e.g., 0.85)
            """

            response = get_analysis_llm().invoke(
                [HumanMessage(content=evaluation_prompt)]
            )
            llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1

            try:
                score = float(response.content.strip())
                score = max(0.0, min(1.0, score))
            except ValueError:
                score = 0.8

            quality_scores[question] = score

            if score < 0.7:
                needs_improvement += 1
                logger.info(
                    f"   📊 {question[:40]}... - Score: {score:.2f} - Needs improvement"
                )
            else:
                logger.info(f"   ✅ {question[:40]}... - Score: {score:.2f} - Adequate")

        # Update state
        state["research_quality_scores"] = quality_scores
        state["llm_calls"] = llm_calls
        state["execution_path"].append("quality_evaluated")

        # Update metrics
        evaluation_time = (time.perf_counter() - start_time) * 1000

        logger.info(f"🎯 Quality evaluation complete in {evaluation_time:.2f}ms")
        logger.info(f"📊 {needs_improvement} sub-questions need additional research")

        return state

    except Exception as e:
        logger.error(f"Quality evaluation failed: {e}")
        for question in sub_answers:
            state["research_quality_scores"][question] = 0.8
        state["execution_path"].append("quality_evaluated")
        return state


def synthesize_response_node(state: WorkflowState) -> WorkflowState:
    """
    Synthesize final response from all sub-answers.

    NEW in Stage 4: Adapts synthesis based on search strategy and information type.
    """
    start_time = time.perf_counter()
    original_query = state["original_query"]
    sub_questions = state["sub_questions"]
    sub_answers = state["sub_answers"]
    search_strategy = state.get("search_strategy", "semantic_only")
    extracted_entities = state.get("extracted_entities", {})

    logger.info(
        f"🔗 Synthesizing {len(sub_answers)} answers (strategy={search_strategy})"
    )

    # Track LLM usage
    llm_calls = state.get("llm_calls", {}).copy()

    try:
        # NOTE: Semantic cache storage commented out for now
        # Will be added in future stages

        # Create synthesis prompt
        if len(sub_questions) == 1:
            # Single question - adapt based on search strategy
            answer = sub_answers.get(sub_questions[0], "No answer available")

            # NEW in Stage 4: Add context about search strategy
            if search_strategy == "exact_match":
                # For exact matches, be direct and concise
                synthesis_context = "This is an exact match for the requested course."
            elif extracted_entities.get("information_type"):
                # For specific info requests, focus on that information
                info_types = extracted_entities["information_type"]
                synthesis_context = f"Focus on providing: {', '.join(info_types)}"
            else:
                synthesis_context = "Provide a comprehensive overview."

            # Check if we have course data
            if "No courses found" in answer or len(answer.strip()) < 50:
                # No courses found - acknowledge and redirect
                final_response = f"""I searched our course catalog for information about "{original_query}", but I couldn't find any courses that match.

Our catalog includes courses in Computer Science, Mathematics, Data Science, and related fields. Would you like me to:
- Show you available courses in a specific department?
- Help you find courses on a related topic?
- List popular courses?

Just let me know what you're interested in!"""
            elif search_strategy == "exact_match" or len(answer) < 500:
                # Simple answer - return directly
                final_response = answer
            else:
                # Otherwise, synthesize with context
                synthesis_prompt = f"""
                Original question: {original_query}

                Context: {synthesis_context}

                Course information from our catalog:
                {answer}

                IMPORTANT:
                - Base your response ONLY on the course information provided above
                - If the course information doesn't fully answer the question, acknowledge what's available and what's not
                - Always tie your response back to the actual courses in our catalog
                - Do NOT provide generic educational content - focus on OUR specific courses
                - If specific information was requested (assignments, syllabus, etc.), focus on that

                Provide a clear, well-structured response that addresses the question using the course data.
                Be concise for exact matches, comprehensive for exploratory queries.
                """

                response = get_analysis_llm().invoke(
                    [HumanMessage(content=synthesis_prompt)]
                )
                llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1
                final_response = response.content
        else:
            # Multiple questions - synthesize
            qa_pairs = []
            for i, question in enumerate(sub_questions, 1):
                answer = sub_answers.get(question, "No answer available")
                qa_pairs.append(f"Q{i}: {question}\nA{i}: {answer}")

            # Adapt synthesis based on search strategy
            if search_strategy == "exact_match":
                synthesis_instruction = "Provide direct, concise answers for each specific course requested."
            elif extracted_entities.get("information_type"):
                info_types = extracted_entities["information_type"]
                synthesis_instruction = (
                    f"Focus on providing: {', '.join(info_types)} for each course."
                )
            else:
                synthesis_instruction = (
                    "Synthesize into a comprehensive, well-structured response."
                )

            # Check if we have meaningful course data
            has_courses = any(
                "No courses found" not in sub_answers.get(q, "") for q in sub_questions
            )

            if not has_courses:
                # No courses found - acknowledge and redirect
                final_response = f"""I searched our course catalog for information about "{original_query}", but I couldn't find any courses that match.

Our catalog includes courses in Computer Science, Mathematics, Data Science, and related fields. Would you like me to:
- Show you available courses in a specific department?
- Help you find courses on a related topic?
- List popular courses?

Just let me know what you're interested in!"""
            else:
                synthesis_prompt = f"""
                Original question: {original_query}

                Course search findings from our catalog:
                {chr(10).join(qa_pairs)}

                IMPORTANT:
                - Base your response ONLY on the course information provided above
                - If the course information doesn't fully answer the question, acknowledge what's available
                - Always tie your response back to the actual courses in our catalog
                - Do NOT provide generic educational content - focus on OUR specific courses
                - {synthesis_instruction}

                Be conversational and helpful while ensuring all key course information is included.
                """

                response = get_analysis_llm().invoke(
                    [HumanMessage(content=synthesis_prompt)]
                )
                llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1
                final_response = response.content

        # Update state
        state["final_response"] = final_response
        state["llm_calls"] = llm_calls
        state["execution_path"].append("synthesized")

        # Update metrics
        synthesis_time = (time.perf_counter() - start_time) * 1000
        state["metrics"]["synthesis_latency"] = synthesis_time

        logger.info(f"🔗 Response synthesized in {synthesis_time:.2f}ms")
        logger.info(f"📝 Final response: {final_response[:100]}...")

        return state

    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        state["final_response"] = f"Error synthesizing response: {e}"
        state["execution_path"].append("synthesis_failed")
        return state


def handle_greeting_node(state: WorkflowState) -> WorkflowState:
    """Handle greetings and non-course queries without course search."""
    start_time = time.perf_counter()
    query = state["original_query"]

    logger.info(f"👋 Handling greeting/non-course query: '{query[:50]}...'")

    try:
        greeting_prompt = f"""
        The user sent this message: {query}

        Respond naturally and helpfully. If it's a greeting, greet them back and let them know you're a course advisor agent that can help them find courses, view syllabi, check prerequisites, etc.

        Keep it brief and friendly (2-3 sentences max).
        """

        response = get_analysis_llm().invoke([HumanMessage(content=greeting_prompt)])

        # Track LLM usage
        llm_calls = state.get("llm_calls", {}).copy()
        llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1

        final_response = response.content.strip()

        logger.info(f"👋 Greeting response: {final_response[:100]}...")

        latency = (time.perf_counter() - start_time) * 1000

        return {
            **state,
            "final_response": final_response,
            "llm_calls": llm_calls,
            "execution_path": state.get("execution_path", []) + ["greeting_handled"],
            "metrics": {
                **state.get("metrics", {}),
                "total_latency": latency,
            },
        }

    except Exception as e:
        logger.error(f"❌ Greeting handling failed: {e}")
        return {
            **state,
            "final_response": "Hello! I'm a course advisor agent. I can help you find courses, view syllabi, check prerequisites, and more. What would you like to know?",
            "execution_path": state.get("execution_path", []) + ["greeting_failed"],
        }
