"""Unit tests for the DynamoDB progress service using moto."""

import os

import boto3
import pytest
from moto import mock_aws

from app.models.domain import ExamDomain

# Override settings before importing the service
os.environ["DYNAMODB_TABLE"] = "test-user-progress"
os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        table = dynamodb.create_table(
            TableName="test-user-progress",
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "domain", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "domain", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table


class TestProgressService:
    @mock_aws
    def test_get_progress_returns_empty_for_new_user(self, dynamodb_table):
        from app.services.progress import get_progress

        result = get_progress("new-user-id")
        assert result == []

    @mock_aws
    def test_record_answer_creates_domain_record(self, dynamodb_table):
        from app.services.progress import get_progress, record_answer

        record_answer("user-1", ExamDomain.AI_ML_FUNDAMENTALS, "qid-1", correct=True)
        progress = get_progress("user-1")

        domain_record = next((p for p in progress if p.domain == ExamDomain.AI_ML_FUNDAMENTALS), None)
        assert domain_record is not None
        assert domain_record.correct_count == 1
        assert domain_record.total_count == 1
        assert domain_record.accuracy == 1.0

    @mock_aws
    def test_record_incorrect_answer(self, dynamodb_table):
        from app.services.progress import record_answer

        record_answer("user-1", ExamDomain.FOUNDATION_MODELS, "qid-2", correct=False)
        result = record_answer("user-1", ExamDomain.FOUNDATION_MODELS, "qid-3", correct=True)

        assert result.correct_count == 1
        assert result.total_count == 2
        assert result.accuracy == pytest.approx(0.5, abs=0.01)

    @mock_aws
    def test_summary_includes_all_domains(self, dynamodb_table):
        from app.services.progress import get_summary

        summary = get_summary("user-with-no-history")
        assert len(summary.domains) == len(ExamDomain)

    @mock_aws
    def test_streak_counts_consecutive_correct(self, dynamodb_table):
        from app.services.progress import get_summary, record_answer

        record_answer("user-streak", ExamDomain.AI_ML_FUNDAMENTALS, "q1", correct=True)
        record_answer("user-streak", ExamDomain.FOUNDATION_MODELS, "q2", correct=True)
        record_answer("user-streak", ExamDomain.RESPONSIBLE_AI, "q3", correct=True)

        summary = get_summary("user-streak")
        assert summary.current_streak == 3

    @mock_aws
    def test_streak_resets_on_wrong_answer(self, dynamodb_table):
        from app.services.progress import get_summary, record_answer

        record_answer("user-break", ExamDomain.AI_ML_FUNDAMENTALS, "q1", correct=True)
        record_answer("user-break", ExamDomain.AI_ML_FUNDAMENTALS, "q2", correct=False)
        record_answer("user-break", ExamDomain.AI_ML_FUNDAMENTALS, "q3", correct=True)

        summary = get_summary("user-break")
        assert summary.current_streak == 1
