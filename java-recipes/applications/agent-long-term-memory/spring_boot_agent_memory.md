# Redis Agent Long-Term Memory

Modern AI agents rely on memory to go beyond single-turn responses and behave more like intelligent, adaptive assistants. Memory enables agents to understand user context, retain important facts, recall past interactions, and personalize conversations over time. Without memory, an agent starts each interaction from scratch — forgetting preferences, goals, and history — which limits its usefulness and realism.

In AI systems, memory is typically divided into two types:
- Short-term memory maintains context within a single session or conversation thread. This allows the agent to track recent messages, follow up on prior turns, and provide coherent responses.
- Long-term memory stores information across sessions, including facts (semantic memory) and personal experiences or preferences (episodic memory). This allows the agent to “remember” what it has learned about a user or domain, making interactions feel more consistent and personalized.

This demo implements both memory types using Redis and Spring AI, combining the speed and flexibility of Redis with the semantic capabilities of vector embeddings. With vector similarity search, agents can retrieve relevant memories even if a user’s phrasing is different from how the information was originally stored. You’ll also see features like memory deduplication and filtering — all designed to give AI agents a robust and scalable memory system.

## Learning resources:

- Video: [What is an embedding model?](https://youtu.be/0U1S0WSsPuE)
- Video: [Exact vs Approximate Nearest Neighbors—What's the difference?](https://youtu.be/9NvO-VdjY80)
- Video: [What is semantic search?](https://youtu.be/o3XN4dImESE)
- Video: [What is a vector database?](https://youtu.be/Yhv19le0sBw)

## Repository

The repository for this demo can be found [here](https://github.com/redis-developer/redis-springboot-resources/tree/main/artificial-intelligence/agent-long-term-memory-with-spring-ai)

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
cd redis-springboot-recipes/artificial-intelligence/agent-long-term-memory-with-spring-ai
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

Agents rely on short and long-term memory. Short-term memory is typically the chat history, the list of messages exchanged between the agent and the user or the context the agent is using during its current session.

To implement both of these memories, we're going to rely on the Spring AI Advisors API. Advisors are a way to intercept, modify, and enhance AI-driven interactions.

We are going to create two advisors. The first one, for shot-term memory, is going to rely on the ChatMemory abstraction provided by Spring AI while the second one is going to be implemented from scratch by ourselves.

### Short-term memory

To see how to implement short-term memory (or chat history) with Spring AI, refer to the dedicated recipe: ![Chat History with Spring AI](../agent-short-term-memory/spring_boot_agent_memory.md)

### Long-term memory

Long-term memory is the memory the agent needs to remember across different sessions or interactions. There are two types of long-term memory:

- Episodic: episodic memories are related to past events. Personal experiences and user-specific preferences. E.g. "User went to Paris in 2009 for his honeymoon"
- Semantic: semantic memories are general domain knowledge and facts. E.g. "Americans don't require a visa to travel to Paris"

Different from short-term memory, not all of this memory needs to be accessed at every interaction, and not every information must be remembered in the long term. Because of that, we will rely on semantic search to retrieve long-term memory and LLMs to extract them from current interactions.

The application uses Spring AI's `RedisVectorStore` to store and search vector embeddings of memories.

#### Configuring the Vector Store

```kotlin
@Bean
fun memoryVectorStore(
  embeddingModel: EmbeddingModel,
  jedisPooled: JedisPooled
): RedisVectorStore {
  return RedisVectorStore.builder(jedisPooled, embeddingModel)
    .indexName("longTermMemoryIdx")
    .contentFieldName("content")
    .embeddingFieldName("embedding")
    .metadataFields(
      RedisVectorStore.MetadataField("memoryType", Schema.FieldType.TAG),
      RedisVectorStore.MetadataField("metadata", Schema.FieldType.TEXT),
      RedisVectorStore.MetadataField("userId", Schema.FieldType.TAG),
      RedisVectorStore.MetadataField("createdAt", Schema.FieldType.TEXT)
    )
    .prefix("short-term-memory:")
    .initializeSchema(true)
    .vectorAlgorithm(RedisVectorStore.Algorithm.HSNW)
    .build()
}
```

Let's break this down:

- **Index Name**: `longTermMemoryIdx` - Redis will create an index with this name for searching memories
- **Content Field**: `content` - The raw memory content that will be embedded
- **Embedding Field**: `embedding` - The field that will store the resulting vector embedding
- **Metadata Fields**:
  - `memoryType`: TAG field for filtering by memory type (EPISODIC or SEMANTIC)
  - `metadata`: TEXT field for storing additional context about the memory
  - `userId`: TAG field for filtering by user ID
  - `createdAt`: TEXT field for storing the creation timestamp

##### Storing Memories

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

##### Retrieving Memories

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

#### Advisor for Long-term memory retrieval

We will implement two advisors: one for retrieval and another for recorder. These advisors will be plugged in our `ChatClient` and intercept every interaction with the LLM.

The retrieval advisor runs before your LLM call. It takes the user’s current message, performs a vector similarity search over Redis, and injects the most relevant memories into the system portion of the prompt so the model can ground its answer.

```kotlin
@Component
class LongTermMemoryRetrievalAdvisor(
  private val memoryService: MemoryService,
) : CallAdvisor, Ordered {

  companion object {
    const val USER_ID = "ltm_user_id"   // pass per-call
    const val TOP_K = "ltm_top_k"       // pass per-call (default 5)
  }

  override fun getOrder() = Ordered.HIGHEST_PRECEDENCE + 40
  override fun getName() = "LongTermMemoryRetrievalAdvisor"

  override fun adviseCall(req: ChatClientRequest, chain: CallAdvisorChain): ChatClientResponse {
    val userId = (req.context()[USER_ID] as? String) ?: "system"
    val k = (req.context()[TOP_K] as? Int) ?: 5

    val query = req.prompt().userMessage.text
    val memories = memoryService.retrieveRelevantMemories(query, userId = userId)
      .take(k)

    val memoryBlock = buildString {
      appendLine("Use the MEMORY below if relevant. Keep answers factual and concise.")
      appendLine("----- MEMORY -----")
      memories.forEachIndexed { i, m -> appendLine("${i+1}. ${m.memory.content}") }
      appendLine("------------------")
    }

    val enrichedPrompt = req.prompt().augmentSystemMessage { sys ->
      val existing = sys.text
      sys.mutate()
        .text(
          buildString {
            appendLine(memoryBlock)
            if (existing.isNotBlank()) {
              appendLine()
              append(existing)
            }
          }
        ).build()
    }

    val enrichedReq = req.mutate()
      .prompt(enrichedPrompt)
      .build()

    return chain.nextCall(enrichedReq)
  }
}
```

#### Advisor for Long-term memory recording

The recorder advisor runs after the assistant responds. It looks at the last user message and the assistant’s reply, asks the model to extract atomic, useful facts (episodic or semantic), deduplicates them, and stores them in Redis.

```kotlin
@Component
class LongTermMemoryRecorderAdvisor(
  private val memoryService: MemoryService,
  private val chatModel: ChatModel
) : CallAdvisor, Ordered {

  data class MemoryCandidate(val content: String, val type: MemoryType, val userId: String?)
  data class ExtractionResult(val memories: List<MemoryCandidate> = emptyList())

  private val extractorConverter = BeanOutputConverter(ExtractionResult::class.java)

  override fun getOrder(): Int = Ordered.HIGHEST_PRECEDENCE + 60
  override fun getName(): String = "LongTermMemoryRecorderAdvisor"

  override fun adviseCall(req: ChatClientRequest, chain: CallAdvisorChain): ChatClientResponse {
    // 1) Proceed with the normal call (other advisors may have enriched the prompt)
    val res = chain.nextCall(req)

    // 2) Build extraction prompt (user + assistant text of *this* turn)
    val userText = req.prompt().userMessage.text
    val assistantText = res.chatResponse()?.result?.output?.text

    // 3) Ask the model to extract long-term memories as structured JSON
    val schemaHint = extractorConverter.jsonSchema // JSON schema string for the POJO
    val extractSystem = """
            You extract LONG-TERM MEMORIES from a dialogue turn.

            A memory is either:

            1. EPISODIC MEMORIES: Personal experiences and user-specific preferences
               Examples: "User prefers Delta airlines", "User visited Paris last year"

            2. SEMANTIC MEMORIES: General domain knowledge and facts
               Examples: "Singapore requires passport", "Tokyo has excellent public transit"

            Only extract clear, factual information. Do not make assumptions or infer information that isn't explicitly stated.
            If no memories can be extracted, return an empty array.
            
            The instance must conform to this JSON Schema (for validation, do not output it):
              $schemaHint

            Do not include code fences, schema, or properties. Output a single-line JSON object.
        """.trimIndent()

    val extractUser = """
            USER SAID:
            $userText

            ASSISTANT REPLIED:
            $assistantText

            Extract up to 5 memories with correct type; set userId if present/known.
        """.trimIndent()

    val options: ChatOptions = OpenAiChatOptions.builder()
      .responseFormat(ResponseFormat.builder().type(ResponseFormat.Type.JSON_OBJECT).build())
      .build()

    val extraction = chatModel.call(
      Prompt(
        listOf(
          UserMessage(extractUser),
          SystemMessage(extractSystem)
        ),
        options
      ),
    )

    val parsed = extractorConverter.convert(extraction.result.output.text ?: "")
      ?: ExtractionResult()

    // 4) Persist memories (MemoryService handles dedupe/thresholding)
    val userId = (req.context["ltm_user_id"] as? String) // optional per-call param
    parsed.memories.forEach { m ->
      val owner = m.userId ?: userId
      memoryService.storeMemory(
        content = m.content,
        memoryType = m.type,
        userId = owner
      )
    }

    return res
  }
}
```

#### Plugging advisors in `ChatClient`

In our `ChatConfig` class, we will configure our `ChatClient` as:

```kotlin
    @Bean
    fun chatClient(
        chatModel: ChatModel,
        chatMemory: ChatMemory,
        longTermRecorder: LongTermMemoryRecorderAdvisor,
        longTermMemoryRetrieval: LongTermMemoryRetrievalAdvisor
    ): ChatClient {
        return ChatClient.builder(chatModel)
            .defaultAdvisors(
                MessageChatMemoryAdvisor.builder(chatMemory).build(),
                longTermRecorder,
                longTermMemoryRetrieval
            ).build()
    }
```


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

Since the advisors have been plugged in the `ChatClient` itself, we don't need to worry about managing memory ourselves when interacting with the LLM. The only thing we need to make sure is that with every interaction we send the expected parameters, namely the session or user ID, so that the advisors know which history to look at.

```kotlin
    fun sendMessage(
        message: String,
        userId: String,
    ): ChatResult {
        // Use userId as the key for conversation history and long-term memory
        log.info("Processing message from user $userId: $message")
        val response = chatClient
            .prompt(
                Prompt(
                    travelAgentSystemPrompt,
                    UserMessage(message)
                )
            )
            .advisors { it
                .param(ChatMemory.CONVERSATION_ID, userId)
                .param("ltm_user_id", userId)
            }
            .call()

        return ChatResult(
            response = response.chatResponse()!!
        )
    }
```

This orchestration allows the agent to maintain context across multiple interactions, personalize responses based on user history, and continuously learn from conversations.
