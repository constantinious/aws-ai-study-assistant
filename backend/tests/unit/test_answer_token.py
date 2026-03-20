"""Unit tests for signed answer token encode/decode."""

import time

import pytest
from jose import JWTError

from app.services.answer_token import decode_answer_token, encode_answer_token


class TestAnswerToken:
    def test_encode_decode_roundtrip(self):
        qid = "test-question-id-123"
        correct_index = 2
        token = encode_answer_token(qid, correct_index)
        decoded_qid, decoded_index = decode_answer_token(token)
        assert decoded_qid == qid
        assert decoded_index == correct_index

    def test_all_valid_indices(self):
        for idx in range(4):
            token = encode_answer_token("qid", idx)
            _, decoded = decode_answer_token(token)
            assert decoded == idx

    def test_tampered_token_raises(self):
        token = encode_answer_token("qid", 0)
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(JWTError):
            decode_answer_token(tampered)

    def test_different_questions_produce_different_tokens(self):
        token_a = encode_answer_token("question-a", 0)
        token_b = encode_answer_token("question-b", 0)
        assert token_a != token_b
