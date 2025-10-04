# pip install --upgrade langchain langchain-community langgraph
# pip install duckduckgo-search

from typing import List, Dict
from langgraph.graph import StateGraph, START, END
# from duckduckgo_search import DDGS   # old
from ddgs import DDGS                     # new

# Step 1: Define State
class State(Dict):
    messages: List[Dict[str, str]] 

# Step 2: Initialize StateGraph
graph_builder = StateGraph(State)

# Step 3: Define DuckDuckGo search function
def duckduckgo_search(query: str, num_results: int = 3) -> str:
    """Searches DuckDuckGo and returns a formatted result."""
    try:
        with DDGS() as ddgs:
            results = [
                f"- {r['title']}: {r['body']}\n{r['href']}" 
                for r in ddgs.text(query, max_results=num_results)
            ]
            if not results:
                return "No results found."
            return "\n\n".join(results)
    except Exception as e:
        return f"Search error: {e}"

# Step 4: Define chatbot function (DuckDuckGo-based)
def chatbot(state: State):
    user_message = state["messages"][-1]["content"]
    
    # Call DuckDuckGo search
    print("🔍 Fetching from DuckDuckGo...")
    response = duckduckgo_search(user_message)
    
    state["messages"].append({"role": "assistant", "content": response})
    return {"messages": state["messages"]}

# Step 5: Add nodes and edges
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Step 6: Compile the graph
graph = graph_builder.compile()

# Step 7: Stream updates
def stream_graph_updates(user_input: str):    
    state = {"messages": [{"role": "user", "content": user_input}]}
    for event in graph.stream(state):
        for value in event.values():
            print("Assistant:", value["messages"][-1]["content"])
            print("-" * 50)

# Step 8: Run chatbot in a loop
if __name__ == "__main__":
    print("🦆 DuckDuckGo Chatbot Ready! (type 'exit' to quit)")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            stream_graph_updates(user_input)
        except Exception as e:
            print(f"An error occurred: {e}")
            break
