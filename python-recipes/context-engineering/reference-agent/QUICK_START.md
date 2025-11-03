# Quick Start - Redis Context Course Agent

Get the Redis Context Course agent running in under 10 minutes.

## 🚀 One-Command Setup

```bash
# 1. Install package
pip install -e .

# 2. Set your OpenAI API key
export OPENAI_API_KEY="sk-your-actual-key-here"

# 3. Start Redis
docker run -d --name redis -p 6379:6379 redis:8-alpine

# 4. Start Agent Memory Server
uv run agent-memory api --no-worker &

# 5. Generate and ingest data
generate-courses --courses-per-major 15 --output course_catalog.json
ingest-courses --catalog course_catalog.json --clear

# 6. Verify everything works
python simple_health_check.py

# 7. Start the agent
redis-class-agent --student-id your_name
```

## ✅ Health Check First

**Always start here** if you have any issues:

```bash
python simple_health_check.py
```

This tells you exactly what's working and what needs to be fixed.

## 🎯 Expected Output

When everything is working:

```
Redis Context Course - Health Check
=====================================
✅ Environment: All variables set
✅ Redis: Connected
✅ Courses: 75 found
✅ Majors: 5 found
✅ Course Search: Working
✅ Agent: Working

🎯 Status: READY
📊 All checks passed!

🚀 Try: redis-class-agent --student-id your_name
```

## 💬 Try These Queries

Once the agent is running, try:

```
You: How many courses are available?
Agent: I found 75 courses across 5 different majors...

You: Show me programming courses
Agent: Here are some programming courses I found...

You: I'm interested in machine learning
Agent: Great! I'll remember your interest in machine learning...

You: What should I take for computer science?
Agent: Based on your interest in machine learning and computer science...
```

## 🔧 Quick Fixes

### "Environment: Missing OPENAI_API_KEY"
```bash
# Set your API key
export OPENAI_API_KEY="sk-your-actual-key-here"

# Or edit .env file
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env
```

### "Redis: Connection failed"
```bash
# Start Redis
docker run -d --name redis -p 6379:6379 redis:8-alpine
```

### "Courses: None found"
```bash
# Generate and ingest data
generate-courses --courses-per-major 15 --output course_catalog.json
ingest-courses --catalog course_catalog.json --clear
```

### "Agent: Failed"
```bash
# Start Agent Memory Server
uv run agent-memory api --no-worker
```

## 📚 What You Get

- **75 sample courses** across 5 majors
- **Semantic search** - find courses by description
- **Memory system** - remembers your preferences
- **Personalized recommendations** - suggests relevant courses
- **Interactive chat** - natural language interface

## 🎓 Example Interaction

```
╭──────── 🎓 Class Agent ────────╮
│ Welcome to Redis University    │
│ Class Agent!                   │
╰────────────────────────────────╯

You: I want to learn data science
Agent: I'll help you find data science courses! Let me search for relevant options...

Found 8 data science related courses:

**DS201: Introduction to Data Science**
Department: Data Science | Credits: 3 | Difficulty: Beginner
Description: Foundational course covering data collection, cleaning, analysis...

**DS301: Machine Learning Fundamentals**  
Department: Data Science | Credits: 4 | Difficulty: Intermediate
Description: Core machine learning algorithms and their applications...

You: I prefer online courses
Agent: I'll remember that you prefer online courses. Let me filter for online data science options...

You: What should I take first?
Agent: Based on your interest in data science and preference for online courses, I recommend starting with DS201: Introduction to Data Science. It's beginner-friendly and available online...
```

## 🛠️ Development Mode

For development and customization:

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Check code quality
python system_health_check.py --verbose

# Explore examples
python examples/basic_usage.py
```

## 📖 Next Steps

1. **Read the full README**: `README.md`
2. **Check examples**: `examples/` directory  
3. **Follow setup plan**: `SETUP_PLAN.md`
4. **Troubleshoot issues**: `INVESTIGATION_GUIDE.md`
5. **Customize the agent**: Modify `redis_context_course/agent.py`

## 🆘 Need Help?

1. **Run health check**: `python simple_health_check.py`
2. **Check investigation guide**: `INVESTIGATION_GUIDE.md`
3. **Review logs**: Look for error messages in terminal
4. **Reset everything**: Follow rollback plan in `SETUP_PLAN.md`

## 🎉 Success!

When you see this, you're ready to go:

```
🎯 Status: READY
📊 All checks passed!
```

Start exploring with:
```bash
redis-class-agent --student-id your_name
```

Happy learning! 🚀
