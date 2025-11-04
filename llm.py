import asyncio

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


class Agent:
    def __init__(self, model_id : str = "qwen2.5:1.5b", temperature: float = 0.1):
        """
        Initialize the Llama31_8B class.

        :param port: The port number of the locally hosted Ollama server.
        """
        self.model_id = model_id
        self.temperature = temperature
        self.model = OllamaLLM(model=self.model_id, temperature=self.temperature)
        self.template = "You are an AI assistant. Answer to the user question being precise and polite:\nUSER QUESTION: {question}"
        self.prompt = ChatPromptTemplate.from_template(self.template)
        self.chain = self.prompt | self.model

    async def chat(self, query: str) -> dict[str, str]:
        """
        Asynchronously send a query to the locally hosted Llama 3.1:8B model and return the response.

        :param query: The input prompt to send to the model.
        :return: The model's response to the input prompt.
        """
        
        result = await self.chain.ainvoke({"question": query})
        return {"result": result}
        
    def test(self):
        """
        Test the Llama31_8B model with a sample query.
        """
        query = "What is the capital of France?"
        response = asyncio.run(self.chat(query))
        print(f"Response: {response['result']}")

def create_agent() -> Agent:
    return Agent()
        
