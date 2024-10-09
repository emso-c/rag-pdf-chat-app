# setup imports
import json
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase
from langchain_google_genai import HarmBlockThreshold, HarmCategory
from app.services.rag_service import env_config, app_config, ChatGoogleGenerativeAI

# test imports
import pytest
from deepeval.test_case import LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric
from deepeval import assert_test


class GoogleGeminiAI(DeepEvalBaseLLM):
    """Class to implement Google Gemini AI for DeepEval"""

    def __init__(self, model):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        return chat_model.invoke(prompt).content

    async def a_generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        res = await chat_model.ainvoke(prompt)
        return res.content

    def get_model_name(self):
        return "Google Gemini Model"


# Initilialize safety filters for vertex model
safety_settings = {
    HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    safety_settings=safety_settings,
    api_key=env_config.google_api_key,
)

# initiatialize the  wrapper class
gemini = GoogleGeminiAI(model=llm)


# load test data
with open("tests/mock/test_data.json", "r") as f:
    test_data: dict = json.load(f)


test_cases = []
for suite, data in test_data.items():
    cases: list[dict] = data["cases"]

    for case in cases:
        query, expected_output, retrieval_context = case.values()

        prompt = app_config.default_history[0][1].format(context=retrieval_context)
        actual_output = gemini.generate(prompt)
        test_case = LLMTestCase(
            input=query,
            actual_output=actual_output,
            expected_output=expected_output,
            retrieval_context=retrieval_context,
        )
        test_cases.append(test_case)
    print("added suite", suite, "with", len(cases), "cases")


@pytest.mark.parametrize(
    "test_case",
    test_cases,
)
def test_model(test_case: LLMTestCase):
    metrics = {
        "relevancy": AnswerRelevancyMetric(model=gemini, threshold=0.5),
        "correctness": GEval(
            name="Correctness",
            model=gemini,
            threshold=0.5,
            criteria="Determine whether the actual output is factually correct based on the expected output.",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT,
                LLMTestCaseParams.RETRIEVAL_CONTEXT,
            ],
        ),
        "faithfullness": FaithfulnessMetric(model=gemini, threshold=0.5),
    }
    del metrics["correctness"]
    assert_test(test_case, metrics.values())
