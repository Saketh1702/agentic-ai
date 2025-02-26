<!-- src/routes/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  
  const messages = writable([]);
  let userInput = '';
  let isLoading = false;
  let messageHistory = [];
  
  async function sendMessage() {
    if (!userInput.trim()) return;
    
    isLoading = true;
    
    // Add user message to the chat
    const userMessage = {
      type: 'user',
      content: userInput,
      timestamp: new Date()
    };
    messages.update(msgs => [...msgs, userMessage]);
    messageHistory.push(userMessage);
    
    try {
      // Detect command type
      let endpoint = '/api/ask';
      if (userInput.toLowerCase().includes('wikipedia')) {
        endpoint = '/api/wikipedia';
      } else if (userInput.toLowerCase().includes('news')) {
        endpoint = '/api/news';
      }
      
      // Send request to backend
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: userInput })
      });
      
      if (!response.ok) {
        throw new Error('Failed to get response');
      }
      
      const data = await response.json();
      
      // Add AI response to the chat
      messages.update(msgs => [...msgs, {
        type: 'ai',
        content: data.response,
        timestamp: new Date()
      }]);
      
    } catch (error) {
      // Add error message to the chat
      messages.update(msgs => [...msgs, {
        type: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      }]);
    } finally {
      isLoading = false;
      userInput = '';
    }
  }
  
  function showHistory() {
    messages.update(msgs => [
      ...msgs, 
      {
        type: 'system',
        content: 'Task History:',
        timestamp: new Date()
      },
      ...messageHistory.map(msg => ({
        type: 'history',
        content: msg.content,
        timestamp: msg.timestamp
      }))
    ]);
  }
  
  function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }
</script>

<svelte:head>
  <title>AI Agent Interface</title>
</svelte:head>

<main>
  <header>
    <h1>AI Agent</h1>
    <p>Ask me anything, or try commands with "wikipedia" or "news"</p>
  </header>
  
  <section class="chat-container">
    {#if $messages.length === 0}
      <div class="welcome-message">
        <h2>Welcome!</h2>
        <p>Try something like:</p>
        <ul>
          <li><strong>wikipedia</strong> artificial intelligence</li>
          <li><strong>news</strong> technology</li>
          <li>Or ask any question</li>
        </ul>
      </div>
    {:else}
      <div class="messages">
        {#each $messages as message}
          <div class="message {message.type}">
            <div class="message-content">
              {#if message.type === 'user'}
                <span class="prefix">You:</span>
              {:else if message.type === 'ai'}
                <span class="prefix">AI:</span>
              {:else if message.type === 'error'}
                <span class="prefix">Error:</span>
              {:else if message.type === 'system' || message.type === 'history'}
                <span class="prefix">System:</span>
              {/if}
              <span>{message.content}</span>
            </div>
            <div class="timestamp">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </section>
  
  <footer>
    <div class="controls">
      <button class="history-btn" on:click={showHistory}>History</button>
    </div>
    <div class="input-container">
      <textarea 
        bind:value={userInput} 
        on:keydown={handleKeydown}
        placeholder="What would you like me to do?"
        disabled={isLoading}
      ></textarea>
      <button 
        on:click={sendMessage} 
        disabled={isLoading || !userInput.trim()}
      >
        {isLoading ? 'Processing...' : 'Send'}
      </button>
    </div>
  </footer>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #f9fafb;
    color: #111827;
  }
  
  main {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 800px;
    margin: 0 auto;
    padding: 0 1rem;
  }
  
  header {
    padding: 1.5rem 0;
    text-align: center;
    border-bottom: 1px solid #e5e7eb;
  }
  
  header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 600;
    color: #4f46e5;
  }
  
  header p {
    margin: 0.5rem 0 0;
    color: #6b7280;
  }
  
  .chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem 0;
  }
  
  .welcome-message {
    text-align: center;
    color: #6b7280;
    padding: 2rem;
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .welcome-message h2 {
    color: #4f46e5;
    margin-bottom: 1rem;
  }
  
  .welcome-message ul {
    text-align: left;
    display: inline-block;
    list-style-type: none;
    padding: 0;
  }
  
  .welcome-message li {
    margin: 0.5rem 0;
    padding: 0.5rem;
    background-color: #f3f4f6;
    border-radius: 0.25rem;
  }
  
  .messages {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .message {
    display: flex;
    flex-direction: column;
    max-width: 80%;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
  }
  
  .message.user {
    align-self: flex-end;
    background-color: #4f46e5;
    color: white;
  }
  
  .message.ai {
    align-self: flex-start;
    background-color: white;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  
  .message.error {
    align-self: center;
    background-color: #fee2e2;
    border: 1px solid #fecaca;
    color: #b91c1c;
  }
  
  .message.system, .message.history {
    align-self: center;
    background-color: #f3f4f6;
    color: #4b5563;
    font-style: italic;
  }
  
  .message-content {
    display: flex;
    gap: 0.5rem;
  }
  
  .prefix {
    font-weight: 600;
  }
  
  .timestamp {
    align-self: flex-end;
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 0.25rem;
  }
  
  .message.ai .timestamp,
  .message.error .timestamp,
  .message.system .timestamp,
  .message.history .timestamp {
    color: #9ca3af;
  }
  
  footer {
    padding: 1rem 0;
    border-top: 1px solid #e5e7eb;
  }
  
  .controls {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 0.5rem;
  }
  
  .history-btn {
    background-color: transparent;
    border: none;
    color: #4f46e5;
    cursor: pointer;
    font-size: 0.875rem;
  }
  
  .input-container {
    display: flex;
    gap: 0.5rem;
  }
  
  textarea {
    flex: 1;
    height: 2.5rem;
    max-height: 8rem;
    padding: 0.5rem 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    resize: none;
    font-family: inherit;
    font-size: 1rem;
  }
  
  button {
    padding: 0 1rem;
    background-color: #4f46e5;
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  button:hover:not(:disabled) {
    background-color: #4338ca;
  }
  
  button:disabled {
    background-color: #a5b4fc;
    cursor: not-allowed;
  }
</style>