from enum import Enum


class ExamDomain(str, Enum):
    AI_ML_FUNDAMENTALS = "ai_ml_fundamentals"
    GENERATIVE_AI_FUNDAMENTALS = "generative_ai_fundamentals"
    FOUNDATION_MODELS = "foundation_models"
    RESPONSIBLE_AI = "responsible_ai"
    SECURITY_GOVERNANCE = "security_governance"


DOMAIN_METADATA: dict[ExamDomain, dict] = {
    ExamDomain.AI_ML_FUNDAMENTALS: {
        "label": "Fundamentals of AI and ML",
        "exam_weight": 0.20,
        "topics": [
            "machine learning concepts",
            "supervised learning",
            "unsupervised learning",
            "neural networks",
            "model training",
            "feature engineering",
            "SageMaker",
            "inference",
        ],
    },
    ExamDomain.GENERATIVE_AI_FUNDAMENTALS: {
        "label": "Fundamentals of Generative AI",
        "exam_weight": 0.24,
        "topics": [
            "large language models",
            "foundation models",
            "tokens",
            "embeddings",
            "prompt engineering",
            "fine-tuning",
            "RAG",
            "Amazon Bedrock",
        ],
    },
    ExamDomain.FOUNDATION_MODELS: {
        "label": "Applications of Foundation Models",
        "exam_weight": 0.28,
        "topics": [
            "Amazon Bedrock",
            "model selection",
            "agents",
            "knowledge bases",
            "guardrails",
            "model customisation",
            "inference parameters",
            "use case patterns",
        ],
    },
    ExamDomain.RESPONSIBLE_AI: {
        "label": "Guidelines for Responsible AI",
        "exam_weight": 0.14,
        "topics": [
            "bias",
            "fairness",
            "transparency",
            "explainability",
            "responsible AI",
            "ethical AI",
            "model cards",
            "human oversight",
        ],
    },
    ExamDomain.SECURITY_GOVERNANCE: {
        "label": "Security, Compliance, and Governance for AI",
        "exam_weight": 0.14,
        "topics": [
            "IAM",
            "data privacy",
            "model governance",
            "compliance",
            "encryption",
            "VPC",
            "audit",
            "AI security",
        ],
    },
}
