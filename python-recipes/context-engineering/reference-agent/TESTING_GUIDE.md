# Testing Guide - Redis Context Course Agent

Comprehensive guide to test and explore all capabilities of the Redis Context Course agent.

## 🎯 **Testing Overview**

This guide helps you systematically test:
- ✅ Core functionality (search, recommendations)
- ✅ Memory system (working + long-term)
- ✅ Context awareness and personalization
- ✅ Tool integration and performance
- ✅ Edge cases and error handling

## 📋 **Pre-Testing Checklist**

```bash
# 1. Verify system health
python simple_health_check.py

# Expected output:
# ✅ Environment: All variables set
# ✅ Redis: Connected  
# ✅ Courses: 75 found
# ✅ Majors: 5 found
# ✅ Course Search: Working
# ✅ Agent: Working

# 2. Check data is properly loaded
redis-cli DBSIZE  # Should show ~88 keys
```

## 🧪 **Phase 1: Basic Functionality (5-10 minutes)**

### **Test Course Discovery**
```bash
redis-class-agent --student-id test_basic

# Test queries:
"How many courses are available?"
"What majors are offered?"
"Show me all programming courses"
"Find data science classes"
"List beginner-level courses"
```

**Expected Results:**
- Should find ~75 courses total
- Should identify 5 majors (Computer Science, Data Science, Business, Psychology, Engineering)
- Programming courses: CS101, CS201, CS301, etc.
- Responses should be specific with course codes and titles

### **Test Search Quality**
```bash
# Semantic search tests:
"I want to learn coding"  # Should find programming courses
"Show me math classes"    # Should find mathematics courses
"Find AI courses"         # Should find machine learning/AI courses
"What about databases?"   # Should find database courses
```

**Success Criteria:**
- ✅ Finds relevant courses (>80% accuracy)
- ✅ Understands synonyms (coding = programming)
- ✅ Returns course details (code, title, description)
- ✅ Responds in <3 seconds

## 🧠 **Phase 2: Memory System Testing (10-15 minutes)**

### **Test Working Memory (Same Session)**
```bash
redis-class-agent --student-id test_memory

# Conversation flow:
"I'm interested in computer science"
"I prefer online courses"
"What do you recommend?"  # Should consider both preferences
"I also like challenging courses"
"Update my recommendations"  # Should include difficulty preference
```

**Expected Behavior:**
- Agent remembers preferences within the conversation
- Recommendations get more personalized as conversation progresses
- Context builds naturally

### **Test Long-Term Memory (Cross-Session)**
```bash
# Session 1:
redis-class-agent --student-id test_persistence

"My name is Alex"
"I'm majoring in computer science"
"I prefer online courses"
"I want to focus on machine learning"
"I've completed CS101 and MATH201"
# Type 'quit'

# Session 2 (restart with same ID):
redis-class-agent --student-id test_persistence

"Hi, do you remember me?"  # Should remember Alex
"What courses should I take next?"  # Should consider completed courses
"Recommend something for my major"  # Should remember CS major + ML interest
```

**Success Criteria:**
- ✅ Remembers student name across sessions
- ✅ Recalls major and preferences
- ✅ Considers completed courses in recommendations
- ✅ Maintains conversation context

## 🎓 **Phase 3: Advanced Features (15-20 minutes)**

### **Test Personalized Recommendations**
```bash
redis-class-agent --student-id test_advanced

# Build a detailed profile:
"I'm a sophomore computer science major"
"I've completed CS101, CS102, and MATH101"
"I'm interested in artificial intelligence and machine learning"
"I prefer hands-on, project-based courses"
"I want to avoid courses with heavy theory"
"My goal is to work in tech after graduation"

# Test recommendations:
"What should I take next semester?"
"Plan my junior year courses"
"What electives would help my career goals?"
```

**Expected Behavior:**
- Recommendations consider academic level (sophomore)
- Suggests appropriate prerequisites
- Aligns with stated interests (AI/ML)
- Considers learning style preferences
- Connects to career goals

### **Test Course Planning**
```bash
# Test academic planning:
"I want to graduate in 2 years, help me plan"
"What prerequisites do I need for advanced AI courses?"
"Show me a typical computer science course sequence"
"I'm behind in math, what should I prioritize?"
```

**Success Criteria:**
- ✅ Understands prerequisite relationships
- ✅ Suggests logical course sequences
- ✅ Adapts to student's current progress
- ✅ Provides strategic academic advice

## 🔧 **Phase 4: Tool Integration Testing (10 minutes)**

### **Test Individual Tools**
```bash
# Test search tool variations:
"Find courses with 'machine learning' in the title"
"Show me 4-credit courses only"
"List all intermediate difficulty courses"
"Find courses in the Computer Science department"

# Test recommendation engine:
"I like CS101, recommend similar courses"
"What's popular among computer science students?"
"Suggest courses that complement data science"
```

### **Test Memory Tools**
```bash
# Test preference storage:
"Remember that I prefer morning classes"
"I don't like courses with group projects"
"Save my goal: become a data scientist"

# Test context retrieval:
"What do you know about my preferences?"
"Remind me of my academic goals"
"What have we discussed before?"
```

**Success Criteria:**
- ✅ All tools respond correctly
- ✅ Filters work as expected
- ✅ Memory storage/retrieval functions
- ✅ Tools integrate seamlessly in conversation

## ⚡ **Phase 5: Performance Testing (5 minutes)**

### **Test Response Times**
```bash
# Time these queries:
"Show me all courses"  # Should be <2 seconds
"Find programming courses"  # Should be <1 second
"What do you recommend for me?"  # Should be <3 seconds
"Plan my entire degree"  # Should be <5 seconds
```

### **Test Load Handling**
```bash
# Test with complex queries:
"Show me all intermediate computer science courses that are available online, have 3-4 credits, and relate to either programming, databases, or machine learning, but exclude any that require advanced mathematics as a prerequisite"

# Test rapid queries:
# Send 5-10 quick questions in succession
```

**Performance Benchmarks:**
- Simple queries: <1 second
- Complex searches: <2 seconds  
- Recommendations: <3 seconds
- Planning queries: <5 seconds

## 🚨 **Phase 6: Edge Cases & Error Handling (10 minutes)**

### **Test Invalid Queries**
```bash
# Test nonsensical requests:
"Show me courses about unicorns"
"I want to major in time travel"
"Find courses taught by aliens"
"What's the weather like?"

# Test boundary conditions:
"Show me 1000 courses"
"Find courses with negative credits"
"I've completed every course, what's next?"
```

### **Test System Limits**
```bash
# Test very long conversations:
# Have a 50+ message conversation, check if context is maintained

# Test memory limits:
# Store many preferences, see if older ones are retained

# Test concurrent sessions:
# Run multiple agent instances with different student IDs
```

**Expected Behavior:**
- ✅ Graceful handling of invalid requests
- ✅ Stays focused on course-related topics
- ✅ Reasonable responses to edge cases
- ✅ No crashes or errors

## 📊 **Success Metrics Summary**

### **Functional Requirements**
- [ ] Course search accuracy >80%
- [ ] Memory persistence across sessions
- [ ] Personalized recommendations
- [ ] Context awareness in conversations
- [ ] All tools working correctly

### **Performance Requirements**
- [ ] Average response time <3 seconds
- [ ] Complex queries <5 seconds
- [ ] No timeouts or failures
- [ ] Handles concurrent users

### **Quality Requirements**
- [ ] Natural conversation flow
- [ ] Relevant and helpful responses
- [ ] Consistent behavior
- [ ] Proper error handling

## 🐛 **Common Issues & Solutions**

### **Agent Doesn't Remember**
```bash
# Check Agent Memory Server
curl http://localhost:8088/health

# Restart if needed
pkill -f "agent-memory"
uv run agent-memory api --no-worker
```

### **Search Returns No Results**
```bash
# Verify course data
python simple_health_check.py

# Re-ingest if needed
ingest-courses --catalog course_catalog.json --clear
```

### **Slow Responses**
```bash
# Check system performance
python system_health_check.py --verbose

# Monitor Redis
redis-cli INFO stats
```

## 📝 **Testing Checklist**

Copy this checklist and check off as you test:

**Basic Functionality:**
- [ ] Course count query works
- [ ] Major listing works  
- [ ] Course search finds relevant results
- [ ] Semantic search understands synonyms

**Memory System:**
- [ ] Working memory maintains context in session
- [ ] Long-term memory persists across sessions
- [ ] Preferences are remembered
- [ ] Completed courses are tracked

**Advanced Features:**
- [ ] Personalized recommendations work
- [ ] Academic planning assistance
- [ ] Prerequisite understanding
- [ ] Career goal alignment

**Performance:**
- [ ] Response times meet benchmarks
- [ ] Complex queries handled efficiently
- [ ] No timeouts or errors
- [ ] Concurrent usage works

**Edge Cases:**
- [ ] Invalid queries handled gracefully
- [ ] System limits respected
- [ ] Error recovery works
- [ ] Maintains focus on courses

## 🎯 **Next Steps After Testing**

1. **Document findings** - Note any issues or unexpected behaviors
2. **Performance optimization** - If responses are slow
3. **Customization** - Modify agent behavior based on testing
4. **Integration** - Connect to your applications
5. **Scaling** - Consider production deployment

## 📚 **Additional Resources**

- **Health Check**: `python simple_health_check.py`
- **Troubleshooting**: `INVESTIGATION_GUIDE.md`
- **Setup Issues**: `SETUP_PLAN.md`
- **Quick Start**: `QUICK_START.md`
- **Examples**: `examples/basic_usage.py`
