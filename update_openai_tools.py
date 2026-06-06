import re

with open('.venv/foreign_price_scraper_ai.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add ddgs import if not there
if "from ddgs import DDGS" not in content:
    content = content.replace("from openai import OpenAI", "from openai import OpenAI\nfrom ddgs import DDGS")

new_func = """
def search_web(query):
    '''
    Tool function for OpenAI to search the web using DuckDuckGo.
    Returns a string of results.
    '''
    log_message(f"   🦆 [OpenAI Tool] Пошук в DuckDuckGo: {query}")
    results_str = ""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            for res in results:
                results_str += f"Title: {res.get('title')}\\nURL: {res.get('href')}\\nSnippet: {res.get('body')}\\n\\n"
    except Exception as e:
        log_message(f"   ⚠️ [OpenAI Tool] Помилка пошуку: {e}")
        return f"Error: {e}"
        
    return results_str if results_str else "No results found."

def get_links_from_openai_with_tools(title, year):
    valid_links = []
    
    # We construct a prompt similar to what the user typed in ChatGPT
    prompt = f"Знайди 3 посилання на маркетплейси з книгою {title} {year}. Обов'язково використовуй інструмент search_web для пошуку товарів на ebay.com, amazon.com та abebooks.com. Після пошуку, поверни прямі посилання на ці товари."
    
    log_message("🤖 Запит до OpenAI (з використанням Function Calling)...")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Пошук в інтернеті. Використовуйте цей інструмент, щоб знайти посилання на товари.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Пошуковий запит (наприклад, 'site:amazon.com Назва Книги')"
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            }
        }
    ]
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant that finds book prices on marketplaces. You must use the search_web tool to find actual, live product URLs. Return only valid direct URLs to the book product pages."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        # First API call
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # If the model decides to use the tool
        if tool_calls:
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "search_web":
                    function_response = search_web(function_args.get("query"))
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    })
            
            # Second API call with the tool results
            log_message("🤖 OpenAI опрацьовує результати пошуку...")
            second_response = client.beta.chat.completions.parse(
                model="gpt-5.4-mini",
                messages=messages,
                response_format=BookLinksResponse
            )
            
            ai_data = second_response.choices[0].message.parsed
            if ai_data and ai_data.links:
                for link in ai_data.links:
                    url = link.url
                    # Add to valid links if it looks like a direct link and not a search page
                    if "amazon.com/s?" not in url and "ebay.com/sch/" not in url and "abebooks.com/servlet/SearchResults" not in url:
                        valid_links.append({"site": link.site, "url": url})
                        
    except Exception as e:
        log_message(f"❌ Помилка роботи з OpenAI: {e}")
        
    log_message(f"✅ OpenAI повернув {len(valid_links)} прямих посилань.")
    for link in valid_links:
        log_message(f"   🔗 {link['site']}: {link['url']}")
        
    return valid_links
"""

# Now replace the old get_links_from_openai with the new logic
# We need to find `class BookLink` and its related stuff up to `return valid_links` inside `get_links_from_openai`
# Wait, let's just replace the body of `get_links_from_openai` entirely by finding it.
start_idx = content.find("def get_links_from_openai(title, year):")
if start_idx != -1:
    end_idx = content.find("def process_product_page(", start_idx)
    if end_idx != -1:
        content = content[:start_idx] + new_func + content[end_idx:]

with open('.venv/foreign_price_scraper_ai.py', 'w', encoding='utf-8') as f:
    f.write(content)
