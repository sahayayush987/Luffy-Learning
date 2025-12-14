import streamlit as st
from openai import OpenAI
import json
import re
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import create_openai_tools_agent, AgentExecutor
from langchain_tavily import TavilySearch

load_dotenv()


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.6,
)

tavily_tool = TavilySearch(
    max_results=5,
    search_depth="basic"
)

tools = [tavily_tool]

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are Luffy Learning's Book Recommendation Agent.

Your task:
1. Recommend 3–5 books based on the user's request
2. Give a paragraph for each book you recommend and why you recommend it.
3. For EACH book:
   - CRITICAL: Use the Tavily search tool to find a book cover image for the exact book you recommend.
   - If you cannot find a cover image for a book, DO NOT include that book in your recommendations.
   - Only recommend books where you successfully found a cover image URL.
   - Use the Tavily search tool MULTIPLE TIMES to find a valid buy link:
     * First search: "[book title] [author] buy Amazon"
     * If that doesn't return a valid Amazon link, search: "[book title] [author] buy"
     * If still no results, try variations: "[main title without subtitle] [author] buy" or just "[author] [main title]"
     * Review the search results carefully and select a link that:
       - Is from a reputable retailer (Amazon, Barnes & Noble, Bookshop.org, IndieBound, Target, Walmart, etc.)
       - Contains the book title (partial matches are acceptable - e.g., "The Hating Game" matches "The Hating Game: A Novel")
       - Contains the author name (or at least the last name)
       - Is NOT a 404 error page, "page not found", or broken link
       - Is a direct product page where the book can be purchased
       - ACCEPT partial title matches - if the main title matches, it's fine even if subtitles differ
4. Return your FINAL answer as valid JSON ONLY with this format:
IMPORTANT: Do not recommend books that are not age-appropriate for the user's request.
IMPORTANT: Do not recommend anything R-rated

[
  {{
    "title": "...",
    "author": "...",
    "age_range": "...",
    "reason": "...",
    "cover_image": "...",
    "buy_link": "...",
    "retailer": "..."
  }}
]

Rules:
- Always use Tavily for images and links
- CRITICAL: DO NOT recommend any book without a cover image - if you cannot find an image URL, exclude that book from recommendations
- CRITICAL: The cover_image field must contain a valid image URL (starting with http:// or https://) - never leave it empty or use placeholder text
- CRITICAL: Only use buy links that are VALID and WORKING - verify the link points to an actual product page
- When searching for buy links:
  * Use flexible search queries - try full title first, then main title without subtitle if needed
  * ACCEPT PARTIAL MATCHES: If a link shows "The Hating Game" and you're looking for "The Hating Game: A Novel", that's acceptable
  * The main title words should match, even if subtitles or additional text differ
  * Author name should match (at least last name)
- Prefer Amazon if you find a valid Amazon product page link
- If Amazon doesn't have a valid link, use ANY other reputable retailer (Barnes & Noble, Bookshop.org, IndieBound, Target, etc.) with a valid product page
- NEVER use links that lead to error pages, "page not found", or broken URLs
- The buy_link must be a complete, working URL (starting with http:// or https://)
- Include the retailer name (e.g., "Amazon", "Barnes & Noble", "Bookshop.org") in the "retailer" field
- Do NOT include any text outside JSON
"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_openai_tools_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False
)

# ============================================================
# 🎨 Streamlit UI
# ============================================================
def book_recommendations_tab(client: OpenAI):
    st.header("📚 Luffy Book Recommendations")
    st.markdown("Get personalized book recommendations based on your preferences 🐶")

    user_input = st.text_input(
        "What kind of book do you want?",
        placeholder="e.g. Fun adventure book for an 8-year-old who likes animals",
    )

    if st.button("Find Books") and user_input:
        with st.spinner("🐾 Luffy is searching for books..."):
            try:
                result = agent_executor.invoke(
                    {"input": user_input}
                )

                output_text = result.get("output", "").strip()
                
                # Try to extract JSON from the output (might be in markdown code blocks or have extra text)
                json_match = re.search(r'\[[\s\S]*\]', output_text)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = output_text
                
                # Try to parse the JSON
                try:
                    books = json.loads(json_str)
                except json.JSONDecodeError:
                    # If still not valid JSON, try to find JSON in code blocks
                    code_block_match = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', output_text)
                    if code_block_match:
                        books = json.loads(code_block_match.group(1))
                    else:
                        # Show the raw output for debugging
                        st.error("Could not parse JSON from agent response.")
                        with st.expander("🔍 Debug: Raw Agent Output"):
                            st.code(output_text)
                        return

            except Exception as e:
                st.error(f"Error generating recommendations: {e}")
                with st.expander("🔍 Debug: See details"):
                    st.exception(e)
                return

        st.subheader("📖 Recommended Books")

        for book in books:
            col1, col2 = st.columns([1, 3])

            with col1:
                if book.get("cover_image"):
                    st.image(book["cover_image"], width=160)

            with col2:
                st.markdown(f"### 📘 {book['title']}")
                st.write(f"**Author:** {book['author']}")
                st.write(f"**Age Range:** {book['age_range']}")
                st.write(book["reason"])
                retailer = book.get("retailer", "Buy here")
                st.markdown(f"[🛒 Buy on {retailer}]({book['buy_link']})")

            st.markdown("---")

    else:
        st.info("👆 Enter a book preference and click **Find Books**")
