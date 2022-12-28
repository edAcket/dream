import logging
import requests
import sentry_sdk
from os import getenv
from typing import Any
import json
from pathlib import Path
from flask import Flask, request, jsonify
import re

import common.dff.integration.response as int_rsp
import common.dff.integration.context as int_ctx
from df_engine.core import Context, Actor
from common.constants import CAN_NOT_CONTINUE

sentry_sdk.init(getenv("SENTRY_DSN"))
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
MODEL_SERVICE_URL = getenv("MODEL_SERVICE_URL")
assert MODEL_SERVICE_URL

# ранжирование делаем на этапе аннотации? когда мы их ранжируем???


def compose_data_for_model(ctx, actor):
    text_prompt = []
    human_uttrs = int_ctx.get_human_utterances(ctx, actor)
    bot_uttrs = int_ctx.get_bot_utterances(ctx, actor)
    if len(human_uttrs) > 1:
        text_prompt.append(f'Human: {human_uttrs[-2]["text"]}')
    if len(bot_uttrs) > 0:
        text_prompt.append(f'AI: {bot_uttrs[-1]["text"]}')
    if len(human_uttrs) > 0:
        logger.info(f"utts: {human_uttrs[-1]}")
        text_prompt.append(f'Human: {human_uttrs[-1]["text"]}')
        prompts = (
            human_uttrs[-1]
            .get("annotations", {})
            .get("prompt_selector", {})
            .get("prompt", "")
        )
        if prompts:
            prompt = prompts[0]
            text_prompt.insert(0, prompt)
        logger.info(f"prompt: {text_prompt}")
    if text_prompt:
        text_prompt = [re.sub(r"\s(?=[\.,:;])", "", x) for x in text_prompt]  # костыль
    return text_prompt


def generative_response(ctx: Context, actor: Actor, *args, **kwargs) -> Any:
    curr_responses, curr_confidences, curr_human_attrs, curr_bot_attrs, curr_attrs = (
        [],
        [],
        [],
        [],
        [],
    )

    def gathering_responses(reply, confidence, human_attr, bot_attr, attr):
        nonlocal curr_responses, curr_confidences, curr_human_attrs, curr_bot_attrs, curr_attrs
        if reply and confidence:
            curr_responses += [reply]
            curr_confidences += [confidence]
            curr_human_attrs += [human_attr]
            curr_bot_attrs += [bot_attr]
            curr_attrs += [attr]

    request_data = compose_data_for_model(ctx, actor)
    logger.info(f"request_data: {request_data}")
    if len(request_data) > 0:
        response = requests.post(
            MODEL_SERVICE_URL, json={"dialog_context": [request_data]}, timeout=20
        )
        hypotheses = response.json()
    else:
        hypotheses = []
    logger.info(f"hyps: {hypotheses}")
    if hypotheses:
        for hyp in hypotheses:
            if hyp[0][-1] not in [".", "?", "!"]:
                hyp += "."
            gathering_responses(
                hyp[0], 0.99, {}, {}, {"can_continue": CAN_NOT_CONTINUE}
            )

    if len(curr_responses) == 0:
        return ""
    return int_rsp.multi_response(
        replies=curr_responses,
        confidences=curr_confidences,
        human_attr=curr_human_attrs,
        bot_attr=curr_bot_attrs,
        hype_attr=curr_attrs,
    )(ctx, actor, *args, **kwargs)
