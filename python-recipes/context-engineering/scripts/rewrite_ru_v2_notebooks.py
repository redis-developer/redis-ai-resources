import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from pathlib import Path

root = Path("python-recipes/context-engineering/notebooks/ru-v2")

# 00_onboarding
nb0 = new_notebook(
    cells=[
        new_markdown_cell(
            """# Lab: Onboarding (Health checks and smoke test)

In this lab you will:
- Load environment variables from .env (including OPENAI_API_KEY)
- Verify Redis and Agent Memory Server health
- Run a one-question smoke test with the ClassAgent
"""
        ),
        new_code_cell(
            """
# 1) Load environment variables from .env (no external dependency)
import os, pathlib
from IPython.display import Markdown, display

def load_env(dotenv_path='.env'):
    p = pathlib.Path(dotenv_path)
    if not p.exists():
        return 0
    loaded = 0
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k, v = k.strip(), v.strip()
        v = v.strip(chr(34))
        v = v.strip("'")
        if k and v and k not in os.environ:
            os.environ[k] = v
            loaded += 1
    return loaded

loaded = load_env()
display(Markdown('Loaded ' + str(loaded) + ' variables from .env. Using OPENAI_MODEL=' + os.getenv('OPENAI_MODEL','gpt-4o')))
"""
        ),
        new_code_cell(
            """
# 2) Health checks: Redis and Agent Memory Server
import os, socket, urllib.request, json

def check_redis(host='localhost', port=6379):
    try:
        import redis
        r = redis.Redis(host=host, port=port, decode_responses=True)
        return bool(r.ping())
    except Exception:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except Exception:
            return False

def check_memory_server(url=None):
    if url is None:
        url = os.getenv('AGENT_MEMORY_URL','http://localhost:8088')
    try:
        with urllib.request.urlopen(url.rstrip('/') + '/v1/health', timeout=2) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get('status') in ('ok','healthy')
    except Exception:
        return False

redis_ok = check_redis()
mem_ok = check_memory_server()
display(Markdown('Redis: ' + ('✅' if redis_ok else '❌') + ' | Agent Memory Server: ' + ('✅' if mem_ok else '❌')))
if not mem_ok:
    display(Markdown('> If the Agent Memory Server is not running, start it in a terminal: `agent-memory api --host 0.0.0.0 --port 8088 --no-worker`'))
if not redis_ok:
    display(Markdown('> If Redis is not running, start it (e.g., Docker): `docker run -d --name redis -p 6379:6379 redis:8-alpine`'))
"""
        ),
        new_code_cell(
            """
# 3) Reference Agent smoke test (single turn)
import sys, asyncio
from pathlib import Path
from IPython.display import Markdown, display

# Ensure we can import the reference agent without pip-installing the package
base = Path.cwd()
for _ in range(8):
    cand = base / 'python-recipes' / 'context-engineering' / 'reference-agent'
    if cand.exists():
        ref_agent_path = cand
        break
    base = base.parent
else:
    raise FileNotFoundError('reference-agent not found')
if str(ref_agent_path) not in sys.path:
    sys.path.insert(0, str(ref_agent_path))

try:
    from redis_context_course.agent import ClassAgent
    student_id = 'ru_onboarding'
    agent = ClassAgent(student_id=student_id)
    answer = asyncio.run(agent.chat('Recommend 2 data science courses'))
    display(Markdown('**Agent reply:**\\n\\n' + str(answer)))
except Exception as e:
    display(Markdown('**Agent error:** ' + str(e)))
"""
        ),
    ],
    metadata={
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python'},
    },
)

# 01_fundamentals
nb1 = new_notebook(
    cells=[
        new_markdown_cell(
            """# Lab: Fundamentals (Baseline vs minimal context)

Goal: compare the same task with and without minimal system context, and log time/token deltas.
"""
        ),
        new_code_cell(
            """
# Load .env (minimal)
import os, pathlib, time
from IPython.display import Markdown, display

def load_env(p='.env'):
    pth = pathlib.Path(p)
    if not pth.exists():
        return 0
    n=0
    for ln in pth.read_text().splitlines():
        ln=ln.strip()
        if not ln or ln.startswith('#') or '=' not in ln: continue
        k,v=ln.split('=',1); k=k.strip(); v=v.strip()
        v = v.strip(chr(34))
        v = v.strip("'")
        if k and v and k not in os.environ: os.environ[k]=v; n+=1
    return n
_=load_env()
display(Markdown('Environment loaded.'))
"""
        ),
        new_code_cell(
            """
# Baseline vs minimal context
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    prompt = 'Recommend 2 AI courses and explain why briefly.'
    model = ChatOpenAI(model=os.getenv('OPENAI_MODEL','gpt-4o-mini'), temperature=0)
    def run(messages):
        t0=time.time(); resp = model.invoke(messages); dt=time.time()-t0
        usage = getattr(resp, 'response_metadata', {}).get('token_usage') or getattr(resp, 'usage_metadata', None) or {}
        return resp.content, dt, usage
    baseline_messages = [HumanMessage(content=prompt)]
    b_out, b_dt, b_usage = run(baseline_messages)
    sys_text = ('You recommend university courses. If uncertain, ask a concise clarifying question. ' , 'Prefer concrete course titles and avoid fluff.')
    sys_text = ' '.join(sys_text)
    ctx_messages = [SystemMessage(content=sys_text), HumanMessage(content=prompt)]
    c_out, c_dt, c_usage = run(ctx_messages)
    display(Markdown('**Baseline output:**\\n\\n' + b_out))
    display(Markdown('**Minimal context output:**\\n\\n' + c_out))
    display(Markdown('Time (s): baseline=' + str(round(b_dt,2)) + ', minimal=' + str(round(c_dt,2))))
    display(Markdown('Token usage (if available): baseline=' + str(b_usage) + ', minimal=' + str(c_usage)))
except Exception as e:
    display(Markdown('**Skipped (missing deps or API):** ' + str(e)))
"""
        ),
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

# 02_system_and_tools
nb2 = new_notebook(
    cells=[
        new_markdown_cell(
            """# Lab: System instructions and tools (exercise existing tools)

We will send targeted prompts to the reference agent and observe behavior for:
- Listing majors
- Course search
- User profile summary (memory)
"""
        ),
        new_code_cell(
            """
# Load .env and prepare imports
import os, pathlib, sys, asyncio
from IPython.display import Markdown, display

def load_env(p='.env'):
    try:
        txt=pathlib.Path(p).read_text()
    except FileNotFoundError:
        return 0
    n=0
    for ln in txt.splitlines():
        ln=ln.strip()
        if not ln or ln.startswith('#') or '=' not in ln: continue
        k,v=ln.split('=',1); k=k.strip(); v=v.strip()
        v = v.strip(chr(34))
        v = v.strip("'")
        if k and v and k not in os.environ: os.environ[k]=v; n+=1
    return n
_=load_env()

# Import reference agent without pip installing
try:
    base = pathlib.Path.cwd()
    for _ in range(8):
        cand = base / 'python-recipes' / 'context-engineering' / 'reference-agent'
        if cand.exists():
            ref_agent_path = cand
            break
        base = base.parent
    else:
        raise FileNotFoundError('reference-agent not found')
    if str(ref_agent_path) not in sys.path:
        sys.path.insert(0, str(ref_agent_path))
    from redis_context_course.agent import ClassAgent
    agent = ClassAgent(student_id='ru_tools')
    async def ask(q):
        ans = await agent.chat(q)
        display(Markdown('**User:** ' + q + '\\n\\n**Agent:**\\n\\n' + str(ans)))
    asyncio.run(ask('what majors are available?'))
    asyncio.run(ask('show me cs courses'))
    asyncio.run(ask('what do you know about me?'))
except Exception as e:
    display(Markdown('**Skipped (missing deps or API):** ' + str(e)))
"""
        ),
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

# 03_memory
nb3 = new_notebook(
    cells=[
        new_markdown_cell(
            """# Lab: Memory (working + long-term)

We will:
1) Verify Agent Memory Server health
2) Use the agent to store a preference (LTM)
3) Ask for a user summary (reads LTM)
4) Show cross-session persistence
"""
        ),
        new_code_cell(
            """
# Load .env and prepare imports
import os, sys, pathlib, asyncio, json, urllib.request
from IPython.display import Markdown, display

def load_env(p='.env'):
    try: txt=pathlib.Path(p).read_text()
    except FileNotFoundError: return 0
    n=0
    for ln in txt.splitlines():
        ln=ln.strip()
        if not ln or ln.startswith('#') or '=' not in ln: continue
        k,v=ln.split('=',1); k=k.strip(); v=v.strip()
        v = v.strip(chr(34))
        v = v.strip("'")
        if k and v and k not in os.environ: os.environ[k]=v; n+=1
    return n
_=load_env()

def mem_health(url=None):
    if url is None:
        url = os.getenv('AGENT_MEMORY_URL','http://localhost:8088')
    try:
        with urllib.request.urlopen(url.rstrip('/')+'/v1/health', timeout=2) as r:
            return json.loads(r.read().decode()).get('status') in ('ok','healthy')
    except Exception:
        return False

ok = mem_health()
display(Markdown('Agent Memory Server health: ' + ('OK' if ok else 'NOT AVAILABLE')))
if not ok:
    display(Markdown('> Start it: `agent-memory api --host 0.0.0.0 --port 8088 --no-worker`'))

# Import agent
base = pathlib.Path.cwd()
for _ in range(8):
    cand = base / 'python-recipes' / 'context-engineering' / 'reference-agent'
    if cand.exists():
        ref_agent_path = cand
        break
    base = base.parent
else:
    raise FileNotFoundError('reference-agent not found')
if str(ref_agent_path) not in sys.path:
    sys.path.insert(0, str(ref_agent_path))
from redis_context_course.agent import ClassAgent

student = 'ru_memory_demo'
if not os.getenv('OPENAI_API_KEY'):
    display(Markdown('Skipped memory demo: OPENAI_API_KEY not set'))
    skip_memory_demo = True
else:
    skip_memory_demo = False
    agent_a = ClassAgent(student_id=student, session_id='s1')
    agent_b = ClassAgent(student_id=student, session_id='s2')

async def run_memory_flow():
    _ = await agent_a.chat('I am interested in math and engineering. Recommend 2 courses.')
    summary = await agent_b.chat('what do you know about me?')
    return summary

try:
    if not skip_memory_demo:
        summary = asyncio.run(run_memory_flow())
        display(Markdown('**User summary (from LTM):**\\n\\n' + str(summary)))
except Exception as e:
    display(Markdown('**Skipped (missing deps or API):** ' + str(e)))
"""
        ),
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

# 04_retrieval
nb4 = new_notebook(
    cells=[
        new_markdown_cell(
            """# Lab: Retrieval and Grounding

We will:
1) Ingest a small subset of the course catalog into Redis (vector index)
2) Run a semantic search query
3) Ask the agent for recommendations (grounded by the index)
"""
        ),
        new_code_cell(
            """
# Load .env and imports
import os, json, asyncio, pathlib, sys
from IPython.display import Markdown, display

def load_env(p='.env'):
    try: txt=pathlib.Path(p).read_text()
    except FileNotFoundError: return 0
    for ln in txt.splitlines():
        ln=ln.strip()
        if not ln or ln.startswith('#') or '=' not in ln: continue
        k,v=ln.split('=',1); k=k.strip(); v=v.strip()
        v = v.strip(chr(34))
        v = v.strip("'")
        if k and v and k not in os.environ: os.environ[k]=v

_ = load_env()

base = pathlib.Path.cwd()
for _ in range(8):
    cand = base / 'python-recipes' / 'context-engineering' / 'reference-agent'
    if cand.exists():
        ref_agent = cand
        break
    base = base.parent
else:
    raise FileNotFoundError('reference-agent not found')
if str(ref_agent) not in sys.path:
    sys.path.insert(0, str(ref_agent))
from redis_context_course.course_manager import CourseManager
from redis_context_course.redis_config import redis_config
from redis_context_course.models import Course, DifficultyLevel, CourseFormat, Semester, Prerequisite, CourseSchedule, DayOfWeek
from redis_context_course.agent import ClassAgent

display(Markdown('Environment ready.'))
"""
        ),
        new_code_cell(
            """
# Ingest a small subset of the catalog
catalog_path = ref_agent / 'course_catalog.json'
data = json.loads(catalog_path.read_text())
majors = data.get('majors', [])[:5]
courses = data.get('courses', [])[:25]

r = redis_config.redis_client
for m in majors:
    key = 'major:' + m['id']
    r.hset(key, mapping={
        'id': m.get('id',''),
        'name': m.get('name',''),
        'code': m.get('code',''),
        'department': m.get('department',''),
        'description': m.get('description',''),
        'required_credits': m.get('required_credits', 0)
    })

skip_retrieval = False
if not os.getenv('OPENAI_API_KEY'):
    display(Markdown('Skipped ingestion: set OPENAI_API_KEY to enable embeddings.'))
    skip_retrieval = True
else:
    cm = CourseManager()

    def to_course(d):
        pres = [Prerequisite(**p) for p in d.get('prerequisites', [])]
        sch = d.get('schedule')
        sched = None
        if sch:
            sched = CourseSchedule(
                days=[DayOfWeek(x) for x in sch.get('days', [])],
                start_time=sch['start_time'],
                end_time=sch['end_time'],
                location=sch.get('location')
            )
        return Course(
            id=d.get('id'),
            course_code=d['course_code'],
            title=d['title'],
            description=d['description'],
            credits=int(d['credits']),
            difficulty_level=DifficultyLevel(d['difficulty_level']),
            format=CourseFormat(d['format']),
            department=d['department'],
            major=d['major'],
            prerequisites=pres,
            schedule=sched,
            semester=Semester(d['semester']),
            year=int(d['year']),
            instructor=d['instructor'],
            max_enrollment=int(d['max_enrollment']),
            current_enrollment=int(d.get('current_enrollment',0)),
            tags=d.get('tags',[]),
            learning_objectives=d.get('learning_objectives',[])
        )

    async def ingest_subset():
        count=0
        for c in courses:
            try:
                course = to_course(c)
                await cm.store_course(course)
                count+=1
            except Exception:
                pass
        return count

    ingested = asyncio.run(ingest_subset())
    display(Markdown('Ingested ' + str(ingested) + ' courses and ' + str(len(majors)) + ' majors (subset).'))
"""
        ),
        new_code_cell(
            """
# Semantic search demo
if not skip_retrieval:
    async def search_demo(q):
        res = await cm.search_courses(q, limit=5)
        return res
    res = asyncio.run(search_demo('machine learning'))
    fmt = []
    for c in res:
        fmt.append('**' + c.course_code + ': ' + c.title + '** | ' + c.department + ' | ' + c.difficulty_level.value)
    display(Markdown('**Search results (machine learning):**\\n\\n' + ('\\n\\n'.join(fmt) if fmt else 'No results')))
else:
    display(Markdown('Skipped search: ingestion was skipped.'))
"""
        ),
        new_code_cell(
            """
# Agent recommendation using the ingested index (skip gracefully if missing deps)
if not skip_retrieval:
    try:
        agent = ClassAgent(student_id='ru_retrieval_demo')
        ans = asyncio.run(agent.chat('Recommend 3 machine learning courses'))
        display(Markdown('**Agent:**\\n\\n' + str(ans)))
    except Exception as e:
        display(Markdown('**Skipped (missing deps or API):** ' + str(e)))
else:
    display(Markdown('Skipped agent recommendation: ingestion was skipped.'))
"""
        ),
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

# Write notebooks
out_files = [(root/"00_onboarding"/"02_lab.ipynb", nb0)]

# 05_orchestration
nb5c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Orchestration

In this module you learn how to orchestrate agent behavior:
- Routing strategies (keyword, intent, classifier)
- Tool enablement per node (loadouts) and constraints
- Graph topologies (linear, hub-and-spoke, router → worker, fallback)
- Timeouts and fallbacks (graceful degradation)
- Checkpointing and memory integration with Redis

Reading goals:
- Understand how a state graph executes nodes and transitions
- Know when to offload to tools vs. respond directly
- Design a safe fallback for timeouts or missing deps
"""
        )
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

nb5l = new_notebook(
    cells=[
        new_markdown_cell(
            """# Lab: Orchestration

We will build a tiny router graph. If LangGraph is not available, we show a minimal fallback.
Objectives:
- Implement a classifier node that routes to a stub tool
- Demonstrate a simple fallback when a node fails
- Run two example inputs and inspect the path
"""
        ),
        new_code_cell(
            """
# Common setup
import os, sys, pathlib, asyncio, time
from IPython.display import Markdown, display

# Load .env (minimal)
def load_env(p='.env'):
    try: txt=pathlib.Path(p).read_text()
    except FileNotFoundError: txt=''
    for ln in txt.splitlines():
        ln=ln.strip()
        if not ln or ln.startswith('#') or '=' not in ln: continue
        k,v=ln.split('=',1); k=k.strip(); v=v.strip()
        v = v.strip(chr(34)); v = v.strip("'")
        if k and v and k not in os.environ: os.environ[k]=v
_ = load_env()

# Try LangGraph
try:
    from langgraph.graph import StateGraph, END
    have_langgraph = True
except Exception:
    have_langgraph = False
            """
        ),
        new_code_cell(
            """
# A tiny router graph (pure stub tools)
if have_langgraph:
    from pydantic import BaseModel
    from typing import Annotated, List
    from langgraph.graph.message import add_messages
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

    class S(BaseModel):
        messages: Annotated[List[BaseMessage], add_messages]
        route: str = 'search'
        result: str = ''

    def classify(state: S) -> S:
        text = ' '.join([m.content for m in state.messages]).lower()
        if 'prereq' in text or 'eligible' in text:
            state.route = 'prereq'
        elif 'me' in text and ('know' in text or 'about' in text):
            state.route = 'profile'
        else:
            state.route = 'search'
        return state

    def tool_node(state: S) -> S:
        # Stub tools
        if state.route == 'search':
            state.result = 'StubSearch: CS101, DS201'
        elif state.route == 'prereq':
            state.result = 'StubPrereq: You meet prerequisites for CS301'
        else:
            state.result = 'StubProfile: You like math and engineering'
        return state

    def respond(state: S) -> S:
        state.messages.append(AIMessage(content=state.result))
        return state

    g = StateGraph(S)
    g.add_node('classify', classify)
    g.add_node('tool', tool_node)
    g.add_node('respond', respond)
    g.set_entry_point('classify')
    g.add_edge('classify', 'tool')
    g.add_edge('tool', 'respond')
    g.add_edge('respond', END)
    graph = g.compile()

    # Run examples
    inputs = [
        'find machine learning courses',
        'am I eligible for CS301?'
    ]
    for text in inputs:
        s = S(messages=[HumanMessage(content=text)])
        out = graph.invoke(s)
        last = ''
        try:
            msgs = out.get('messages', []) if hasattr(out, 'get') else out['messages']
            last = msgs[-1].content if msgs else ''
        except Exception:
            last = str(out)
        display(Markdown('**Input:** ' + text + '\\n\\n**Result:** ' + last))
else:
    display(Markdown('LangGraph not available. Showing fallback...'))
    def fallback_router(text: str) -> str:
        t = text.lower()
        if 'prereq' in t or 'eligible' in t: return 'StubPrereq: You meet prerequisites for CS301'
        if 'me' in t and ('know' in t or 'about' in t): return 'StubProfile: You like math and engineering'
        return 'StubSearch: CS101, DS201'
    for q in ['find machine learning courses', 'am I eligible for CS301?']:
        display(Markdown('**Input:** ' + q + '\\n\\n**Result:** ' + fallback_router(q)))
            """
        ),
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

# 06_optimizations
nb6c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Optimizations

Key techniques:
- Pruning and summarization to manage context windows
- Retrieval strategies and hybrid ranking
- Grounding with memory to resolve references
- Tool optimization (selective exposure)
- Caching and repetition handling

Outcome: Be able to cut tokens/time without hurting quality.
"""
        )
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

nb6l = new_notebook(
    cells=[
        new_markdown_cell(
            """# Lab: Optimizations

We will:
1) Compare baseline vs summarized prompt (skip gracefully if no API key)
2) Demonstrate simple tool selection filtering
"""
        ),
        new_code_cell(
            """
# Setup
import os, pathlib, time
from IPython.display import Markdown, display

def load_env(p='.env'):
    try: txt=pathlib.Path(p).read_text()
    except FileNotFoundError: txt=''
    for ln in txt.splitlines():
        ln=ln.strip()
        if not ln or ln.startswith('#') or '=' not in ln: continue
        k,v=ln.split('=',1); k=k.strip(); v=v.strip()
        v=v.strip(chr(34)); v=v.strip("'")
        if k and v and k not in os.environ: os.environ[k]=v
_ = load_env()
            """
        ),
        new_code_cell(
            """
# 1) Baseline vs summarized (tokens/latency if available)
try:
    from langchain_openai import ChatOpenAI
    model = ChatOpenAI(model=os.getenv('OPENAI_MODEL','gpt-4o-mini'), temperature=0)
    long_text = ' '.join(['This is a background paragraph about the university.']*20)
    prompt = f"Summarize in 3 bullets: {long_text}"
    t0=time.time(); resp1 = model.invoke(prompt); t1=time.time()-t0
    summary = ' '.join(resp1.content.split()[:40])  # local trim as a guard
    t0=time.time(); resp2 = model.invoke('Expand a bit: '+summary); t2=time.time()-t0
    u1 = getattr(resp1,'response_metadata',{}).get('token_usage') or getattr(resp1,'usage_metadata',None)
    u2 = getattr(resp2,'response_metadata',{}).get('token_usage') or getattr(resp2,'usage_metadata',None)
    display(Markdown('**Baseline (first pass) latency:** ' + str(round(t1,2)) + 's, usage=' + str(u1)))
    display(Markdown('**Summarized (second pass) latency:** ' + str(round(t2,2)) + 's, usage=' + str(u2)))
except Exception as e:
    display(Markdown('Skipped summarization demo: ' + str(e)))
            """
        ),
        new_code_cell(
            """
# 2) Tool selection filtering (keyword-based)
# Uses a simple helper that selects categories based on query
try:
    # No heavy deps required
    def select_tools_by_keywords(query: str, all_tools: dict):
        q = query.lower()
        if any(w in q for w in ['search','find','show','what','which','tell me about']):
            return all_tools.get('search', [])
        elif any(w in q for w in ['remember','recall','know about me','preferences']):
            return all_tools.get('memory', [])
        else:
            return all_tools.get('search', [])
    all_tools = {
        'search': ['search_courses','get_course_details'],
        'memory': ['write_memory','read_memory_summary']
    }
    for q in ['show me ml courses','what do you know about me?']:
        sel = select_tools_by_keywords(q, all_tools)
        display(Markdown('**Query:** ' + q + '\\n\\n**Selected tools:** ' + ', '.join(sel)))
except Exception as e:
    display(Markdown('Tool selection demo failed: ' + str(e)))
            """
        ),
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

# 07_production
nb7c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Production

- Health checks and readiness probes
- Tracing and correlation IDs
- Metrics and SLOs (latency, error rate)
- Eval loops and canaries
- Operational practices (rollbacks, configs)
"""
        )
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

nb7l = new_notebook(
    cells=[
        new_markdown_cell(
            """# Lab: Production

We will run health checks and a small latency sample. Skips gracefully without external services.
"""
        ),
        new_code_cell(
            """
import os, socket, json, urllib.request, asyncio, time, uuid, pathlib
from IPython.display import Markdown, display

def load_env(p='.env'):
    try: txt=pathlib.Path(p).read_text()
    except FileNotFoundError: txt=''
    for ln in txt.splitlines():
        ln=ln.strip()
        if not ln or ln.startswith('#') or '=' not in ln: continue
        k,v=ln.split('=',1); k=k.strip(); v=v.strip()
        v=v.strip(chr(34)); v=v.strip("'")
        if k and v and k not in os.environ: os.environ[k]=v
_ = load_env()

def redis_up(host='localhost', port=6379):
    try:
        import redis
        return bool(redis.Redis(host=host, port=port).ping())
    except Exception:
        try:
            with socket.create_connection((host,port), timeout=1):
                return True
        except Exception:
            return False

def memory_ok(url=None):
    url = url or os.getenv('AGENT_MEMORY_URL','http://localhost:8088')
    try:
        with urllib.request.urlopen(url.rstrip('/')+'/v1/health', timeout=2) as r:
            return json.loads(r.read().decode()).get('status') in ('ok','healthy')
    except Exception:
        return False

r_ok = redis_up(); m_ok = memory_ok()
display(Markdown('Redis: ' + ('✅' if r_ok else '❌') + ' | Memory API: ' + ('✅' if m_ok else '❌')))
            """
        ),
        new_code_cell(
            """
# Latency sample using ClassAgent if OPENAI_API_KEY is set
try:
    if not os.getenv('OPENAI_API_KEY'):
        raise RuntimeError('OPENAI_API_KEY not set')
    # Locate reference-agent
    base = pathlib.Path.cwd()
    for _ in range(8):
        cand = base / 'python-recipes' / 'context-engineering' / 'reference-agent'
        if cand.exists():
            ref_agent = cand
            break
        base = base.parent
    import sys
    if str(ref_agent) not in sys.path: sys.path.insert(0, str(ref_agent))
    from redis_context_course.agent import ClassAgent
    agent = ClassAgent(student_id='ru_prod', session_id='latency')
    async def run_once(q):
        thread_id = 'trace_' + uuid.uuid4().hex[:8]
        t0=time.time(); _ = await agent.chat(q, thread_id=thread_id); dt=time.time()-t0
        return dt
    async def sample():
        qs = ['recommend 1 ml course']*3
        return await asyncio.gather(*[run_once(q) for q in qs])
    dts = asyncio.run(sample())
    display(Markdown('**Latencies (s):** ' + ', '.join(str(round(x,2)) for x in dts)))
except Exception as e:
    display(Markdown('Skipped latency sample: ' + str(e)))
            """
        ),
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

# 08_capstone
nb8c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Capstone

Define your agent for a domain of your choice. Plan:
- System context and role
- Tooling strategy and constraints
- Memory (working + long-term)
- Retrieval sources and grounding
- Optimizations and evaluation plan
"""
        )
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

nb8l = new_notebook(
    cells=[
        new_markdown_cell(
            """# Lab: Capstone

This is a guided scaffold that runs without external services. Replace stubs with your domain details.
"""
        ),
        new_code_cell(
            """
from IPython.display import Markdown, display

project = {
  'domain': 'Course advising',
  'goals': ['Personalized recommendations','Prerequisite checks','Profile-aware responses'],
  'tools': ['search_courses','get_course_details','check_prerequisites','memory_summary'],
  'optimizations': ['summarize context','keyword tool filter'],
}
display(Markdown('**Project plan:** ' + str(project)))
            """
        ),
        new_code_cell(
            """
# Mini-eval canaries (stub)
from statistics import mean
latencies = [0.12, 0.15, 0.11]
quality_scores = [4,4,5]
report = {
  'p50_latency_s': sorted(latencies)[len(latencies)//2],
  'avg_quality': mean(quality_scores)
}
from IPython.display import Markdown; display(Markdown('**Eval report:** ' + str(report)))
            """
        ),
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

# Write new/updated notebooks for 05-08
more = [
    (root/"05_orchestration"/"01_concepts.ipynb", nb5c),
    (root/"05_orchestration"/"02_lab.ipynb", nb5l),
    (root/"06_optimizations"/"01_concepts.ipynb", nb6c),
    (root/"06_optimizations"/"02_lab.ipynb", nb6l),
    (root/"07_production"/"01_concepts.ipynb", nb7c),
    (root/"07_production"/"02_lab.ipynb", nb7l),
    (root/"08_capstone"/"01_concepts.ipynb", nb8c),
    (root/"08_capstone"/"02_lab.ipynb", nb8l),
]
for p, nb in more:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print('Wrote', p)



# Enhanced concept notebooks for 00–08 (self-contained, runnable, graceful skips)
nb0c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Context Engineering

Core ideas:
- Layered context (system → few-shot → user)
- Make instructions explicit and testable
- Prefer small, composable prompts over one giant prompt
"""
        ),
        new_code_cell(
            """
# Demonstrate layered context ordering
from IPython.display import Markdown, display
system = "You are a helpful course advisor. Prefer concrete course titles."
few_shot = [
  ("user","I like databases"),
  ("assistant","Consider 'Intro to Databases' or 'NoSQL Systems'.")
]
user = "Recommend 1 ML course."
md = '**System:** ' + system + '\\n\\n' + '**Few-shot:** ' + str(few_shot) + '\\n\\n' + '**User:** ' + user
display(Markdown(md))
            """
        ),

        new_code_cell(
            """
# Optional: run layered context with a small LLM (skips if no API)
try:
    import os, time
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
    if not os.getenv('OPENAI_API_KEY'):
        raise RuntimeError('OPENAI_API_KEY not set')
    model = ChatOpenAI(model=os.getenv('OPENAI_MODEL','gpt-4o-mini'), temperature=0)
    msgs = [SystemMessage(content=system), HumanMessage(content=user)]
    t0=time.time(); resp = model.invoke(msgs); dt=time.time()-t0
    print('Latency(s):', round(dt,2))
    print('Output:', resp.content[:200])
except Exception as e:
    print('Skipped LLM demo:', e)
            """
        )

    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

nb1c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Fundamentals

- Messages (system, user, assistant)
- Token budgets and why they matter
- Determinism vs. creativity (temperature)
"""
        ),
        new_code_cell(
            """
# Token counting (try tiktoken; fallback to words)
text = "This is a small example to estimate tokens."
try:
    import tiktoken
    enc = tiktoken.get_encoding('cl100k_base')
    toks = len(enc.encode(text))
    print('tiktoken tokens:', toks)
except Exception:
    print('tiktoken not available; word count:', len(text.split()))
            """
        ),

        new_code_cell(
            """
# Temperature contrast (skips if no API)
try:
    import os
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    if not os.getenv('OPENAI_API_KEY'):
        raise RuntimeError('OPENAI_API_KEY not set')
    prompt = 'List two course ideas about optimization.'
    cold = ChatOpenAI(model=os.getenv('OPENAI_MODEL','gpt-4o-mini'), temperature=0)
    hot = ChatOpenAI(model=os.getenv('OPENAI_MODEL','gpt-4o-mini'), temperature=0.8)
    a = cold.invoke([HumanMessage(content=prompt)]).content
    b = hot.invoke([HumanMessage(content=prompt)]).content
    print('Temperature 0:', a[:160])
    print('Temperature 0.8:', b[:160])
except Exception as e:
    print('Skipped temp demo:', e)
            """
        )
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

nb2c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: System and Tools

- System instructions constrain behavior
- Tools extend the model (retrieval, calculators, domain APIs)
- Keep tool IO small and validated
"""
        ),
        new_code_cell(
            """
# Tiny tool example (no external deps)
from typing import List

def search_courses_stub(query: str, corpus: List[str]):
    q = query.lower()
    return [c for c in corpus if any(w in c.lower() for w in q.split())]

corpus = ['Intro to Databases','NoSQL Systems','Machine Learning 101','Deep Learning']
print(search_courses_stub('learning', corpus))
            """
        ),

        new_code_cell(
            """
# Pydantic-validated tool contract
from pydantic import BaseModel, Field, ValidationError
from typing import List

class CourseQuery(BaseModel):
    query: str = Field(..., min_length=3)
    limit: int = 3

def course_tool(input: CourseQuery, corpus: List[str]):
    results = [c for c in corpus if input.query.lower() in c.lower()]
    return results[: input.limit]

try:
    print(course_tool(CourseQuery(query='ML', limit=2), corpus))
    course_tool(CourseQuery(query='x', limit=1), corpus)
except ValidationError as ve:
    print('Validation error:', ve.errors()[0]['msg'])
            """
        )
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

nb3c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Memory

- Working memory (per session) vs. long-term memory
- Extract facts; avoid storing full transcripts
- Summarize to control growth
"""
        ),
        new_code_cell(
            """
# Local memory stub (no server)
working = []
long_term = {}

working.append({'speaker':'user','text':'My name is Alex and I like ML.'})
# Extract a 'fact' with a simple heuristic
if 'name is' in working[-1]['text']:
    name = working[-1]['text'].split('name is',1)[1].split()[0]
    long_term['name'] = name
print('working:', working[-1]['text'])
print('long_term:', long_term)
            """
        ),

        new_code_cell(
            """
# Summarize working memory to long-term (very naive)
summary = working[-1]['text'][:40] + '...'
long_term['summary'] = summary
print('summary:', summary)

# Recall + respond (grounding to long-term facts)
name = long_term.get('name','student')
print(f"Hello {name}, I'll remember you like ML.")
            """
        )
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

nb4c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Retrieval (RAG)

- Separate knowledge from prompts
- Index documents; fetch relevant chunks; ground responses
- Start simple: lexical similarity is fine for demos
"""
        ),
        new_code_cell(
            """
# Simple lexical similarity (Jaccard)
def jaccard(a, b):
    A, B = set(a.lower().split()), set(b.lower().split())
    return len(A & B) / (len(A | B) or 1)

docs = [
  ('DB101','Relational databases and SQL basics.'),
  ('ML101','Intro to machine learning: supervised, unsupervised.'),
  ('DS201','Data science pipelines and feature engineering.')
]
query = 'machine learning basics'
top = sorted(docs, key=lambda d: jaccard(query, d[1]), reverse=True)[:2]
print(top)
            """
        ),

        new_code_cell(
            """
# Compose a grounded answer from top result
best = top[0]
print('Answer:', f"Based on {best[0]}: {best[1]}")
            """
        )
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

# Enrich 05–08 concepts with small runnable examples
nb5c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Orchestration

- Router → worker topology
- Timeouts and fallbacks
- Per-node tool exposure (loadouts)
"""
        ),
        new_code_cell(
            """
# Pure-Python router demo
from IPython.display import Markdown, display

def route(q: str) -> str:
    ql = q.lower()
    if 'eligible' in ql or 'prereq' in ql: return 'prereq'
    if 'about me' in ql or 'know me' in ql: return 'profile'
    return 'search'

for q in ['find ML courses','am I eligible for CS301?']:
    r = route(q)
    display(Markdown('**Query:** ' + q + '\\n\\n**Route:** ' + r))
            """
        ),
        new_code_cell(
            """
# Timeout + fallback demo (Jupyter-safe using threading)
import threading, time

result = {'value': None}

def slow_task():
    time.sleep(1.5)
    result['value'] = 'slow-path result'

thr = threading.Thread(target=slow_task)
thr.start()
thr.join(timeout=0.5)
print(result['value'] if result['value'] is not None else 'fallback result (timeout)')
            """
        ),
        new_code_cell(
            """
# Loadouts: per-route tool exposure
loadouts = {
  'search': ['search_courses','get_course_details'],
  'prereq': ['check_prerequisites'],
  'profile': ['read_memory_summary']
}
for q in ['find ML courses','am I eligible for CS301?','what do you know about me?']:
    r = route(q)
    print(r, '→', loadouts.get(r, []))
            """
        ),
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

nb6c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Optimizations

- Summarize to reduce tokens
- Cache repeated calls
- Filter tools by intent
"""
        ),
        new_code_cell(
            """
# LRU cache demo
from functools import lru_cache

@lru_cache(maxsize=4)
def slow_fn(x):
    s = 0
    for i in range(10000): s += (i % (x+1))
    return s
print(slow_fn(5)); print(slow_fn(5))  # second call cached
            """
        ),

        new_code_cell(
            """
# Prompt distillation (naive summarization)
text = ' '.join(['This is a background paragraph about the university.']*10)
summary = ' '.join(text.split()[:30])
print('orig_len:', len(text.split()), 'summary_len:', len(summary.split()))
            """
        ),
        new_code_cell(
            """
# Intent-based tool filter
def select_tools(query, all_tools):
    q=query.lower()
    if any(w in q for w in ['search','find','show','what','which']): return all_tools['search']
    if any(w in q for w in ['remember','recall','about me']): return all_tools['memory']
    return all_tools['search']
print(select_tools('what courses are available?', {'search':['search','details'],'memory':['read_mem']}))
            """
        )
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

nb7c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Production

- Correlation IDs for tracing
- Structured logs
- Latency and error metrics
"""
        ),
        new_code_cell(
            """
# Correlation ID + structured log demo
import time, uuid, json
cid = 'trace_' + uuid.uuid4().hex[:8]
start = time.time()
# ... do work ...
log = {'cid': cid, 'event': 'work_done', 'latency_s': round(time.time()-start,4)}
print(json.dumps(log))
            """
        ),

        new_code_cell(
            """
# Retry with exponential backoff (demo)
import random, time

def flaky():
    if random.random() < 0.7: raise RuntimeError('flaky error')
    return 'ok'

attempts=0; delay=0.1
while True:
    try:
        print('result:', flaky()); break
    except Exception as e:
        attempts+=1
        if attempts>3: print('failed after retries'); break
        time.sleep(delay); delay*=2
            """
        )
    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)

nb8c = new_notebook(
    cells=[
        new_markdown_cell(
            """# Concepts: Capstone

Design blueprint:
- Domain and user journeys
- Context, tools, memory, retrieval
- Optimization and evaluation plan
"""
        ),
        new_code_cell(
            """
# Minimal blueprint object
blueprint = {
  'domain':'Course advising',
  'tools':['search','details','prereq','memory'],
  'eval':['accuracy','latency','coverage']
}
print(blueprint)
            """
        ),

        new_code_cell(
            """
# Rubric + checklist
rubric = {'context':3,'tools':3,'memory':3,'retrieval':3,'production':3}
submission = {'context':2,'tools':3,'memory':2,'retrieval':3,'production':2}
score = sum(min(submission[k], rubric[k]) for k in rubric)
print('score/possible:', score, '/', sum(rubric.values()))
            """
        )

    ],
    metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
)



# Final write (canonical): consolidate and write all notebooks
_out_files = [
    # Concepts (0004)
    (root/"00_onboarding"/"01_concepts.ipynb", nb0c),
    (root/"01_fundamentals"/"01_concepts.ipynb", nb1c),
    (root/"02_system_and_tools"/"01_concepts.ipynb", nb2c),
    (root/"03_memory"/"01_concepts.ipynb", nb3c),
    (root/"04_retrieval"/"01_concepts.ipynb", nb4c),
    # Labs (0004)
    (root/"00_onboarding"/"02_lab.ipynb", nb0),
    (root/"01_fundamentals"/"02_lab.ipynb", nb1),
    (root/"02_system_and_tools"/"02_lab.ipynb", nb2),
    (root/"03_memory"/"02_lab.ipynb", nb3),
    (root/"04_retrieval"/"02_lab.ipynb", nb4),
    # Concepts + Labs (0508)
    (root/"05_orchestration"/"01_concepts.ipynb", nb5c),
    (root/"05_orchestration"/"02_lab.ipynb", nb5l),
    (root/"06_optimizations"/"01_concepts.ipynb", nb6c),
    (root/"06_optimizations"/"02_lab.ipynb", nb6l),
    (root/"07_production"/"01_concepts.ipynb", nb7c),
    (root/"07_production"/"02_lab.ipynb", nb7l),
    (root/"08_capstone"/"01_concepts.ipynb", nb8c),
    (root/"08_capstone"/"02_lab.ipynb", nb8l),
]
for p, nb in _out_files:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print('Wrote', p)
