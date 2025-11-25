"""
Workflow nodes for the Course Q&A Agent.

Adapted from caching-agent to use CourseManager for course search.
Semantic caching is commented out for now - will be added later.
"""

import time
import logging
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from .state import WorkflowState, initialize_metrics
from .tools import search_courses, search_courses_sync

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
        _analysis_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=400)
    return _analysis_llm


def get_research_llm():
    """Get the configured research LLM instance."""
    global _research_llm
    if _research_llm is None:
        _research_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, max_tokens=800)
    return _research_llm


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
        
        response = get_analysis_llm().invoke([HumanMessage(content=decomposition_prompt)])
        
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
                if line.strip() and not line.strip().startswith(("1.", "2.", "3.", "4.", "-", "*"))
                and line.strip() != "SINGLE_QUESTION"
            ]
            
            if not sub_questions or len(sub_questions) == 1:
                sub_questions = [query]
            elif len(sub_questions) > 4:
                sub_questions = sub_questions[:4]
            
            logger.info(f"🧠 Decomposed into {len(sub_questions)} sub-questions in {(time.perf_counter() - start_time) * 1000:.2f}ms")
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


def check_cache_node(state: WorkflowState) -> WorkflowState:
    """
    Check semantic cache for existing answers to sub-questions.
    
    NOTE: Semantic caching is COMMENTED OUT for now.
    This node currently just marks all questions as cache misses.
    Will be implemented in future stages.
    """
    start_time = time.perf_counter()
    sub_questions = state["sub_questions"]
    
    logger.info(f"🔍 Checking cache for {len(sub_questions)} sub-questions (CACHE DISABLED)")
    
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
    
    logger.info(f"🔍 Cache check complete: {cache_hits}/{len(sub_questions)} hits ({hit_rate:.1f}%) in {cache_time:.2f}ms")
    
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
    Research sub-questions using course search.

    Uses CourseManager.search_courses() to find relevant courses.
    Simplified version that directly calls search without ReAct agent.
    """
    start_time = time.perf_counter()
    cache_hits = state.get("cache_hits", {})
    sub_answers = state.get("sub_answers", {}).copy()
    research_iterations = state.get("research_iterations", {}).copy()
    questions_researched = 0

    # Track LLM usage
    llm_calls = state.get("llm_calls", {}).copy()

    logger.info("🔬 Research: Starting course search")

    try:
        for sub_question, is_cached in cache_hits.items():
            if not is_cached:
                iteration = research_iterations.get(sub_question, 0) + 1
                current_strategy = state.get("current_research_strategy", {}).get(sub_question, "initial")

                logger.info(f"🔍 Researching: '{sub_question[:50]}...' (iteration {iteration}, strategy: {current_strategy})")

                # Directly search for courses using synchronous wrapper
                search_results = search_courses_sync(sub_question, top_k=5)

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

                logger.info(f"   ✅ Research complete (iteration {iteration}): '{answer[:50]}...'")

        # Update state
        state["sub_answers"] = sub_answers
        state["research_iterations"] = research_iterations
        state["llm_calls"] = llm_calls
        state["execution_path"].append("researched")

        # Update metrics
        research_time = (time.perf_counter() - start_time) * 1000
        state["metrics"]["research_latency"] = research_time
        state["metrics"]["questions_researched"] = questions_researched

        logger.info(f"🔬 Research complete: {questions_researched} questions researched in {research_time:.2f}ms")

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

    logger.info(f"🎯 Quality Evaluation: Evaluating research quality for {len(sub_answers)} answers")

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

            response = get_analysis_llm().invoke([HumanMessage(content=evaluation_prompt)])
            llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1

            try:
                score = float(response.content.strip())
                score = max(0.0, min(1.0, score))
            except ValueError:
                score = 0.8

            quality_scores[question] = score

            if score < 0.7:
                needs_improvement += 1
                logger.info(f"   📊 {question[:40]}... - Score: {score:.2f} - Needs improvement")
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
    """Synthesize final response from all sub-answers."""
    start_time = time.perf_counter()
    original_query = state["original_query"]
    sub_questions = state["sub_questions"]
    sub_answers = state["sub_answers"]

    logger.info(f"🔗 Synthesizing {len(sub_answers)} answers into final response")

    # Track LLM usage
    llm_calls = state.get("llm_calls", {}).copy()

    try:
        # NOTE: Semantic cache storage commented out for now
        # Will be added in future stages

        # Create synthesis prompt
        if len(sub_questions) == 1:
            # Single question - return answer directly
            final_response = sub_answers.get(sub_questions[0], "No answer available")
        else:
            # Multiple questions - synthesize
            qa_pairs = []
            for i, question in enumerate(sub_questions, 1):
                answer = sub_answers.get(question, "No answer available")
                qa_pairs.append(f"Q{i}: {question}\nA{i}: {answer}")

            synthesis_prompt = f"""
            Original question: {original_query}

            Course search findings:
            {chr(10).join(qa_pairs)}

            Synthesize these findings into a comprehensive, well-structured response that fully addresses the original question.
            Be conversational and helpful while ensuring all key course information is included.
            """

            response = get_analysis_llm().invoke([HumanMessage(content=synthesis_prompt)])
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

