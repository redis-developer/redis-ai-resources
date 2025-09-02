# Redis Agent Memory

Modern AI agents rely on memory to go beyond single-turn responses and behave more like intelligent, adaptive assistants. Memory enables agents to understand user context, retain important facts, recall past interactions, and personalize conversations over time. Without memory, an agent starts each interaction from scratch — forgetting preferences, goals, and history — which limits its usefulness and realism.

In AI systems, memory is typically divided into two types:
- Short-term memory maintains context within a single session or conversation thread. This allows the agent to track recent messages, follow up on prior turns, and provide coherent responses.
- Long-term memory stores information across sessions, including facts (semantic memory) and personal experiences or preferences (episodic memory). This allows the agent to “remember” what it has learned about a user or domain, making interactions feel more consistent and personalized.

This demo implements both memory types using Redis and Spring AI, combining the speed and flexibility of Redis with the semantic capabilities of vector embeddings. With vector similarity search, agents can retrieve relevant memories even if a user’s phrasing is different from how the information was originally stored. You’ll also see features like memory deduplication, summarization, and filtering — all designed to give AI agents a robust and scalable memory system.

## Learning resources:

- Video: [What is an embedding model?](https://youtu.be/0U1S0WSsPuE)
- Video: [Exact vs Approximate Nearest Neighbors - What's the difference?](https://youtu.be/9NvO-VdjY80)
- Video: [What is semantic search?](https://youtu.be/o3XN4dImESE)
- Video: [What is a vector database?](https://youtu.be/Yhv19le0sBw)

## Repository

The repository for this demo can be found [here](https://github.com/redis-developer/redis-springboot-resources/tree/main/artificial-intelligence/agent-memory-with-spring-ai)

## Requirements

To run this demo, you’ll need the following installed on your system:
- Docker – [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose – Included with Docker Desktop or available via CLI installation guide
- An OpenAI API Key – You can get one from [platform.openai.com](https://platform.openai.com)

## Running the demo

The easiest way to run the demo is with Docker Compose, which sets up all required services in one command.

### Step 1: Clone the repository

If you haven’t already:

```bash
git clone https://github.com/redis-developer/redis-springboot-recipes.git
cd redis-springboot-recipes/artificial-intelligence/agent-memory-with-spring-ai
```

### Step 2: Configure your environment

You can pass your OpenAI API key in two ways:

#### Option 1: Export the key via terminal

```bash
export OPENAI_API_KEY=sk-your-api-key
```

#### Option 2: Use a .env file

Create a `.env` file in the same directory as the `docker-compose.yml` file:

```env
OPENAI_API_KEY=sk-your-api-key
```

### Step 3: Start the services

```bash
docker compose up --build
```

This will start:

- redis: for storing both vector embeddings and chat history
- redis-insight: a UI to explore the Redis data
- agent-memory-app: the Spring Boot app that implements the memory-aware AI agent

## Using the demo

When all of your services are up and running. Go to `localhost:8080` to access the demo:

![Screenshot of the Redis Agent Memory demo web interface. The interface is titled “Travel Agent with Redis Memory” and features two main panels: a “Memory Management” section on the left with tabs for Episodic and Semantic memories (currently showing “No episodic memories yet”), and a “Travel Assistant” chat on the right displaying a welcome message. At the top right, there’s a field to enter a user ID and buttons to start or clear the chat. The interface is clean and styled with Redis branding.](readme-assets/1_demo_home.png)

Type a user ID in the user ID box and then click on `start chat` to start a new chat:

![Close-up screenshot of the user ID input and chat controls. The label “User ID:” appears on the left with a text input field containing the value “raphael”. To the right are two red buttons labeled “Start Chat” and “Clear Chat”.](readme-assets/2_userid_box.png)

Type a message and hit send:

![Animated screen recording of a user sending a message in the Redis Agent Memory demo. The user, identified as “raphael”, types a detailed message into the chat input box: “Hi, my name’s Raphael. I went to Paris back in 2009 with my wife for our honeymoon and we had a lovely time. For our 10-year anniversary we’re planning to go back. Help us plan the trip!” The cursor then clicks the red “Send” button, initiating the interaction with the AI travel assistant.](readme-assets/3_sending_a_msg.gif)

The system will reply with the response to your message and, in case it identifies potential memories to be stored, they will be stored either as semantic or episodic memories. You can see the stored memories on the "Memory Management" sidebar.

On top of that, with each message, the system will also return performance metrics.

If you refresh the page, you will see that all memories and the chat history are gone.

If you reenter the same user ID, the long-term memories will be reloaded on the sidebar and the short-term memory (the chat history) will be reloaded as well:

![Animated screen recording of the Redis Agent Memory demo after sending a message. The sidebar under “Episodic Memories” now shows two stored entries: one noting that the user went to Paris in 2009 for their honeymoon, and another about planning a return for their 10-year anniversary. The chat assistant responds with a personalized message suggesting activities and asking follow-up questions. The browser page is then refreshed, clearing both the chat history and memory display. After re-entering the same user ID, the agent reloads the long-term memories in the sidebar and restores the conversation history, demonstrating persistent memory retrieval.](readme-assets/4_refreshing_page.gif)

Finally, if we clear the chat, the chatbot won't have access to the short-term memory anymore. But it will still have access to the long-term memory. If we ask something related to one of the long-term memories, we will see that the chatbot retained this information:

![Animated screen recording of a cleared chat session in the Redis Agent Memory demo. The “Episodic Memories” panel still shows two past memories about a trip to Paris. In the chat panel, the message “Conversation cleared. How can I assist you today?” appears, indicating that the short-term memory has been reset. The user is about to start a new conversation. This demonstrates that although the short-term context is gone, the agent retains access to long-term memories, allowing it to respond with relevant information from past interactions.](readme-assets/5_starting_new_chat.gif)

### Redis Insight

RedisInsight is a graphical tool developed by Redis to help developers and administrators interact with and manage Redis databases more efficiently. It provides a visual interface for exploring keys, running commands, analyzing memory usage, and monitoring performance metrics in real-time. RedisInsight supports features like full-text search, time series, streams, and vector data structures, making it especially useful for working with more advanced Redis use cases. With its intuitive UI, it simplifies debugging, optimizing queries, and understanding data patterns without requiring deep familiarity with the Redis CLI.

The Docker Compose file will also spin up an instance of Redis Insight. We can access it by going to `localhost:5540`:

![Screenshot of RedisInsight showing stored keys from the Redis Agent Memory demo. The interface displays two key groups: a conversation key under a list named “raphael”, and four memory keys stored as JSON objects with unique UUID-like names. Each memory key is around 10 KB in size, and the interface indicates that 5 keys have been scanned. The right panel is empty, waiting for a key selection to show detailed contents. This view illustrates how short- and long-term memory data is structured and persisted in Redis.](readme-assets/6_redis_insight.png)

If we go to Redis Insight, we will be able to see the data stored in Redis.

The short-term memory (chat history) is stored in a List data structure:

![Screenshot of RedisInsight displaying the contents of the conversation:raphael key. The selected key is a Redis list representing a conversation history. On the right panel, the list shows four indexed elements: system prompts defining the assistant’s role and memory access, a user message asking “Where did I go back in 2009?”, and the assistant’s reply recalling a previous trip to Paris. Below this, several memory entries stored as JSON keys are also visible. This illustrates how short-term chat history is preserved in Redis and replayed per user session.](readme-assets/7_redis_insight_short_term_memory.png)

And the long-term memory is stored as JSON documents:

![Screenshot of RedisInsight showing a semantic memory stored in Redis. The selected key is a JSON object with the name memory:04d04.... The right panel displays the memory’s fields: createdAt timestamp, empty metadata, memoryType set to “SEMANTIC”, an embedding vector (collapsed), userId set to “system”, and the memory content: “Paris is a beautiful city known for celebrating love”. This illustrates how general knowledge is stored as semantic memory in the AI agent.](readme-assets/8_redis_insight_long_term_memory.png)

If we go to the workbench on the sidebar, and then run the `FT.INDEX 'memoryIdx'` command. We will be able to see the details of the schema that was created to efficiently search through the persisted memories:

![Screenshot of RedisInsight Workbench showing the schema details of the memoryIdx vector index. The result of the FT.INFO memoryIdx command displays an index on JSON documents prefixed with memory:. The schema includes: •	$.content as a TEXT field named content  •	$.embedding as a VECTOR field using HNSW with 384-dimension FLOAT32 vectors and COSINE distance  •	$.memoryType and $.userId as TAG fields  •	$.metadata and $.createdAt as TEXT fields  This shows how memory data is structured and searchable in Redis using RediSearch vector similarity.](readme-assets/redis_insight_index_details.png)

## How It Is Implemented

The application uses Spring AI's `RedisVectorStore` to store and search vector embeddings of memories.

### Configuring the Vector Store

```kotlin
@Bean
fun memoryVectorStore(
    embeddingModel: EmbeddingModel,
    jedisPooled: JedisPooled
): RedisVectorStore {
    return RedisVectorStore.builder(jedisPooled, embeddingModel)
        .indexName("memoryIdx")
        .contentFieldName("content")
        .embeddingFieldName("embedding")
        .metadataFields(
            RedisVectorStore.MetadataField("memoryType", Schema.FieldType.TAG),
            RedisVectorStore.MetadataField("metadata", Schema.FieldType.TEXT),
            RedisVectorStore.MetadataField("userId", Schema.FieldType.TAG),
            RedisVectorStore.MetadataField("createdAt", Schema.FieldType.TEXT)
        )
        .prefix("memory:")
        .initializeSchema(true)
        .vectorAlgorithm(RedisVectorStore.Algorithm.HSNW)
        .build()
}
```

Let's break this down:

- **Index Name**: `memoryIdx` - Redis will create an index with this name for searching memories
- **Content Field**: `content` - The raw memory content that will be embedded
- **Embedding Field**: `embedding` - The field that will store the resulting vector embedding
- **Metadata Fields**:
    - `memoryType`: TAG field for filtering by memory type (EPISODIC or SEMANTIC)
    - `metadata`: TEXT field for storing additional context about the memory
    - `userId`: TAG field for filtering by user ID
    - `createdAt`: TEXT field for storing the creation timestamp

### Storing Memories

Memories are stored as Spring AI `Document` objects with metadata:

```kotlin
val memory = Memory(
    content = content,
    memoryType = memoryType,
    userId = userId ?: systemUserId,
    metadata = validatedMetadata,
    createdAt = LocalDateTime.now()
)

val document = Document(
    content,
    mapOf(
        "memoryType" to memoryType.name,
        "metadata" to validatedMetadata,
        "userId" to (userId ?: systemUserId),
        "createdAt" to memory.createdAt.toString()
    )
)

memoryVectorStore.add(listOf(document))
```

### Retrieving Memories

The memory service uses Spring AI's `SearchRequest` and `FilterExpressionBuilder` to perform vector similarity search with filters:

```kotlin
val b = FilterExpressionBuilder()
val filterList = mutableListOf<FilterExpressionBuilder.Op>()

// Add user filter
val effectiveUserId = userId ?: systemUserId
filterList.add(b.eq("userId", effectiveUserId))

// Add memory type filter if specified
if (memoryType != null) {
    filterList.add(b.eq("memoryType", memoryType.name))
}

// Combine filters
val filterExpression = when (filterList.size) {
    0 -> null
    1 -> filterList[0]
    else -> filterList.reduce { acc, expr -> b.and(acc, expr) }
}?.build()

// Execute search
val searchResults = memoryVectorStore.similaritySearch(
    SearchRequest.builder()
        .query(query)
        .topK(limit)
        .filterExpression(filterExpression)
        .build()
)
```

This performs a vector similarity search using:
- A semantic query that is embedded into a vector
- A topK setting to limit how many nearest matches to return
- A Redis filter expression to narrow down by memory type, user ID, and thread ID

### Agent System Prompt

The agent is configured with a system prompt that explains its capabilities and access two different types of memory:

```kotlin
@Bean
fun travelAgentSystemPrompt(): Message {
    val promptText = """
        You are a travel assistant helping users plan their trips. You remember user preferences
        and provide personalized recommendations based on past interactions.

        You have access to the following types of memory:
        1. Short-term memory: The current conversation thread
        2. Long-term memory:
           - Episodic: User preferences and past trip experiences (e.g., "User prefers window seats")
           - Semantic: General knowledge about travel destinations and requirements

        Always be helpful, personal, and context-aware in your responses.

        Always answer in text format. No markdown or special formatting.
    """.trimIndent()

    return SystemMessage(promptText)
}
```

### Agent Memory Orchestration

The agent orchestrates memory through the `ChatService`, which handles the flow of retrieving, using, and storing memories during conversations. Here's how it works:

#### 1. Processing User Messages

When a user sends a message, the agent processes it through the `sendMessage` method:

```kotlin
fun sendMessage(
    message: String,
    userId: String,
): ChatResult {
    // Get or create conversation history (try to load from Redis first)
    val history = conversationHistory.computeIfAbsent(userId) {
        // Try to load from Redis first
        val redisHistory = loadConversationHistoryFromRedis(userId)
        if (redisHistory.isNotEmpty()) {
            redisHistory.toMutableList()
        } else {
            mutableListOf(travelAgentSystemPrompt)
        }
    }

    // Retrieve relevant memories with timing
    val (memories, embTime) = retrieveRelevantMemoriesWithTiming(message, userId)

    // Add memory context if available
    if (memories.isNotEmpty()) {
        val memoryContext = formatMemoriesAsContext(memories)
        // Add memory context as a system message
        history.add(SystemMessage(memoryContext))
    }

    // Add user's message to history
    val userMessage = UserMessage(message)
    history.add(userMessage)

    // Create prompt with conversation history
    val prompt = Prompt(history)

    // Generate response
    val response = chatModel.call(prompt)

    // Add assistant response to history
    history.add(AssistantMessage(response.result.output.text ?: ""))

    // Save conversation history to Redis
    saveConversationHistoryToRedis(userId, history)

    // Extract and store memories from the conversation
    extractAndStoreMemoriesWithTiming(message, response.result.output.text ?: "", userId)

    // Summarize conversation if it's getting too long
    if (history.size > 10) {
        summarizeConversation(history, userId)
        // Save the summarized history to Redis
        saveConversationHistoryToRedis(userId, history)
    }

    // Return result
    return ChatResult(response, metrics)
}
```

#### 2. Retrieving Relevant Memories

For each user message, the agent retrieves relevant memories from long-term storage:

```kotlin
private fun retrieveRelevantMemoriesWithTiming(
    query: String,
    userId: String
): Pair<List<Memory>, Long> {
    val memories = memoryService.retrieveMemories(
        query = query,
        userId = userId,
        distanceThreshold = 0.3f
    ).map { it.memory }

    return Pair(memories, embeddingTimeMs)
}
```

#### 3. Adding Memory Context to Conversation

Retrieved memories are formatted and added to the conversation context:

```kotlin
private fun formatMemoriesAsContext(memories: List<Memory>): String {
    val formattedMemories = memories.joinToString("\n") {
        "- [${it.memoryType}] ${it.content}"
    }

    return """
        I have access to the following relevant memories about this user or topic:

        $formattedMemories

        Use this information to personalize your response, but don't explicitly mention 
        that you're using stored memories unless directly asked about your memory capabilities.
    """.trimIndent()
}
```

#### 4. Extracting and Storing New Memories

After each interaction, the agent extracts potential new memories from the conversation:

```kotlin
private fun extractAndStoreMemoriesWithTiming(
    userMessage: String,
    assistantResponse: String,
    userId: String
): ExtractAndStoreTimings {
    // Create extraction prompt
    val extractionPrompt = """
        Analyze the following conversation and extract potential memories.

        USER MESSAGE:
        $userMessage

        ASSISTANT RESPONSE:
        $assistantResponse

        Extract two types of memories:

        1. EPISODIC MEMORIES: Personal experiences and user-specific preferences
           Examples: "User prefers Delta airlines", "User visited Paris last year"

        2. SEMANTIC MEMORIES: General domain knowledge and facts
           Examples: "Singapore requires passport", "Tokyo has excellent public transit"

        Format your response as a JSON array with objects containing:
        - "type": Either "EPISODIC" or "SEMANTIC"
        - "content": The memory content
    """.trimIndent()

    // Call the LLM to extract memories
    val extractionResponse = chatModel.call(
        Prompt(listOf(SystemMessage(extractionPrompt)))
    )

    // Parse the response and store memories
    // ...

    // Store each extracted memory
    memoryService.storeMemory(
        content = content,
        memoryType = memoryType,
        userId = memoryUserId,
        metadata = "{}"
    )

    return ExtractAndStoreTimings(llmExtractionTimeMs, memoryStorageTimeMs)
}
```

#### 5. Managing Short-Term Memory

The agent manages short-term memory through conversation history:

```kotlin
// Save conversation history to Redis
private fun saveConversationHistoryToRedis(userId: String, history: List<Message>) {
    val redisKey = "$conversationKeyPrefix$userId"

    // Delete existing key if it exists
    jedisPooled.del(redisKey)

    // Serialize each message and add to Redis list
    for (message in history) {
        val serializedMessage = serializeMessage(message)
        jedisPooled.rpush(redisKey, serializedMessage)
    }

    // Set TTL of one hour (3600 seconds)
    jedisPooled.expire(redisKey, 3600)
}

// Load conversation history from Redis
private fun loadConversationHistoryFromRedis(userId: String): List<Message> {
    val redisKey = "$conversationKeyPrefix$userId"

    // Get all messages from Redis list
    val serializedMessages = jedisPooled.lrange(redisKey, 0, -1)

    // Deserialize messages
    return serializedMessages.mapNotNull { deserializeMessage(it) }.toMutableList()
}
```

#### 6. Summarizing Long Conversations

To prevent context windows from getting too large, the agent summarizes long conversations:

```kotlin
private fun summarizeConversation(
    history: MutableList<Message>,
    userId: String
) {
    // Keep the system prompt and the last 4 messages
    val systemPrompt = history.first()
    val recentMessages = history.takeLast(4)

    // Create a summary prompt
    val summaryPrompt = """
        Summarize the key points of this conversation, including:
        1. User preferences and important details
        2. Topics discussed
        3. Any decisions or conclusions reached
    """.trimIndent()

    // Generate summary
    val summaryResponse = chatModel.call(summaryRequest)
    val summary = summaryResponse.result.output.text

    // Replace history with summary and recent messages
    history.clear()
    history.add(systemPrompt)
    history.add(SystemMessage("Conversation summary: $summary"))
    history.addAll(recentMessages)
}
```

This orchestration allows the agent to maintain context across multiple interactions, personalize responses based on user history, and continuously learn from conversations.
