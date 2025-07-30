from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
from markdown2 import markdown
from xhtml2pdf import pisa
import os

class AINewsNode:
    def __init__(self,llm):
        """
        Initialize the AINewsNode with API keys for Tavily and GROQ.
        """

        self.tavily = TavilyClient()
        self.llm = llm
        # This is used to capture various steps in the file so that later can be used for steps shown
        self.state = {}
    
    def fetch_news(self, state:dict)-> dict:
        """
        Fetch AI news based on the specified frequency.

        Args:
            state(dict): The state dictionary containing 'frequency'.
        
        Returns:
            dict: Updated state with 'news_data' key containing fetched news.
        """

        frequency = state['messages'][0].content.lower()
        self.state['frequency'] = frequency
        time_range_map = {'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'year': 'y'}
        days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'year': 366}

        response = self.tavily.search(
            query = "Top Artificial Integlligence (AI) technology news in India and globally",
            topic="news",
            time_range=time_range_map[frequency],
            include_answer="advanced",
            max_results=20,
            days = days_map[frequency],
        )

        state['news_data'] = response.get('results',[])
        self.state['news_data'] = state['news_data']
        return state
    
    def summarize_news(self, state:dict)-> dict:
        """
        Summarize the fetched news using an LLM.

        Args:
            state (dict): The state dictionary containing 'news_data'
        
        Returns:
            dict: Updated state with 'summary' key containing the summarized news.
        """

        news_item = self.state['news_data']

        prompt_template = ChatPromptTemplate.from_messages([
            (
                "system", """You are an AI news summarizer. Format AI news into markdown with:

                - Date headers in **DD-MM-YYYY** (IST timezone)
                - One-line summaries per item
                - Link shown as: [source](URL) at the end of each line (do not wrap summary in link)

                Use format strictly like:

                ### 29-07-2025
                - Summary one. [source](https://example.com)
                - Summary two. [source](https://example.com)

                Maintain clear date headers and include only relevant AI-related items.
                Strictly sort the news by keeping latest news above
                """
            ),
            (
                "user", "Articles:\n{articles}"
            )
            ])
        
        articles_str = "\n\n".join([
            f"Content: {item.get('content', '')}\nURL: {item.get('url','')}\nDate: {item.get('published_date','')}"
            for item in news_item
        ])

        response = self.llm.invoke(prompt_template.format(articles=articles_str) )
        state['summary'] = response.content
        self.state['summary'] = state['summary']
        return self.state
    
    # def save_result(self, state):
    #     frequency = self.state['frequency']
    #     summary = self.state['summary']
    #     filename = f"./AINews/{frequency}_summary.md"
    #     with open(filename, 'w') as f:
    #         f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
    #         f.write(summary)
    #     self.state['filename'] = filename
    #     return self.state

    
    def save_result(self,state):
        frequency = self.state['frequency']
        summary = self.state['summary']

        # Ensure output directory exists
        output_dir = "./AINews"
        os.makedirs(output_dir, exist_ok=True)

        # Save as Markdown
        md_filename = os.path.join(output_dir, f"{frequency}_summary.md")
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)

        # Convert markdown to HTML
        html_content = markdown(summary)

        # Save as PDF
        pdf_filename = os.path.join(output_dir, f"{frequency}_summary.pdf")
        with open(pdf_filename, "w+b") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

        if pisa_status.err:
            print("❌ Failed to create PDF")
        else:
            print("✅ PDF successfully created at:", pdf_filename)

        # Save both filenames to state
        self.state['filename_md'] = md_filename
        self.state['filename_pdf'] = pdf_filename

        return self.state