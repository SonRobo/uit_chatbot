"""
The defined prompt template for loader to process raw text from URLs, PDF, Excels, etc.
"""

URL_SPLITER_PROMPT = """
Given a markdown text. Your task is to split text into subsession for readability.
Each session provide group of relevant information.
Split as much subsession as possible.  
Respons full content of each session.
Your response must be NOT contain ```json```
The response's structure: {'sessions': [{'title': title 1, 'content': content 1},
                                        {'title': title 2, 'content': content 2}
                                        ]}
Trả lời bằng tiếng việt.
"""
