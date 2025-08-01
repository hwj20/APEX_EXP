from transformers import BlipForQuestionAnswering, BlipProcessor
from PIL import Image
import base64
import re
from experiments.physical_question_expt.utils.llm_router import *

import requests
import os

from openai import OpenAI



def strip_markdown(text: str) -> str:
    text = re.sub(r"```", "", text)
    text = re.sub("json", "", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

class LLM_Agent:
    def __init__(self, model="gpt-4o"):
        self.model = model

    # APEX
    def decide_move_APEX(self, state, APEX_results):
        prompt = f"""
        You are playing Tetris. Your goal is to maximize the score by:
        - Clearing as many lines as possible.
        - Keeping the board as flat as possible.
        - Avoiding unnecessary stacking.

        Here is the current board state(0-blank,,1-current piece, 2-landed piece):
        {state}
        
        Here are physical engine analysis:{APEX_results}

        Available moves:
        - "left": Move the piece left by one column.
        - "right": Move the piece right by one column.
        - "rotate": Rotate the piece 90 degrees clockwise.
        - "down": Instantly drop the piece to the lowest possible position.(max times = 1)
        
        Decide the best move sequence in JSON format as a list of actions. Each action should include the move and how many times to perform it.

        Example:
        [
          {{"move": "left", "times": 2}},
          {{"move": "rotate", "times": 1}},
          {{"move": "down", "times": 1}}
        ]

        Allowed moves are: "left", "right", "rotate", and "down".
        Only return the JSON array without any explanation or markdown. No Markdown
        """

        system_prompt = "You are a Tetris AI agent."
        try:
            messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
            ]
            generated_answer = call_llm(self.model,messages)
            return generated_answer

        except Exception as e:
            return f"API error: {e}"

    # baseline
    def decide_move(self, state,model):
        prompt = f"""
        You are playing Tetris. Your goal is to maximize the score by:
        - Clearing as many lines as possible.
        - Keeping the board as flat as possible.
        - Avoiding unnecessary stacking.

        Here is the current board state(0-blank,,1-current piece, 2-landed piece):
        {state}

        Available moves:
        - "left": Move the piece left by one column.
        - "right": Move the piece right by one column.
        - "rotate": Rotate the piece 90 degrees clockwise.
        - "down": Instantly drop the piece to the lowest possible position.(max times = 1)
        
        Decide the best move sequence in JSON format as a list of actions. Each action should include the move and how many times to perform it.

        Example:
        [
          {{"move": "left", "times": 2}},
          {{"move": "rotate", "times": 1}},
          {{"move": "down", "times": 1}}
        ]

        Allowed moves are: "left", "right", "rotate", and "down".
        Only return the JSON array without any explanation or markdown. No Markdown
        """

        system_prompt = "You are a Tetris AI agent."
        try:
            messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
            ]
            generated_answer = call_llm(self.model,messages)
            return generated_answer
        except Exception as e:
            return f"API error: {e}"
    def vlm_decide_move_APEX(self, image_path,APEX_results):
        prompt = f"""
        You are playing Tetris. Your goal is to maximize the score by:
        - Clearing as many lines as possible.
        - Keeping the board as flat as possible.
        - Avoiding unnecessary stacking.
        
        Here are physical engine analysis:{APEX_results}

        Available moves:
        - "left": Move the piece left by one column.
        - "right": Move the piece right by one column.
        - "rotate": Rotate the piece 90 degrees clockwise.
        - "down": Instantly drop the piece to the lowest possible position.(max times = 1)

        Decide the best move sequence in JSON format as a list of actions. Each action should include the move and how many times to perform it.

        Example:
        [
          {{"move": "left", "times": 2}},
          {{"move": "rotate", "times": 1}},
          {{"move": "down", "times": 1}}
        ]

        Allowed moves are: "left", "right", "rotate", and "down". 
        
        Only return the JSON array without any explanation or markdown. No Markdown

        Here is the current board state:
        """

        system_prompt = "You are a Tetris AI agent."

        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

        base64_image = encode_image(image_path)

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        try:
            response = call_llm(self.model,messages)
            return response
        except Exception as e:
            return f"API error: {e}"

    def vlm_decide_move(self, image_path):
        prompt = f"""
        You are playing Tetris. Your goal is to maximize the score by:
        - Clearing as many lines as possible.
        - Keeping the board as flat as possible.
        - Avoiding unnecessary stacking.

        Available moves:
        - "left": Move the piece left by one column.
        - "right": Move the piece right by one column.
        - "rotate": Rotate the piece 90 degrees clockwise.
        - "down": Instantly drop the piece to the lowest possible position.(max times = 1)

        Example:
        [
          {{"move": "left", "times": 2}},
          {{"move": "rotate", "times": 1}},
          {{"move": "down", "times": 1}}
        ]

        Allowed moves are: "left", "right", "rotate", and "down".
        Only return the JSON array without any explanation or markdown. No Markdown

        Here is the current board state:
        """

        system_prompt = "You are a Tetris AI agent."

        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

        base64_image = encode_image(image_path)

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]

        
        try:
            response = call_llm(self.model,messages)
            return response
        except Exception as e:
            return f"API error: {e}"

